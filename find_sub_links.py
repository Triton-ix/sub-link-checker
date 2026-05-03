import subprocess
import sys
import os
import re
import time
import random
import requests
from colorama import init, Fore, Style

def install_packages():
    packages = ['requests', 'colorama']
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages()

init(autoreset=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# لیست ثابت لینک‌های ساب‌اسکریپشن معروف (همانهایی که قبلاً کار می‌کردند)
KNOWN_SUBSCRIPTION_LINKS = [
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Mahdi0024/ProxyCollector/master/sub/proxies.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed",
    "https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/master/collected-proxies/row-url/all.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
    "https://raw.githubusercontent.com/Ashkan-m/v2ray/main/Sub.txt",
    "https://raw.githubusercontent.com/Kwinshadow/TelegramV2rayCollector/main/sublinks/mix.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/liMilCo/v2r/main/all_configs.txt",
    "https://raw.githubusercontent.com/Kolandone/v2raycollector/main/config.txt",
    "https://raw.githubusercontent.com/mehdirzfx/v2ray-sub/main/links.txt",
    "https://raw.githubusercontent.com/miladtahanian/Config-Collector/main/mixed_iran.txt",
    "https://raw.githubusercontent.com/ircfspace/tconfig/main/config.txt",
    "https://raw.githubusercontent.com/coldwater-10/V2Hub3/main/merged",
    "https://raw.githubusercontent.com/coldwater-10/V2Hub4/main/merged",
    "https://raw.githubusercontent.com/coldwater-10/V2Hub5/main/merged",
    "https://raw.githubusercontent.com/Surfboardv2ray/v2ray-worker-sub/master/sub",
    "https://raw.githubusercontent.com/MahanKenway/Freedom-V2Ray/main/configs/mix.txt",
    "https://raw.githubusercontent.com/Delta-Kronecker/V2ray-Config/refs/heads/main/config/all_configs.txt",
]

def color_print(text, color=Fore.WHITE, style=Style.NORMAL):
    print(f"{style}{color}{text}{Style.RESET_ALL}")

def is_link_valid(url):
    """بررسی می‌کند لینک در دسترس است و محتوای آن حاوی کانفیگ است"""
    try:
        resp = requests.get(url, timeout=15, headers=HEADERS)
        if resp.status_code != 200:
            return False
        content = resp.text.strip()
        # بررسی وجود پروتکل‌های معروف
        if any(x in content for x in ['vmess://', 'vless://', 'trojan://', 'ss://']):
            return True
        # یا اینکه شبیه base64 بلند باشد
        if len(content) > 100 and re.match(r'^[A-Za-z0-9+/=\n]+$', content[:500]):
            return True
        return False
    except Exception:
        return False

def main():
    color_print("\n" + "="*60, Fore.CYAN)
    color_print("   V2RAY SUBSCRIPTION LINK VALIDATOR (SIMPLE & RELIABLE)", Fore.YELLOW, Style.BRIGHT)
    color_print("="*60 + "\n", Fore.CYAN)
    
    # لینک‌های موجود قبلی (اگر فایل وجود داشته باشد)
    existing_links = []
    if os.path.exists("pool_address.txt"):
        with open("pool_address.txt", "r", encoding='utf-8') as f:
            existing_links = [line.strip() for line in f if line.strip()]
        color_print(f"[*] Existing links in pool_address.txt: {len(existing_links)}", Fore.YELLOW)
    
    # ترکیب لینک‌های جدید و قدیمی (حذف تکراری)
    all_candidate_links = list(set(KNOWN_SUBSCRIPTION_LINKS + existing_links))
    color_print(f"[*] Total candidate links to validate: {len(all_candidate_links)}", Fore.CYAN)
    
    # تست اعتبار لینک‌ها
    valid_links = []
    for idx, link in enumerate(all_candidate_links, 1):
        color_print(f"[{idx}/{len(all_candidate_links)}] Testing: {link[:70]}...", Fore.CYAN)
        if is_link_valid(link):
            valid_links.append(link)
            color_print(f"    ✅ Valid", Fore.GREEN)
        else:
            color_print(f"    ❌ Invalid or dead", Fore.RED)
        time.sleep(random.uniform(0.2, 0.5))
    
    # ذخیره فقط لینک‌های معتبر در pool_address.txt
    with open("pool_address.txt", "w", encoding='utf-8') as f:
        for link in valid_links:
            f.write(link + "\n")
    
    color_print(f"\n" + "="*60, Fore.CYAN)
    color_print(f"[✓] Validation completed.", Fore.GREEN)
    color_print(f"    Total valid links saved: {len(valid_links)}", Fore.YELLOW)
    if len(valid_links) < len(all_candidate_links):
        color_print(f"    Removed dead links: {len(all_candidate_links) - len(valid_links)}", Fore.RED)
    color_print("="*60, Fore.CYAN)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        color_print(f"[ERROR] {e}", Fore.RED)
        sys.exit(1)
