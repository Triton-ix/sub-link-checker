import os
import json
from datetime import datetime, timezone, timedelta
import subprocess
import sys

# --------------------------- نصب خودکار jdatetime ---------------------------
def install_jdatetime():
    try:
        import jdatetime
        return jdatetime
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'jdatetime'])
        import jdatetime
        return jdatetime

# --------------------------- تبدیل به زمان ایران (هجری شمسی) ---------------------------
def to_jalali(gregorian_dt):
    jdt = install_jdatetime()
    tehran_tz = timezone(timedelta(hours=3, minutes=30))
    local = gregorian_dt.astimezone(tehran_tz)
    return jdt.datetime.fromgregorian(datetime=local).strftime("%Y/%m/%d %H:%M:%S")

# --------------------------- خواندن تعداد خطوط یک فایل ---------------------------
def count_lines(filename):
    if not os.path.exists(filename):
        return 0
    with open(filename, 'r', encoding='utf-8') as f:
        return sum(1 for line in f if line.strip())

# --------------------------- آمار لینک‌ها از link_stats.json ---------------------------
def get_link_stats():
    if not os.path.exists("link_stats.json"):
        return 0, 0, 0
    with open("link_stats.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    total = len(data)
    working = sum(1 for v in data.values() if v.get("success", False))
    return total, working, total - working

# --------------------------- تعداد کل کانفیگ‌های خام (قبل از حذف تکراری) ---------------------------
def get_raw_total():
    if not os.path.exists("link_stats.json"):
        return 0
    with open("link_stats.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    total = 0
    for v in data.values():
        if v.get("success", False):
            total += v.get("configs_found", 0)
    return total

# --------------------------- تعداد لینک‌های یکتا در pool_address.txt ---------------------------
def get_unique_links_count():
    if not os.path.exists("pool_address.txt"):
        return 0
    with open("pool_address.txt", 'r', encoding='utf-8') as f:
        return len(set(line.strip() for line in f if line.strip()))

# --------------------------- تولید README.md با جدول RTL و اعداد واقعی ---------------------------
def generate_readme():
    # ---- دریافت آمار ----
    total_links, working_links, dead_links = get_link_stats()
    raw_total = get_raw_total()
    unique_total = count_lines("cleaned_configs.txt")
    working_total = count_lines("success_config.txt")
    duplicate_total = max(0, raw_total - unique_total)
    dead_configs = max(0, unique_total - working_total)

    # درصدها
    perc_links_working = (working_links / total_links * 100) if total_links else 0
    perc_links_dead = (dead_links / total_links * 100) if total_links else 0
    perc_unique = (unique_total / raw_total * 100) if raw_total else 0
    perc_duplicate = 100 - perc_unique if raw_total else 0
    perc_working = (working_total / unique_total * 100) if unique_total else 0
    perc_dead = 100 - perc_working if unique_total else 0

    # تاریخ شمسی
    now_utc = datetime.now(timezone.utc)
    jalali_str = to_jalali(now_utc)

    # تعداد لینک‌های موجود در pool_address.txt (یکتا)
    pool_link_count = get_unique_links_count()

    # نام مخزن جاری (برای لینک success_config.txt)
    repo_name = os.environ.get('GITHUB_REPOSITORY', 'farzanfarhangi/sub-link-checker')
    success_url = f"https://github.com/{repo_name}/blob/main/success_config.txt"

    # ---- ساخت جدول RTL (با dir="rtl") ----
    # ترتیب ستون‌ها در کد: از چپ به راست (همان ترتیبی که در حالت RTL از راست به چپ دیده می‌شود)
    table = f"""
<div dir="rtl">

| 🟢 کانفیگ تست شده | 🔴 کانفیگ خراب | 🔄 کانفیگ بدون تکرار | 🗑️ کانفیگ تکراری | 📥 کل کانفیگ‌ها | ❌ لینک‌های خراب | ✅ لینک‌های سالم | 🔗 کل لینک‌های SUB |
|-----------------|---------------|---------------------|-----------------|----------------|----------------|----------------|------------------|
| **{working_total}** | **{dead_configs}** | **{unique_total}** | **{duplicate_total}** | **{raw_total}** | **{dead_links}** | **{working_links}** | **{total_links}** |
| {perc_working:.1f}% | {perc_dead:.1f}% | {perc_unique:.1f}% | {perc_duplicate:.1f}% | 100% | {perc_links_dead:.1f}% | {perc_links_working:.1f}% | 100% |

</div>

> درصد ستون‌های **کانفیگ بدون تکرار**، **کانفیگ خراب** و **کانفیگ تست شده** نسبت به کل کانفیگ‌های بدون تکرار محاسبه شده است.
"""

    # ---- محتوای کامل README ----
    readme_content = f"""
## 🤖 تولید شده با **Vibe Coding** – نظارت انسانی + پیشنهادات هوش مصنوعی
این کدها با کمک **GitHub Copilot** و بهینه‌سازی‌های هوش مصنوعی ساخته شده‌اند.

### 📌 نحوه جمع‌آوری خودکار لینک‌های اشتراک
لینک‌های ساب‌اسکریپشن (`pool_address.txt`) هر ۵ روز یکبار با جستجو در ریپازیتوری‌های گیت‌هاب مرتبط با ایران یافت می‌شوند. فقط لینک‌هایی که در ۱۵ روز گذشته بروز شده باشند انتخاب می‌گردند.

---

## 📊 گزارش خودکار وضعیت کانفیگ‌ها  
**📅 آخرین بروزرسانی (زمان ایران):** {jalali_str}

{table}

### 🚀 استفاده آسان
برای استفاده از لیست به‌روز کانفیگ‌های سالم، فقط کافی است لینک زیر را در نرم‌افزارهای V2Ray خود وارد کنید:

👉 **[{success_url}]({success_url})**

این فایل شامل هزاران کانفیگ تست‌شده و فعال است که از بیش از **{pool_link_count}** لینک اشتراک مختلف استخراج شده‌اند.

### 📁 فایل‌های خروجی
- `cleaned_configs.txt` : کانفیگ‌های یکتا (بدون تکرار)
- `success_config.txt` : کانفیگ‌های سالم (تست شده)
- `link_stats.json` : وضعیت هر لینک اشتراک

> این ریپازیتوری توسط **Vibe Coding** با هدایت انسان و کمک هوش مصنوعی مدیریت می‌شود.
"""

    with open("README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    print("README.md با جدول RTL و تاریخ شمسی به‌روز شد.")

if __name__ == "__main__":
    generate_readme()
