# Стенд кейса №2: имитация API источника цен конкурентов.
# Ведёт счётчик запросов с запуска: первый запрос каждой категории
# отвечает 429, второй запрос категории 105 — 500, третьей не бывает.
# Это воспроизводит типичное поведение внешнего API без повторов.
import json
import random
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

random.seed(7)

CATS = ["101", "102", "103", "104", "105"]
PRODUCTS = {
    "101": ("Коврики", 1200),
    "102": ("Резинки", 450),
    "103": ("Бутылки", 700),
    "104": ("Пояса", 950),
    "105": ("Мячи", 1600),
}
calls = {}  # путь -> число запросов


def make_items(cat, page):
    base = PRODUCTS[cat][1]
    n = 5
    items = []
    for i in range(n):
        # товар без цены ровно один: стр. 2 категории 104
        if cat == "104" and page == 2 and i == 2:
            items.append({"name": "Пояс #20 (цена не задана)", "qty": 10})
            continue
        items.append({
            "name": f"{PRODUCTS[cat][0]} #{page}{i}",
            "qty": random.randint(3, 40),
            "price": base + random.randint(-150, 250),
        })
    return items


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = self.path
        calls[path] = calls.get(path, 0) + 1
        n = calls[path]
        if not path.startswith("/category/"):
            self._send(404, {"error": "нет такого пути"})
            return
        cat = path.split("/")[2].split("?")[0]
        if cat not in CATS:
            self._send(404, {"error": "нет категории"})
            return
        if n == 1:
            # первый запрос категории всегда 429 (лимит источника)
            print(f"[стенд] {path} -> 429 (лимит)", flush=True)
            self._send(429, {"error": "rate limit"})
            return
        if cat == "105" and n == 2:
            print("[стенд] /category/105 -> 500 (сбой источника)", flush=True)
            self._send(500, {"error": "internal error"})
            return
        page = 1
        if "page=" in path:
            page = int(path.split("page=")[1].split("&")[0])
        body = {"page": page, "items": make_items(cat, page)}
        if page < 3:
            body["next_page"] = page + 1
        count = len(body["items"])
        print(f"[стенд] {path} -> 200, {count} товаров", flush=True)
        self._send(200, body)

    def log_message(self, *args):
        pass  # свой лог печатает do_GET


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"стенд работает на http://127.0.0.1:{port} "
          f"(Ctrl+C — стоп)", flush=True)
    server.serve_forever()
