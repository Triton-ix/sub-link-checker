import subprocess
import sys
import os
import re
import json
import time
import random
from datetime import datetime, timedelta

def install_packages():
    packages = ['requests', 'colorama']
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"[!] {package} not found. Installing now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages()

import requests
from colorama import init, Fore, Style

init(autoreset=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

GITHUB_SEARCH_URL = "https://api.github.com/search/code"
GITHUB_REPO_URL = "https://api.github.com/repos"

def color_print(text, color=Fore.WHITE, style=Style.NORMAL):
    print(f"{style}{color}{text}{Style.RESET_ALL}")

def search_github_sub_links():
    color_print("\n" + "="*60, Fore.CYAN)
    color_print("      SEARCHING FOR V2RAY SUBSCRIPTION LINKS ON GITHUB", Fore.YELLOW, Style.BRIGHT)
    color_print("="*60 + "\n", Fore.CYAN)
    
    queries = [
        "v2ray subscription link",
        "vmess://",
        "vless://",
        "trojan://",
        "ss://",
        "sub.txt v2ray",
        "config.txt v2ray",
        "clash.yaml v2ray"
    ]
    
    found_raw_links = []
    
    for query in queries:
        page = 1
        while page <= 3:
            params = {'q': query, 'per_page': 30, 'page': page}
            try:
                resp = requests.get(GITHUB_SEARCH_URL, headers=HEADERS, params=params, timeout=10)
                if resp.status_code != 200:
                    color_print(f"  [!] Search failed for '{query}': {resp.status_code}", Fore.RED)
                    break
                data = resp.json()
                items = data.get('items', [])
                if not items:
                    break
                for item in items:
                    repo_full_name = item['repository']['full_name']
                    file_path = item['path']
                    if not (file_path.endswith('.txt') or file_path.endswith('.yaml') or file_path.endswith('.yml') or 'sub' in file_path.lower()):
                        continue
                    raw_url = f"https://raw.githubusercontent.com/{repo_full_name}/HEAD/{file_path}"
                    found_raw_links.append({
                        'url': raw_url,
                        'repo': repo_full_name,
                        'path': file_path,
                        'updated_at': item['repository']['updated_at']
                    })
                page += 1
                time.sleep(random.uniform(0.5, 1.0))
            except Exception as e:
                color_print(f"  [!] Error searching '{query}': {e}", Fore.RED)
                break
    
    color_print(f"[*] Raw links found (before filtering): {len(found_raw_links)}", Fore.YELLOW)
    return found_raw_links

def check_repo_last_commit(repo_full_name):
    api_url = f"{GITHUB_REPO_URL}/{repo_full_name}"
    try:
        resp = requests.get(api_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            pushed_at = data.get('pushed_at')
            if pushed_at:
                last_commit = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                days_ago = (datetime.now().astimezone() - last_commit).days
                return days_ago <= 15, days_ago
        return False, None
    except:
        return False, None

def has_persian_or_iran(repo_full_name, file_path, raw_url):
    # چک README
    readme_url = f"https://raw.githubusercontent.com/{repo_full_name}/HEAD/README.md"
    try:
        resp = requests.get(readme_url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            content = resp.text.lower()
            if re.search(r'[آ-ی]|iran|ایران|تهران|v2ray.*ایران|free.*iran', content):
                return True
    except:
        pass
    # چک خود فایل
    try:
        resp = requests.get(raw_url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            content = resp.text.lower()
            if re.search(r'[آ-ی]|iran|ایران|تهران|v2ray.*ایران|free.*iran', content):
                return True
    except:
        pass
    return False

def validate_subscription_link(url):
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        if resp.status_code == 200:
            text = resp.text.strip()
            if len(text) > 50 and re.match(r'^[A-Za-z0-9+/=]+$', text[:100]):
                return True
            if 'vmess://' in text or 'vless://' in text or 'trojan://' in text or 'ss://' in text:
                return True
        return False
    except:
        return False

def main():
    color_print("Starting GitHub subscription link finder...", Fore.GREEN)
    
    existing_links = []
    if os.path.exists("pool_address.txt"):
        with open("pool_address.txt", "r", encoding='utf-8') as f:
            existing_links = [line.strip() for line in f if line.strip()]
    
    raw_candidates = search_github_sub_links()
    valid_links = []
    
    for idx, cand in enumerate(raw_candidates, 1):
        url = cand['url']
        repo = cand['repo']
        color_print(f"[{idx}/{len(raw_candidates)}] Checking: {repo}", Fore.CYAN)
        
        is_recent, days = check_repo_last_commit(repo)
        if not is_recent:
            color_print(f"    ❌ Last commit >15 days (or unknown)", Fore.RED)
            continue
        
        if not has_persian_or_iran(repo, cand['path'], url):
            color_print(f"    ❌ No Persian/Iran mention", Fore.RED)
            continue
        
        if not validate_subscription_link(url):
            color_print(f"    ❌ Link validation failed", Fore.RED)
            continue
        
        valid_links.append(url)
        color_print(f"    ✅ Valid subscription link found", Fore.GREEN)
        time.sleep(random.uniform(0.3, 0.7))
    
    all_links = list(set(existing_links + valid_links))
    
    with open("pool_address.txt", "w", encoding='utf-8') as f:
        for link in all_links:
            f.write(link + "\n")
    
    color_print(f"\n[✓] Done! Total links after update: {len(all_links)}", Fore.GREEN)
    color_print(f"    New links added: {len(valid_links)}", Fore.YELLOW)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        color_print(f"[ERROR] {e}", Fore.RED)
        sys.exit(1)
