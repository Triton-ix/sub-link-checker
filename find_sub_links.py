import os
import requests
import json
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # توکن در workflow تأمین می‌شود
HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

def search_github_repos():
    """جستجوی مخازن با اشاره به ایران و آپدیت کمتر از 15 روز"""
    query = "iran v2ray subscription OR v2ray config OR subscribe OR sub.txt"
    # می‌توانیم از زبان‌های مختلف استفاده کنیم
    # برای سادگی، کلمه ایران را به انگلیسی و فارسی جستجو می‌کنیم
    queries = [
        "iran v2ray sub",
        "v2ray config iran",
        "subscription iran v2ray",
        "config v2ray ایران",
        "v2ray sub فارسی"
    ]
    all_repos = []
    for q in queries:
        url = f"https://api.github.com/search/repositories?q={q}&sort=updated&order=desc"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                for repo in items:
                    updated_at = datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
                    if datetime.utcnow() - updated_at <= timedelta(days=15):
                        all_repos.append(repo)
            time.sleep(0.5)  # جلوگیری از محدودیت API
        except:
            continue
    # حذف تکراری بر اساس full_name
    unique = {repo["full_name"]: repo for repo in all_repos}.values()
    return list(unique)

def extract_raw_links_from_repo(repo_full_name):
    """از یک مخزن، فایل‌های متنی که احتمالاً حاوی لینک ساب هستند را پیدا کرده و محتوای raw آن را برگرداند"""
    api_url = f"https://api.github.com/repos/{repo_full_name}/contents"
    raw_links = []
    try:
        resp = requests.get(api_url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return raw_links
        contents = resp.json()
        for item in contents:
            if item["type"] == "file" and item["name"].endswith((".txt", ".sub", ".list", "config")):
                raw_url = item["download_url"]
                if raw_url and "raw.githubusercontent.com" in raw_url:
                    raw_links.append(raw_url)
            elif item["type"] == "dir":
                # می‌توانیم یک سطح عمیق‌تر برویم (اختیاری)
                subdir_url = f"https://api.github.com/repos/{repo_full_name}/contents/{item['name']}"
                try:
                    sub_resp = requests.get(subdir_url, headers=HEADERS, timeout=10)
                    if sub_resp.status_code == 200:
                        for sub_item in sub_resp.json():
                            if sub_item["type"] == "file" and sub_item["name"].endswith((".txt", ".sub", ".list")):
                                raw_url = sub_item["download_url"]
                                if raw_url and "raw.githubusercontent.com" in raw_url:
                                    raw_links.append(raw_url)
                    time.sleep(0.2)
                except:
                    pass
        time.sleep(0.3)
    except:
        pass
    return raw_links

def main():
    print("[*] Searching GitHub for V2Ray subscription links related to Iran...")
    repos = search_github_repos()
    print(f"[*] Found {len(repos)} relevant repositories updated in last 15 days")
    
    all_raw_links = []
    for repo in repos:
        full_name = repo["full_name"]
        print(f"[*] Checking {full_name} ...")
        links = extract_raw_links_from_repo(full_name)
        all_raw_links.extend(links)
        time.sleep(0.5)
    
    # حذف تکراری لینک‌ها
    unique_links = list(set(all_raw_links))
    print(f"[*] Total unique raw subscription links extracted: {len(unique_links)}")
    
    # ذخیره در pool_address.txt
    with open("pool_address.txt", "w", encoding="utf-8") as f:
        for link in unique_links:
            f.write(link + "\n")
    
    print("[✓] pool_address.txt updated successfully.")

if __name__ == "__main__":
    main()
