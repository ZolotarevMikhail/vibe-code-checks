#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# бот «Запись клиентов» v1.5 — исправленная версия (кейс №3).
# Секреты приходят только из окружения (.env), в коде и в логах их нет.
import os
import sys

from dotenv import load_dotenv

REQUIRED_VARS = ["TELEGRAM_TOKEN", "SHOP_API_TOKEN", "GTABLE_ID"]


def load_config():
    """Читает .env рядом с ботом и не печатает значения,
    только факт «есть/нет»."""
    load_dotenv()
    missing = [name for name in REQUIRED_VARS if not os.environ.get(name)]
    if missing:
        names = ", ".join(missing)
        print(f"не заданы переменные: {names}. Скопируйте .env.example "
              f"в .env и заполните — инструкция в README.")
        sys.exit(2)
    return {name: os.environ.get(name) for name in REQUIRED_VARS}


def get_orders(config):
    import requests  # импорт внутри: пока нет сети, бот не валится на старте
    url = "https://shop-source.example/api/v2/orders"
    headers = {"X-Api-Key": config["SHOP_API_TOKEN"]}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.json()


def main():
    config = load_config()
    print(f"конфигурация загружена: {len(config)} ключей, "
          f"значения в лог не печатаю")
    orders = get_orders(config)
    print(f"заказов сегодня: {len(orders)}")


if __name__ == "__main__":
    main()
