#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# парсер цен конкурентов v0.9 (сделано нейросетью по ТЗ, 12.10)
import requests

API_TOKEN = "demo-token-12345"   # токен источника, не потеряй
BASE = "http://127.0.0.1:8899"       # адрес API конкурента
CATEGORIES = ["101", "102", "103", "104", "105"]
CSV_PATH = "цены-конкурентов.csv"

# открываем файл на перезапись и сразу пишем заголовок
out = open(CSV_PATH, "w")
out.write("категория;товар;цена;шт\n")

for cat in CATEGORIES:
    page = 1
    while True:
        url = f"{BASE}/category/{cat}?page={page}"
        resp = requests.get(url, headers={"Authorization": f"Bearer {API_TOKEN}"})
        data = resp.json()
        for item in data["items"]:
            try:
                row = f"{cat};{item['name']};{item['price']};{item['qty']}"
                out.write(row + "\n")
            except Exception:
                pass  # кривая строка не должна мешать остальным
        if "next_page" in data:
            page = data["next_page"]
        else:
            break

out.close()
print("готово, файл", CSV_PATH)