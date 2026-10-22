import requests
import time
import concurrent.futures

PROXY_FILE = "proxies.txt"
TEST_URL = "https://api.ipify.org?format=json"
TIMEOUT = 10

def parse_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = line.split(":")
    if len(parts) != 4:
        return None
    ip, port, user, pwd = parts
    return ip, port, user, pwd

def check(proxy):
    ip, port, user, pwd = proxy
    proxy_url = f"http://{user}:{pwd}@{ip}:{port}"
    proxies = {"http": proxy_url, "https": proxy_url}
    start = time.time()
    try:
        r = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
        elapsed = time.time() - start
        if r.status_code == 200:
            ip_out = r.json().get("ip")
            return f"✅ {ip}:{port} | {elapsed:.2f}s | IP الظاهر: {ip_out}"
        else:
            return f"⚠️ {ip}:{port} | HTTP {r.status_code} | {elapsed:.2f}s"
    except Exception as e:
        return f"❌ {ip}:{port} | {type(e).__name__}: {e}"

proxies = []
with open(PROXY_FILE, encoding="utf-8") as f:
    for line in f:
        p = parse_line(line)
        if p:
            proxies.append(p)

print(f"اختبار {len(proxies)} بروكسي...\n")
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    for result in ex.map(check, proxies):
        print(result)