import requests
import sys
import time
from concurrent.futures import ThreadPoolExecutor

PROXY_FILE = sys.argv[1] if len(sys.argv) > 1 else "proxies.txt"
TEST_URL = "https://api.ipify.org?format=json"
TIMEOUT = 15


def parse(line):
    parts = line.strip().split(":")
    if len(parts) != 4:
        return None
    return parts  # host, port, user, pwd


def check(entry):
    host, port, user, pwd = entry
    results = {}
    for scheme in ("http", "socks5"):
        proxy_url = f"{scheme}://{user}:{pwd}@{host}:{port}"
        proxies = {"http": proxy_url, "https": proxy_url}
        start = time.time()
        try:
            r = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
            ms = round((time.time() - start) * 1000)
            if r.status_code == 200:
                results[scheme] = f"OK ip={r.json()['ip']} {ms}ms"
            else:
                results[scheme] = f"HTTP {r.status_code}"
        except Exception as e:
            results[scheme] = f"FAIL {type(e).__name__}"
    return host, port, results


def main():
    with open(PROXY_FILE, encoding="utf-8") as f:
        entries = [p for p in (parse(l) for l in f if l.strip()) if p]

    print(f"Testing {len(entries)} proxies (HTTP + SOCKS5)...\n")
    with ThreadPoolExecutor(max_workers=10) as ex:
        results = list(ex.map(check, entries))

    working = 0
    for host, port, res in results:
        ok_http = res["http"].startswith("OK")
        ok_socks = res["socks5"].startswith("OK")
        ok = ok_http or ok_socks
        working += ok
        print(f"{'✅' if ok else '❌'} {host}:{port}")
        print(f"     HTTP  : {res['http']}")
        print(f"     SOCKS5: {res['socks5']}")
    print(f"\n{working}/{len(results)} proxies working (HTTP or SOCKS5)")


if __name__ == "__main__":
    main()