import os
import json
from datetime import datetime, timezone, timedelta
import subprocess

# ------------------- تبدیل به تاریخ و زمان ایران (UTC+3:30) و شمسی -------------------
def to_jalali(gregorian_dt):
    # تبدیل datetime utc به ایران (UTC+3:30)
    tehran_tz = timezone(timedelta(hours=3, minutes=30))
    local = gregorian_dt.astimezone(tehran_tz)
    # کتابخانه تبدیل شمسی – چون ممکن است نصب نباشد، از یک تابع ساده استفاده نمی‌کنیم.
    # به جای آن از دستور linux 'date' استفاده می‌کنیم (در GitHub Actions موجود است)
    # یا از کتابخانه jdatetime که در requirements اضافه می‌کنیم.
    # برای اطمینان، ابتدا jdatetime را نصب می‌کنیم.
    try:
        import jdatetime
        return jdatetime.datetime.fromgregorian(datetime=local).strftime("%Y/%m/%d %H:%M:%S")
    except ImportError:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'jdatetime'], capture_output=True)
        import jdatetime
        return jdatetime.datetime.fromgregorian(datetime=local).strftime("%Y/%m/%d %H:%M:%S")

def read_lines_count(fname):
    if not os.path.exists(fname):
        return 0
    with open(fname, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f if _.strip())

def get_link_stats():
    if not os.path.exists("link_stats.json"):
        return 0, 0, 0
    with open("link_stats.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    total = len(data)
    working = sum(1 for v in data.values() if v.get("success"))
    return total, working, total - working

def get_raw_total():
    if not os.path.exists("link_stats.json"):
        return 0
    with open("link_stats.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    total = 0
    for v in data.values():
        if v.get("success"):
            total += v.get("configs_found", 0)
    return total

def generate_readme():
    # آمار لینک‌ها
    total_links, working_links, dead_links = get_link_stats()
    # آمار کانفیگ‌ها
    raw_total = get_raw_total()
    unique_total = read_lines_count("cleaned_configs.txt")
    working_total = read_lines_count("success_config.txt")
    duplicate_total = raw_total - unique_total if raw_total > unique_total else 0
    dead_configs = unique_total - working_total if unique_total > working_total else 0

    # درصدها
    perc_links_working = (working_links / total_links * 100) if total_links else 0
    perc_links_dead = (dead_links / total_links * 100) if total_links else 0
    perc_unique = (unique_total / raw_total * 100) if raw_total else 0
    perc_duplicate = 100 - perc_unique if raw_total else 0
    perc_working = (working_total / unique_total * 100) if unique_total else 0
    perc_dead = 100 - perc_working if unique_total else 0

    # زمان بروزرسانی به شمسی و تهران
    now_utc = datetime.now(timezone.utc)
    jalali_str = to_jalali(now_utc)

    table = f"""
## 🤖 تولید شده با **Vibe Coding** – نظارت انسانی + پیشنهادات هوش مصنوعی  
این کدها با کمک **GitHub Copilot** و بهینه‌سازی‌های هوش مصنوعی ساخته شده‌اند.

### 📌 نحوه جمع‌آوری خودکار لینک‌های اشتراک  
لینک‌های ساب‌اسکریپشن (`pool_address.txt`) هر ۵ روز یکبار با جستجو در ریپازیتوری‌های گیت‌هاب مرتبط با ایران و کلمات کلیدی V2Ray یافت می‌شوند. فقط لینک‌هایی که در ۱۵ روز گذشته بروز شده باشند و محتوای فارسی/ایرانی داشته باشند، انتخاب می‌گردند.

---

## 📊 گزارش خودکار وضعیت کانفیگ‌ها (به‌روزرسانی هر ۲۴ ساعت)

**📅 آخرین بروزرسانی (زمان ایران):** {jalali_str}

| آیتم | 🔗 کل لینکهای ساب‌اسکریپشن | ✅ لینک‌های دارای کانفیگ واقعی | ❌ لینک‌های خراب | 📥 کل کانفیگ‌های استخراج شده | 🗑️ تعداد کانفیگ‌های تکراری حذف شده | 🔄 کل کانفیگ‌های بدون تکرار | 🔴 کل کانفیگ‌های خراب | 🟢 کل کانفیگ‌های سالم و تست شده |
|------|----------------|------------------------|------------------|--------------------------|-----------------------------|-----------------------|---------------------|------------------------------|
| **تعداد** | {total_links} | {working_links} | {dead_links} | {raw_total} | {duplicate_total} | {unique_total} | {dead_configs} | {working_total} |
| **درصد** | 100% | {perc_links_working:.1f}% | {perc_links_dead:.1f}% | 100% | {perc_duplicate:.1f}% | {perc_unique:.1f}% | {perc_dead:.1f}% | {perc_working:.1f}% |

> درصد ستون **کانفیگ‌های بدون تکرار** و **سالم/خراب** نسبت به کل کانفیگ‌های بدون تکرار محاسبه شده است.

### 🧪 روش تست  
- هر کانفیگ با درخواست HTTP به `host:port` در کمتر از ۱ ثانیه تست می‌شود.  
- همزمانی: ۱۰ رشته – ذخیره نتایج هر ۷۰۰۰ کانفیگ در مخزن.  
- لینک‌های اشتراک هر ۵ روز یکبار به‌روز می‌شوند (اکشن جداگانه).

### 📁 فایل‌های خروجی  
- `cleaned_configs.txt` : کانفیگ‌های یکتا  
- `success_config.txt` : کانفیگ‌های سالم (تدریجی append)  
- `link_stats.json` : وضعیت هر لینک اشتراک  

> این ریپازیتوری توسط **Vibe Coding** با هدایت انسان و کمک هوش مصنوعی مدیریت می‌شود.
"""
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(table)
    print("README.md updated with Persian date and new table.")

if __name__ == "__main__":
    # نصب jdatetime در صورتی که نباشد
    try:
        import jdatetime
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'jdatetime'])
        import jdatetime
    generate_readme()
