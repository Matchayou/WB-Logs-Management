#!/usr/bin/env python3
"""
W&B Logs Management — one-click launcher
Starts the local CORS proxy and opens the app in the default browser.
"""
import subprocess
import sys
import time
import webbrowser
import urllib.request
from pathlib import Path

PROXY_PORT = 8080
APP_FILE   = Path(__file__).parent / "index.html"

def proxy_ready():
    try:
        urllib.request.urlopen(f"http://localhost:{PROXY_PORT}", timeout=1)
    except Exception:
        # Any response (even an error body) means the server is up
        pass
    try:
        urllib.request.urlopen(f"http://localhost:{PROXY_PORT}", timeout=1)
        return True
    except urllib.error.HTTPError:
        return True   # HTTP error = server is listening
    except Exception:
        return False

def main():
    print("🚀 启动 W&B Logs Management…")
    print(f"   代理端口：{PROXY_PORT}")
    print(f"   按 Ctrl+C 停止\n")

    proxy = subprocess.Popen(
        [sys.executable, str(Path(__file__).parent / "proxy.py")],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )

    # Wait for proxy to be ready (up to 5 s)
    for _ in range(50):
        time.sleep(0.1)
        if proxy_ready():
            break
    else:
        print("⚠️  代理启动超时，仍尝试打开应用…")

    url = APP_FILE.as_uri()
    print(f"✅ 正在打开：{url}")
    webbrowser.open(url)

    try:
        proxy.wait()
    except KeyboardInterrupt:
        proxy.terminate()
        print("\n已停止。")

if __name__ == "__main__":
    main()
