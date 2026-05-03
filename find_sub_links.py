import subprocess
import sys
import os
import re
import time
import random
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style

# نصب خودکار پکیج‌ها
def install_packages():
    packages = ['requests', 'beautifulsoup4', 'colorama']
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"[!] Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages()

from bs4 import BeautifulSoup
init(autoreset=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# لیست ریپازیتوری‌های ثابت و معروف
KNOWN_REPOS = [
    "mahdibland/V2RayAggregator",
    "barry-far/V2ray-Config",
    "Epodonios/v2ray-configs",
    "MahanKenway/Freedom-V2Ray",
    "liMilCo/v2r",
    "Kolandone/v2raycollector",
    "miladtahanian/Config-Collector",
    "Delta-Kronecker/V2ray-Config",
    "mehdirzfx/v2ray-sub",
    "DrFarhad2/v2ray_configs_pools",
    "ircfspace/tconfig",
    "mahxray/Free-SUB-Link",
    "coldwater-10/V2Hub3",
    "coldwater-10/V2Hub4",
    "coldwater-10/V2Hub5",
    "Surfboardv2ray/v2ray-worker-sub",
    "mheidari98/.proxy",
    "aiboboxx/v2rayfree",
    "Pawdroid/Free-servers",
    "ermaozi01/free_clash",
    "learnhard-cn/free_proxy_ss",
    "freefq/free",
    "NiREvil/vless",
]


def color_print(text, color=Fore.WHITE, style=Style.NORMAL):
    print(f"{style}{color}{text}{Style.RESET_ALL}")

def search_github_via_google():
    """جستجو در گوگل برای پیدا کردن ریپازیتوری‌های ایرانی V2Ray"""
    found_repos = set()
    
    color_print("[*] Searching Google for Iranian V2Ray repositories...", Fore.CYAN)
    
    queries = [
        "site:github.com V2Ray config ایران",
        "site:github.com v2ray subscription ایران",
        "site:github.com v2ray collector ایران",
        "site:github.com V2ray config free ایران",
        "site:github.com v2ray iran telegram",
        "site:github.com v2ray config فارسی",
        "site:github.com v2ray free config ایران",
        "site:github.com v2ray collector for iran"
    ]
    
    for query in queries[:3]:  # محدود کردن به ۳ کوئری برای سرعت
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    match = re.search(r'github\.com/([^/]+/[^/]+)/?', href)
                    if match:
                        repo = match.group(1)
                        found_repos.add(repo)
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            color_print(f"  [!] Google search error: {e}", Fore.RED)
    
    return list(found_repos)

def extract_raw_links_from_readme(repo):
    """استخراج لینک‌های raw از README ریپازیتوری"""
    raw_links = []
    
    # لینک README
    readme_url = f"https://raw.githubusercontent.com/{repo}/HEAD/README.md"
    try:
        resp = requests.get(readme_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            content = resp.text
            
            # الگوهای لینک raw
            patterns = [
                r'(https?://raw\.githubusercontent\.com/[^\s\'"\)<>]+\.txt)',
                r'(https?://raw\.githubusercontent\.com/[^\s\'"\)<>]+/sub[^\s\'"\)<>]*)',
                r'(https?://raw\.githubusercontent\.com/[^\s\'"\)<>]+/config[^\s\'"\)<>]*)',
                r'(https?://raw\.githubusercontent\.com/[^\s\'"\)<>]+/mixed[^\s\'"\)<>]*)',
                r'(https?://raw\.githubusercontent\.com/[^\s\'"\)<>]+/all[^\s\'"\)<>]*)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                raw_links.extend(matches)
    
    except:
        pass
    
    return list(set(raw_links))

def build_known_links():
    """لیست لینک‌های شناخته شده از ریپازیتوری‌های معروف"""
    known_links = []
    
    for repo in KNOWN_REPOS:
        raw_links = extract_raw_links_from_readme(repo)
        known_links.extend(raw_links)
        time.sleep(random.uniform(0.3, 0.7))
    
    # لینک‌های مستقیم معروف
    direct_links = [
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
    
    known_links.extend(direct_links)
    return list(set(known_links))

def check_link_validity(url):
    """بررسی اینکه لینک در دسترس است و محتوای معتبر دارد"""
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        if resp.status_code == 200:
            content = resp.text.strip()
            if 'vmess://' in content or 'vless://' in content or 'trojan://' in content or 'ss://' in content:
                return True
            if len(content) > 50 and re.match(r'^[A-Za-z0-9+/=\n]+$', content[:500]):
                return True
        return False
    except:
        return False

def main():
    color_print("\n" + "=" * 60, Fore.CYAN)
    color_print("      V2RAY SUBSCRIPTION LINK FINDER (POWERFUL VERSION)", Fore.YELLOW, Style.BRIGHT)
    color_print("=" * 60 + "\n", Fore.CYAN)
    
    existing_links = []
    if os.path.exists("pool_address.txt"):
        with open("pool_address.txt", "r", encoding='utf-8') as f:
            existing_links = [line.strip() for line in f if line.strip()]
        color_print(f"[*] Existing links in pool_address.txt: {len(existing_links)}", Fore.YELLOW)
    
    all_found_links = set()
    
    color_print("[1] Building known subscription links from repositories...", Fore.GREEN)
    known_links = build_known_links()
    color_print(f"    Found {len(known_links)} raw links", Fore.CYAN)
    
    color_print("\n[2] Testing and validating links...", Fore.GREEN)
    
    valid_links = []
    for idx, link in enumerate(known_links, 1):
        color_print(f"  [{idx}/{len(known_links)}] Testing: {link[:60]}...", Fore.CYAN)
        if check_link_validity(link):
            valid_links.append(link)
            color_print(f"      ✅ Valid subscription link", Fore.GREEN)
        else:
            color_print(f"      ❌ Invalid or not accessible", Fore.RED)
        time.sleep(random.uniform(0.2, 0.5))
    
    # ترکیب لینک‌های جدید با قدیمی
    all_links = list(set(existing_links + valid_links))
    
    # ذخیره در pool_address.txt
    with open("pool_address.txt", "w", encoding='utf-8') as f:
        for link in all_links:
            f.write(link + "\n")
    
    color_print(f"\n" + "="*60, Fore.CYAN)
    color_print(f"[✓] Process completed!", Fore.GREEN)
    color_print(f"    Total links after update: {len(all_links)}", Fore.YELLOW)
    color_print(f"    New working links added: {len(valid_links)}", Fore.GREEN)
    color_print("="*60, Fore.CYAN)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        color_print(f"[ERROR] {e}", Fore.RED)
        sys.exit(1)
