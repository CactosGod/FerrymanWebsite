#!/usr/bin/env python3
"""Ferryman Hat Co. — local site + admin server (Python stdlib only).

    python3 serve.py           # site: http://localhost:8080  admin: /admin.html
    python3 serve.py 9000      # custom port

Serves the static site and adds a tiny API used by admin.html:
    GET  /api/products         -> products.json
    PUT  /api/products         -> replace products.json (JSON array)
    POST /api/upload?name=x.jpg  (raw image bytes) -> {"path": "assets/uploads/..."}

Local mock-up only: there is no authentication. Do not expose this
server to the internet as-is — the production site gets real auth.
"""
import json
import os
import re
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PRODUCTS = os.path.join(ROOT, "products.json")
UPLOAD_DIR = os.path.join(ROOT, "assets", "uploads")
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD = 15 * 1024 * 1024  # 15 MB


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    # ---------- helpers ----------
    def send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0 or length > MAX_UPLOAD:
            return None
        return self.rfile.read(length)

    # ---------- routes ----------
    def do_GET(self):
        if self.path.split("?")[0] == "/api/products":
            try:
                with open(PRODUCTS, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            except FileNotFoundError:
                self.send_json(200, [])
            return
        super().do_GET()

    def do_PUT(self):
        if self.path.split("?")[0] != "/api/products":
            self.send_json(404, {"error": "not found"})
            return
        body = self.read_body()
        if body is None:
            self.send_json(400, {"error": "empty or oversized body"})
            return
        try:
            data = json.loads(body)
            assert isinstance(data, list)
            for item in data:
                assert isinstance(item, dict) and item.get("name")
        except Exception:
            self.send_json(400, {"error": "body must be a JSON array of products"})
            return
        tmp = PRODUCTS + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, PRODUCTS)  # atomic save
        self.send_json(200, {"ok": True, "count": len(data)})

    def do_POST(self):
        path = self.path.split("?")[0]
        if path != "/api/upload":
            self.send_json(404, {"error": "not found"})
            return
        query = self.path.split("?", 1)[1] if "?" in self.path else ""
        m = re.search(r"name=([^&]+)", query)
        raw_name = m.group(1) if m else "upload.jpg"
        # sanitize: keep letters, digits, dot, dash, underscore
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(raw_name))
        ext = os.path.splitext(safe)[1].lower()
        if ext not in ALLOWED_EXT:
            self.send_json(400, {"error": f"extension must be one of {sorted(ALLOWED_EXT)}"})
            return
        body = self.read_body()
        if body is None:
            self.send_json(400, {"error": "empty or oversized body (max 15 MB)"})
            return
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        final = f"{int(time.time())}-{safe}"
        with open(os.path.join(UPLOAD_DIR, final), "wb") as f:
            f.write(body)
        self.send_json(200, {"path": f"assets/uploads/{final}"})

    def log_message(self, fmt, *args):  # quieter log
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Ferryman Hat Co. — site:  http://localhost:{port}")
    print(f"                   admin: http://localhost:{port}/admin.html")
    print("Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
