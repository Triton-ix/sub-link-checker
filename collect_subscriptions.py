import requests
import json
import re
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
import subprocess

# ======================== تنظیمات اولیه ========================
GITHUB_TOKEN = ""  # اگر توکن دارید، برای افزایش لیمیت وارد کنید
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "V2Ray-Collector/1.0"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

DAYS_THRESHOLD = 15  # فقط لینک‌هایی که حداکثر ۱۵ روز پیش آپدیت شده‌اند
# ================================================================

def search_github_repos():
    """جستجوی مخازن مرتبط با V2Ray در ایران"""
    # ترکیب کلمات کلیدی به زبان فارسی و انگلیسی
    queries = [
        'v2ray config iran language:farsi',
        'v2ray subscription iran language:english',
        'کانفیگ v2ray ایران',
        'v2ray free iran',
        'v2ray for iran'
    ]
    
    all_repos = []
    
    for query in queries:
        url = f"https://api.github.com/search/repositories?q={query}&sort=updated&order=desc&per_page=30"
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                data = response.json()
                repos = data.get('items', [])
                print(f"[+] جستجو '{query}': {len(repos)} مخزن پیدا شد")
                all_repos.extend(repos)
            else:
                print(f"[-] خطا در جستجو: {response.status_code}")
        except Exception as e:
            print(f"[-] خطا: {e}")
        time.sleep(1)  # احترام به محدودیت API
    
    # حذف مخازن تکراری بر اساس URL
    unique_repos = {}
    for repo in all_repos:
        repo_url = repo.get('html_url')
        if repo_url not in unique_repos:
            unique_repos[repo_url] = repo
    
    return list(unique_repos.values())

def filter_by_last_update(repo):
    """بررسی آخرین بروزرسانی مخزن (کمتر از ۱۵ روز)"""
    try:
        last_update_str = repo.get('updated_at', '')
        if not last_update_str:
            return False
        last_update = datetime.strptime(last_update_str, '%Y-%m-%dT%H:%M:%SZ')
        days_ago = (datetime.utcnow() - last_update).days
        return days_ago <= DAYS_THRESHOLD
    except:
        return False

def extract_subscription_links_from_repo(repo):
    """استخراج لینک‌های سابسکریپشن از فایل README یک مخزن"""
    repo_name = repo.get('full_name')
    repo_url = repo.get('html_url')
    subscription_links = []
    
    # تلاش برای دریافت README به زبان فارسی و انگلیسی
    readme_urls = [
        f"https://raw.githubusercontent.com/{repo_name}/main/README.md",
        f"https://raw.githubusercontent.com/{repo_name}/main/README.fa.md",
        f"https://raw.githubusercontent.com/{repo_name}/main/README_fa.md",
        f"https://raw.githubusercontent.com/{repo_name}/main/README.en.md"
    ]
    
    for readme_url in readme_urls:
        try:
            response = requests.get(readme_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                # الگوی لینک‌های خام GitHub
                pattern = r'https?://raw\.githubusercontent\.com/[^\s<>"\'\)]+\.(txt|conf|json|list|config)'
                links = re.findall(pattern, content, re.IGNORECASE)
                
                # تطابق کامل URL‌ها
                full_links = re.findall(r'https?://raw\.githubusercontent\.com/[^\s<>"\'\)]+', content)
                
                for link in full_links:
                    if link not in subscription_links:
                        subscription_links.append(link)
        except:
            continue
    
    return subscription_links

def find_subscription_files_in_repo(repo):
    """پیدا کردن فایل‌های سابسکریپشن در ساختار مخزن"""
    repo_name = repo.get('full_name')
    subscription_links = []
    
    # تلاش برای دریافت لیست فایل‌ها از API
    contents_url = f"https://api.github.com/repos/{repo_name}/contents"
    try:
        response = requests.get(contents_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            contents = response.json()
            for item in contents:
                if item.get('type') == 'file':
                    file_name = item.get('name', '').lower()
                    file_path = item.get('path', '')
                    # بررسی فرمت‌های متداول فایل‌های سابسکریپشن
                    if any(ext in file_name for ext in ['sub', 'config', 'subscription', 'v2ray', 'mix', 'all']):
                        download_url = item.get('download_url')
                        if download_url and download_url.startswith('https://raw.githubusercontent.com'):
                            subscription_links.append(download_url)
    except:
        pass
    
    return subscription_links

def check_link_updates(link):
    """بررسی آخرین بروزرسانی یک فایل لینک (بر اساس تاریخ آخرین commit)"""
    try:
        # استخراج اطلاعات مخزن از لینک
        parts = link.replace('https://raw.githubusercontent.com/', '').split('/')
        if len(parts) >= 4:
            owner = parts[0]
            repo = parts[1]
            branch = parts[2]
            file_path = '/'.join(parts[3:])
            
            commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={file_path}&per_page=1"
            response = requests.get(commits_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                commits = response.json()
                if commits and len(commits) > 0:
                    last_commit_date = commits[0].get('commit', {}).get('committer', {}).get('date', '')
                    if last_commit_date:
                        last_update = datetime.strptime(last_commit_date, '%Y-%m-%dT%H:%M:%SZ')
                        days_ago = (datetime.utcnow() - last_update).days
                        return days_ago <= DAYS_THRESHOLD
    except:
        pass
    return False

def is_relevant_repo(repo):
    """بررسی مرتبط بودن مخزن با ایران (بر اساس README و توضیحات)"""
    # کلمات کلیدی مرتبط با ایران
    iran_keywords = ['iran', 'ایران', 'فارسی', 'persian', 'ٱيران', '🇮🇷', 'for iran', 'iranian', 'ج.ا.ا', 'جمهوری اسلامی']
    
    # بررسی توضیحات مخزن
    description = repo.get('description', '').lower()
    if description:
        for keyword in iran_keywords:
            if keyword.lower() in description:
                return True
    
    # بررسی موضوعات (topics) مخزن
    topics = repo.get('topics', [])
    for topic in topics:
        topic_lower = topic.lower()
        for keyword in iran_keywords:
            if keyword.lower() in topic_lower:
                return True
    
    return False

def load_existing_links():
    """بارگذاری لینک‌های موجود از فایل pool_address.txt"""
    try:
        with open('pool_address.txt', 'r', encoding='utf-8') as f:
            return set([line.strip() for line in f if line.strip()])
    except:
        return set()

def save_links_to_file(links):
    """ذخیره لینک‌ها در فایل pool_address.txt"""
    with open('pool_address.txt', 'w', encoding='utf-8') as f:
        for link in sorted(links):
            f.write(link + '\n')

def main():
    print("=" * 60)
    print("V2RAY SUBSCRIPTION COLLECTOR - جستجوی خودکار لینک‌های جدید")
    print("=" * 60)
    print(f"[*] جستجوی لینک‌های سابسکریپشن V2Ray مرتبط با ایران...")
    print(f"[*] محدودیت بروزرسانی: حداکثر {DAYS_THRESHOLD} روز")
    print()
    
    # جستجوی مخازن مرتبط
    repos = search_github_repos()
    print(f"\n[*] {len(repos)} مخزن منحصر‌به‌فرد پیدا شد")
    
    # فیلتر مخازن بر اساس مرتبط بودن با ایران و آخرین بروزرسانی
    relevant_repos = []
    for repo in repos:
        if is_relevant_repo(repo) and filter_by_last_update(repo):
            relevant_repos.append(repo)
    
    print(f"[*] {len(relevant_repos)} مخزن مرتبط با ایران و بروزرسانی شده در {DAYS_THRESHOLD} روز اخیر")
    
    existing_links = load_existing_links()
    print(f"[*] لینک‌های موجود در pool_address.txt: {len(existing_links)}")
    
    new_links = set()
    
    # استخراج لینک‌ها از مخازن مرتبط
    for i, repo in enumerate(relevant_repos, 1):
        repo_name = repo.get('full_name')
        print(f"\n[{i}/{len(relevant_repos)}] بررسی مخزن: {repo_name}")
        
        # استخراج لینک از README
        readme_links = extract_subscription_links_from_repo(repo)
        print(f"    - {len(readme_links)} لینک از README استخراج شد")
        
        # استخراج لینک از ساختار فایل‌ها
        file_links = find_subscription_files_in_repo(repo)
        print(f"    - {len(file_links)} فایل سابسکریپشن در ساختار مخزن پیدا شد")
        
        # ترکیب لینک‌ها
        all_found_links = set(readme_links + file_links)
        
        for link in all_found_links:
            if link not in existing_links and link not in new_links:
                # بررسی آخرین بروزرسانی فایل
                if check_link_updates(link):
                    new_links.add(link)
                    print(f"    ✓ لینک جدید و بروز اضافه شد: {link[:80]}...")
                else:
                    print(f"    - لینک قدیمی‌تر از {DAYS_THRESHOLD} روز: {link[:60]}...")
        
        # جلوگیری از ارسال درخواست زیاد
        time.sleep(1)
    
    # به‌روزرسانی فایل در صورت وجود لینک جدید
    if new_links:
        all_links = existing_links.union(new_links)
        save_links_to_file(all_links)
        print(f"\n[✓] {len(new_links)} لینک جدید پیدا شد و به pool_address.txt اضافه شد")
        print(f"[✓] تعداد کل لینک‌ها: {len(all_links)}")
    else:
        print(f"\n[✓] لینک جدیدی پیدا نشد. فایل pool_address.txt تغییری نکرد")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
