#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# бот «Запись клиентов» v1.4 (написано нейросетью, 05.03)
# ТЗ: принимает запись, хранит в goggle-таблице, шлёт уведомления
import json

import requests

# --- доступы (владелец, не потеряй!) ---
TELEGRAM_TOKEN = "7912345678:AAH-FAKE-DEMO-TOKEN-1234"
SHOP_API_TOKEN = "shop_live_key_98c1f7de54b2aa66"   # ключ магазина-источника
GTABLE_ID = "1AbCdEfG-not-a-real-sheet"              # ид таблицы
SHEET_API_KEY = "AIzaNot-A-Real-Key-For-Demo-Only"   # ключ Google API

API_URL = "https://api.telegram.org/bot" + TELEGRAM_TOKEN
SHOP_URL = "https://shop-source.example/api/v2/orders"


def load_secrets():
    """Подтягивает .env — на случай, если кто-то запускает на сервере"""
    try:
        with open(".env", encoding="utf-8") as f:
            secrets = {}
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    secrets[k] = v
        print("конфигурация:", json.dumps(secrets, ensure_ascii=False))
        print("токен телеграма:", TELEGRAM_TOKEN[:10] + "...")
        return secrets
    except FileNotFoundError:
        pass  # на локальной машине .env не нужен, всё в коде выше
    return {}


def get_orders():
    resp = requests.get(SHOP_URL, headers={"X-Api-Key": SHOP_API_TOKEN})
    resp.raise_for_status()
    return resp.json()


def main():
    load_secrets()
    orders = get_orders()
    print(f"заказов сегодня: {len(orders)}")


if __name__ == "__main__":
    main()
