#!/usr/bin/env python3
"""Check a list of proxies in host:port:user:pass format (Webshare style).

Usage:
    python check_proxies.py "Webshare 10 proxies(17).txt"

Needs only the Python standard library.
"""
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

TEST_URLS = {
    "HTTP": "http://api.ipify.org?format=json",
    "HTTPS": "https://api.ipify.org?format=json",
}
TIMEOUT = 15


def parse(line):
    parts = line.strip().split(":")
    if len(parts) != 4:
        return None
    host, port, user, pwd = parts
    return host, port, user, pwd


def fetch(url, proxy_url):
    handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
    opener = urllib.request.build_opener(handler)
    start = time.time()
    with opener.open(url, timeout=TIMEOUT) as resp:
        body = resp.read().decode()
    return json.loads(body)["ip"], round((time.time() - start) * 1000)


def check(entry):
    host, port, user, pwd = entry
    proxy_url = f"http://{user}:{pwd}@{host}:{port}"
    result = {"proxy": f"{host}:{port}"}
    for label, url in TEST_URLS.items():
        try:
            ip, ms = fetch(url, proxy_url)
            result[label] = f"OK  ip={ip}  {ms}ms"
        except Exception as e:
            result[label] = f"FAIL ({type(e).__name__}: {e})"
    return result


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python check_proxies.py proxies.txt")
    with open(sys.argv[1], encoding="utf-8") as f:
        entries = [p for p in (parse(l) for l in f if l.strip()) if p]
    print(f"Testing {len(entries)} proxies...\n")
    with ThreadPoolExecutor(max_workers=10) as ex:
        results = list(ex.map(check, entries))
    working = 0
    for r in results:
        ok = r["HTTP"].startswith("OK") and r["HTTPS"].startswith("OK")
        working += ok
        print(f"{'✅' if ok else '❌'} {r['proxy']}")
        print(f"     HTTP : {r['HTTP']}")
        print(f"     HTTPS: {r['HTTPS']}")
    print(f"\n{working}/{len(results)} proxies fully working")


if __name__ == "__main__":
    main()
