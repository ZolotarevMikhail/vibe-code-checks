#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Парсер цен конкурентов — исправленная версия (кейс №2).
# Отличия от вайбкода: повторы с ограничением, таймауты, атомарная
# запись результата, пропуск битых товаров с логом, токен из окружения.
import os
import sys
import time
from datetime import datetime

import requests

BASE = os.environ.get("PARSER_BASE_URL", "http://127.0.0.1:8899")
TOKEN = os.environ.get("PARSER_TOKEN", "")
CATEGORIES = ["101", "102", "103", "104", "105"]
CSV_PATH = os.environ.get("PARSER_CSV", "цены-конкурентов.csv")

REQUEST_TIMEOUT = 20   # сек: без него запрос зависает навсегда
MAX_ATTEMPTS = 5       # повторов на один запрос: конечное число
RETRY_PAUSES = [2, 4, 8, 8]  # паузы между попытками, сек
PAUSE_BETWEEN_REQUESTS = 0.4  # вежливость к источнику


def log(level, message):
    """Печатает событие с меткой времени — иначе ночное падение не найти."""
    print(f"[{datetime.now():%H:%M:%S}] {level}: {message}", flush=True)


def fetch_json(url):
    """Один URL с повторами конечное число раз; при упорном сбое
    возвращает None (категория пропустится, сбор не валится)."""
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            # 429/5xx — вина источника: ждём и пробуем снова
            if resp.status_code >= 400:
                if attempt < MAX_ATTEMPTS:
                    pause = RETRY_PAUSES[attempt - 1]
                    log("warn", f"{url} -> HTTP {resp.status_code}, "
                                f"повтор через {pause} с "
                                f"({attempt}/{MAX_ATTEMPTS})")
                    time.sleep(pause)
                    continue
                log("error", f"{url} -> HTTP {resp.status_code}, "
                             f"попытки кончились ({MAX_ATTEMPTS})")
                return None
            return resp.json()
        except (requests.RequestException, ValueError) as err:
            if attempt < MAX_ATTEMPTS:
                pause = RETRY_PAUSES[attempt - 1]
                log("warn", f"{url} — сеть/JSON сбой: {err}; "
                            f"повтор через {pause} с")
                time.sleep(pause)
            else:
                log("error", f"{url} — сеть/JSON сбой, "
                             f"попытки кончились: {err}")
                return None
    return None


def collect_category(cat):
    """Собирает все страницы одной категории. Возвращает список строк
    CSV и число пропущенных товаров без цены."""
    rows, skipped, page, url_path = [], 0, 1, ""
    while True:
        url_path = f"{BASE}/category/{cat}?page={page}"
        data = fetch_json(url_path)
        if data is None:
            return None, skipped  # категория не собрана — сигнал наверх
        items = data.get("items") or []
        for item in items:
            price = item.get("price")
            if price is None:
                skipped += 1
                log("warn", f"категория {cat}: товар без цены пропущен: "
                            f"{item.get('name', '?')} ({url_path})")
                continue
            rows.append(f"{cat};{item.get('name', '?')};{price};"
                        f"{item.get('qty', '?')}")
        next_page = data.get("next_page")
        if not next_page:
            break
        page = next_page
        time.sleep(PAUSE_BETWEEN_REQUESTS)
    return rows, skipped


def write_csv(all_rows):
    """Пишет результат атомарно: сначала временный файл, потом
    подмена. Так прошлые данные не теряются при сбое в середине."""
    tmp = CSV_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8-sig") as out:
        out.write("категория;товар;цена;шт\n")
        out.write("\n".join(all_rows) + "\n")
    os.replace(tmp, CSV_PATH)
    log("info", f"файл обновлён целиком: {CSV_PATH}, строк с данными: "
                f"{len(all_rows)}")


def main():
    if not TOKEN:
        log("warn", "парсер работает без токена: задайте PARSER_TOKEN "
                    "в окружении (.env), если источник требует ключ")
    all_rows, failed_cats = [], []
    for cat in CATEGORIES:
        rows, skipped = collect_category(cat)
        if rows is None:
            failed_cats.append(cat)
            continue
        all_rows += rows
        log("info", f"категория {cat}: {len(rows)} строк, "
                    f"пропущено без цены: {skipped}")
        time.sleep(PAUSE_BETWEEN_REQUESTS)
    if not all_rows:
        log("error", "ни одна категория не собрана — файл не тронут, "
                     "прошлые данные сохранены")
        return 2
    write_csv(all_rows)
    if failed_cats:
        log("error", f"не собраны категории: {', '.join(failed_cats)} — "
                     f"результат частичный")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
