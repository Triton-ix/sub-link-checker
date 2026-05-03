import os
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
import jdatetime  # نیاز به نصب دارد

def install_jdatetime():
    try:
        __import__('jdatetime')
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'jdatetime'])

install_jdatetime()
import jdatetime

def read_file_lines(filename):
    if not os.path.exists(filename):
        return 0
    with open(filename, 'r', encoding='utf-8') as f:
        return sum(1 for line in f if line.strip())

def get_link_stats():
    stats_file = "link_stats.json"
    if not os.path.exists(stats_file):
        return 0, 0, 0
    with open(stats_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    total_links = len(data)
    working_links = sum(1 for v in data.values() if v.get("success", False))
    return total_links, working_links, total_links - working_links

def get_raw_total():
    stats_file = "link_stats.json"
    if not os.path.exists(stats_file):
        return 0
    with open(stats_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    total = 0
    for v in data.values():
        if v.get("success", False):
            total += v.get("configs_found", 0)
    return total

def get_iran_time():
    """بازگرداندن زمان حال به هجری شمسی و ساعت ایران (UTC+3:30)"""
    utc_now = datetime.now(timezone.utc)
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    iran_now = utc_now.astimezone(iran_tz)
    # تبدیل به شمسی
    shamsi = jdatetime.datetime.fromgregorian(datetime=iran_now.replace(tzinfo=None))
    return shamsi.strftime("%Y/%m/%d %H:%M:%S")

def generate_readme():
    total_links, working_links, dead_links = get_link_stats()
    raw_total = get_raw_total()
    unique_total = read_file_lines("cleaned_configs.txt")
    working_total = read_file_lines("success_config.txt")
    
    # محاسبه درصدها بر اساس تعداد کل کانفیگ‌های یکتا به عنوان مبنا
    unique_base = unique_total if unique_total > 0 else 1
    duplicate_count = raw_total - unique_total
    duplicate_percent = (duplicate_count / raw_total * 100) if raw_total > 0 else 0
    working_percent = (working_total / unique_base * 100)
    dead_configs_percent = 100 - working_percent
    
    last_update = get_iran_time()
    
    # جدول به صورت افقی (یک ردیف با چند ستون)
    # برای خوانایی، در Markdown می‌توانیم چند ردیف بسازیم یا یک ردیف طولانی با جداکننده
    # بهترین شکل: یک جدول با دو ردیف: ردیف اول عنوان، ردیف دوم مقادیر
    table = f"""
## 🤖 تولید شده با vibe coding
این کدها با کمک **vibe coding** با نظارت انسانی و پیشنهادات هوش مصنوعی ساخته و بهینه‌سازی شده‌اند.

## 📊 گزارش خودکار وضعیت کانفیگ‌ها (به‌روزرسانی خودکار)

**📅 آخرین بروزرسانی (به وقت تهران):** {last_update}

| آیتم | 🔗 لینک‌های اشتراک (کل) | ✅ لینک‌های فعال | ❌ لینک‌های غیرفعال | 📥 کانفیگ خام استخراج شده | 🔄 کانفیگ یکتا (بدون تکرار) | 🗑️ کانفیگ تکراری حذف شده | 🟢 کانفیگ سالم (تست شده) | 🔴 کانفیگ خراب |
|------|------------------------|----------------|--------------------|--------------------------|---------------------------|--------------------------|------------------------|----------------|
| تعداد | {total_links} | {working_links} | {dead_links} | {raw_total} | {unique_total} | {duplicate_count} | {working_total} | {unique_total - working_total} |
| درصد | 100% | {(working_links/total_links*100) if total_links>0 else 0:.1f}% | {(dead_links/total_links*100) if total_links>0 else 0:.1f}% | 100% | {(unique_total/raw_total*100) if raw_total>0 else 0:.1f}% | {duplicate_percent:.1f}% | {working_percent:.1f}% | {dead_configs_percent:.1f}% |

### 🧪 روش تست
- هر کانفیگ با ارسال درخواست HTTP به آدرس `host:port` تست می‌شود (timeout 1 ثانیه)
- کد پاسخ کمتر از 500 به معنی سالم بودن است.
- تعداد همزمانی در تست: ۱۰ رشته
- فاصله تصادفی بین بسته‌های ۷۰۰۰ تایی: ۱ تا ۲ ثانیه
- بعد از هر بسته ۷۰۰۰ کانفیگ، نتایج در مخزن ذخیره می‌شود.
- لینک‌های اشتراک هر ۵ روز یکبار از گیت‌هاب جمع‌آوری می‌شوند (شرط: اشاره به ایران و آپدیت کمتر از ۱۵ روز).

### 📁 فایل‌های خروجی
- `cleaned_configs.txt` → همه کانفیگ‌های یکتا (بدون تکرار)
- `success_config.txt` → فقط کانفیگ‌های سالم (به‌تدریج append می‌شود)
- `pool_address.txt` → لینک‌های ساب‌اسکریپشن (خودکار به‌روز می‌شود)
- `link_stats.json` → جزئیات وضعیت هر لینک اشتراک

> این گزارش به‌طور خودکار هر ۲۴ ساعت یکبار تولید می‌شود.
"""
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(table)
    print("README.md successfully generated with Persian date and horizontal table.")

if __name__ == "__main__":
    generate_readme()
