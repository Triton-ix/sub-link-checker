import os
import sys
import subprocess
import json
import time
import random

def install_dependencies():
    for pkg in ['requests', 'colorama']:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

install_dependencies()

import requests
from colorama import init, Fore, Style
init(autoreset=True)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def process():
    input_file = "pool_address.txt"
    output_file = "cleaned_configs.txt"
    stats_file = "link_stats.json"

    if not os.path.exists(input_file):
        print(Fore.RED + f"[ERROR] {input_file} not found!")
        return

    print(Fore.CYAN + "="*50)
    print(Fore.CYAN + "       V2RAY CONFIG CLEANER PRO")
    print(Fore.CYAN + "="*50 + "\n")

    with open(input_file, 'r', encoding='utf-8') as f:
        raw_urls = [line.strip() for line in f if line.strip()]
    unique_urls = list(set(raw_urls))
    print(Fore.YELLOW + f"[*] Found {len(raw_urls)} URLs, {len(unique_urls)} unique.")

    all_configs = []
    total_raw = 0
    link_status = {}

    for i, url in enumerate(unique_urls, 1):
        print(Fore.BLUE + f"[{i}/{len(unique_urls)}] Fetching {url[:50]}...")
        try:
            r = requests.get(url, timeout=15, headers=HEADERS)
            r.raise_for_status()
            lines = r.text.strip().splitlines()
            cnt = len(lines)
            total_raw += cnt
            all_configs.extend(lines)
            link_status[url] = {"success": True, "configs_found": cnt}
            print(Fore.MAGENTA + f"    -> {cnt} configs")
        except Exception as e:
            link_status[url] = {"success": False, "error": str(e)}
            print(Fore.RED + f"    -> FAILED: {e}")
        time.sleep(random.uniform(0.5, 1.5))

    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(link_status, f, indent=2, ensure_ascii=False)

    print(Fore.CYAN + "\n" + "-"*50)
    print(Fore.YELLOW + f"Total raw configs: {total_raw}")
    unique_configs = list(set(all_configs))
    unique_count = len(unique_configs)
    print(Fore.YELLOW + f"Unique configs: {unique_count}")
    print(Fore.GREEN + f"Duplicates removed: {total_raw - unique_count}")

    with open(output_file, 'w', encoding='utf-8') as f:
        for cfg in unique_configs:
            f.write(cfg + "\n")
    print(Fore.GREEN + f"[SUCCESS] Saved to {output_file}")

if __name__ == "__main__":
    process()
