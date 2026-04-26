#!/usr/bin/env python3
"""
W&B 本地 CORS 代理 — 零外部依赖，只用标准库
用法：python wb_proxy.py
然后在 app 设置里填入「自定义代理 URL」= http://localhost:8080
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request, ssl, json, sys
from pathlib import Path

PORT = 8080
TARGET = "https://api.wandb.ai/graphql"
COMPARE_FILE = Path(__file__).parent / "compare_sessions.json"
SETTINGS_FILE = Path(__file__).parent / "app_settings.json"
ANNOTATIONS_FILE = Path(__file__).parent / "run_annotations.json"

def load_compare_sessions():
    if not COMPARE_FILE.exists():
        return []
    try:
        data = json.loads(COMPARE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def save_compare_sessions(sessions):
    COMPARE_FILE.write_text(
        json.dumps(sessions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def load_app_settings():
    if not SETTINGS_FILE.exists():
        return {}
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def save_app_settings(settings):
    SETTINGS_FILE.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def load_run_annotations():
    if not ANNOTATIONS_FILE.exists():
        return {"version": 1, "runs": {}, "tagLibrary": []}
    try:
        data = json.loads(ANNOTATIONS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"version": 1, "runs": {}, "tagLibrary": []}
        return {
            "version": data.get("version", 1),
            "runs": data.get("runs", {}) if isinstance(data.get("runs", {}), dict) else {},
            "tagLibrary": data.get("tagLibrary", []) if isinstance(data.get("tagLibrary", []), list) else [],
        }
    except Exception:
        return {"version": 1, "runs": {}, "tagLibrary": []}

def save_run_annotations(annotations):
    payload = {
        "version": annotations.get("version", 1),
        "runs": annotations.get("runs", {}),
        "tagLibrary": annotations.get("tagLibrary", []),
    }
    ANNOTATIONS_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        # Echo back the exact Origin (including "null" from file://)
        # MUST NOT use "*" when file:// sends Origin: null
        origin = self.headers.get("Origin") or "*"
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        if self.path == "/compare-sessions":
            try:
                parsed = json.loads(body or b"[]")
                if not isinstance(parsed, list):
                    raise ValueError("compare sessions payload must be a list")
                save_compare_sessions(parsed)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "count": len(parsed)}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
        if self.path == "/app-settings":
            try:
                parsed = json.loads(body or b"{}")
                if not isinstance(parsed, dict):
                    raise ValueError("app settings payload must be an object")
                save_app_settings(parsed)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
        if self.path == "/run-annotations":
            try:
                parsed = json.loads(body or b"{}")
                if not isinstance(parsed, dict):
                    raise ValueError("run annotations payload must be an object")
                save_run_annotations(parsed)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
        try:
            parsed = json.loads(body)
            print(f"  [variables] {json.dumps(parsed.get('variables', {}))}")
        except Exception:
            print(f"  [req body] {body[:300].decode('utf-8', errors='replace')}")
        auth   = self.headers.get("Authorization", "")
        print(f"  [auth] {auth[:20]}... (len={len(auth)})" if auth else "  [auth] MISSING")

        req = urllib.request.Request(
            TARGET,
            data=body,
            headers={
                "Content-Type":  "application/json",
                "Authorization": auth,
                "User-Agent":    "wb-local-proxy/1.0",
            },
            method="POST",
        )
        ctx = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = resp.read()
            print(f"  [W&B resp] {data[:500].decode('utf-8', errors='replace')}")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        if self.path == "/compare-sessions":
            sessions = load_compare_sessions()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps(sessions, ensure_ascii=False).encode("utf-8"))
            return
        if self.path == "/app-settings":
            settings = load_app_settings()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps(settings, ensure_ascii=False).encode("utf-8"))
            return
        if self.path == "/run-annotations":
            annotations = load_run_annotations()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps(annotations, ensure_ascii=False).encode("utf-8"))
            return
        params = parse_qs(urlparse(self.path).query)
        target = params.get('url', [None])[0]
        if not target:
            self.send_response(400); self._cors(); self.end_headers()
            self.wfile.write(b'missing url param'); return
        req = urllib.request.Request(target, method='GET',
            headers={"User-Agent": "wb-local-proxy/1.0"})
        ctx = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self._cors(); self.end_headers(); self.wfile.write(data)
        except urllib.error.HTTPError as e:
            body = e.read()
            self.send_response(e.code); self._cors(); self.end_headers(); self.wfile.write(body)
        except Exception as e:
            self.send_response(500); self._cors(); self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, fmt, *args):
        print(f"  {args[0]}  {args[1]}")

if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"✅ W&B 代理已启动：http://localhost:{PORT}")
    print(f"   把  http://localhost:{PORT}  填入 app 设置的「自定义代理 URL」")
    print(f"   按 Ctrl+C 停止\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
        sys.exit(0)
