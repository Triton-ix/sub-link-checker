# ... (بقیه کد مانند قبل، فقط تابع filter_links را اضافه می‌کنیم)

def filter_links_with_conditions(links):
    """فیلتر لینک‌ها بر اساس سه شرط"""
    filtered = []
    for link in links:
        # استخراج repo name از لینک raw
        match = re.search(r'raw\.githubusercontent\.com/([^/]+/[^/]+)/', link)
        if not match:
            continue
        repo = match.group(1)
        
        # شرط ۱: آپدیت کمتر از ۱۵ روز
        api_url = f"https://api.github.com/repos/{repo}"
        try:
            resp = requests.get(api_url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                pushed_at = resp.json().get('pushed_at')
                if pushed_at:
                    last_push = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                    days_ago = (datetime.now().astimezone() - last_push).days
                    if days_ago > 15:
                        continue
            else:
                continue  # اگر API جواب نداد، رد کن
        except:
            continue
        
        # شرط ۲: وجود فارسی/ایران در README
        readme_url = f"https://raw.githubusercontent.com/{repo}/HEAD/README.md"
        try:
            resp = requests.get(readme_url, timeout=8)
            if resp.status_code == 200:
                content = resp.text.lower()
                if not re.search(r'[آ-ی]|iran|ایران|تهران', content):
                    # اگر README نداشت، خود فایل را چک می‌کنیم (اختیاری)
                    file_resp = requests.get(link, timeout=8)
                    if file_resp.status_code == 200:
                        if not re.search(r'[آ-ی]|iran|ایران', file_resp.text.lower()):
                            continue
        except:
            # اگر README در دسترس نبود، لینک را نگه می‌داریم (اختیاری)
            pass
        
        filtered.append(link)
        time.sleep(0.5)
    return filtered
