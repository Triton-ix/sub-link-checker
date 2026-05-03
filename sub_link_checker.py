import os
import sys
import subprocess
import json
import time
import random

def install_dependencies():
    required_packages = ["requests", "colorama"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"[!] {package} not found. Installing now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_dependencies()

import requests
from colorama import init, Fore, Style

init(autoreset=True)

# User-Agent شبیه مرورگر واقعی
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def process_v2ray_links():
    input_file = "pool_address.txt"
    output_file = "cleaned_configs.txt"
    stats_file = "link_stats.json"

    if not os.path.exists(input_file):
        print(Fore.RED + f"[ERROR] '{input_file}' not found!")
        return

    print(Fore.CYAN + "="*50)
    print(Fore.CYAN + "       V2RAY CONFIG CLEANER PRO")
    print(Fore.CYAN + "="*50 + "\n")

    with open(input_file, 'r', encoding='utf-8') as f:
        raw_urls = [line.strip() for line in f if line.strip()]
    unique_urls = list(set(raw_urls))
    print(Fore.YELLOW + f"[*] Found {len(raw_urls)} URLs in file.")
    print(Fore.GREEN + f"[*] Removed duplicates. Working with {len(unique_urls)} unique subscription links.\n")

    all_configs_raw = []
    total_configs_found = 0
    link_status = {}  # ذخیره وضعیت هر لینک

    for index, url in enumerate(unique_urls, 1):
        print(Fore.BLUE + f"[{index}/{len(unique_urls)}] Fetching: {url[:50]}...")
        try:
            response = requests.get(url, timeout=15, headers=HEADERS)
            response.raise_for_status()
            content = response.text.strip().splitlines()
            current_link_count = len(content)
            total_configs_found += current_link_count
            all_configs_raw.extend(content)
            link_status[url] = {"success": True, "configs_found": current_link_count}
            print(Fore.MAGENTA + f"    -> Found {current_link_count} configs in this link.")
        except Exception as e:
            link_status[url] = {"success": False, "error": str(e)}
            print(Fore.RED + f"    -> [FAILED] Error: {e}")
        # تأخیر تصادفی بین درخواست‌ها برای جلوگیری از مسدود شدن
        time.sleep(random.uniform(0.5, 1.5))

    # ذخیره وضعیت لینک‌ها برای گزارش‌گیری بعدی
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(link_status, f, indent=2, ensure_ascii=False)

    print(Fore.CYAN + "\n" + "-"*50)
    print(Fore.YELLOW + f"Total raw configs collected: {total_configs_found}")

    unique_configs = list(set(all_configs_raw))
    unique_count = len(unique_configs)
    print(Fore.YELLOW + f"Total unique configs found:  {unique_count}")
    print(Fore.GREEN + f"Configs removed (duplicates): {total_configs_found - unique_count}")
    print(Fore.CYAN + "-"*50)

    with open(output_file, 'w', encoding='utf-8') as f:
        for config in unique_configs:
            f.write(config + "\n")
    print(Fore.GREEN + f"\n[SUCCESS] All unique configs saved to: {Fore.WHITE}{output_file}")
    print(Fore.CYAN + "\n" + "="*50)

if __name__ == "__main__":
    process_v2ray_links()
