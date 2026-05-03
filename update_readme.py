import os
import json
from datetime import datetime, timezone
import subprocess
import sys

# نصب jdatetime در صورت نبود (برای تبدیل به شمسی)
try:
    import jdatetime
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'jdatetime'])
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
    dead_links = total_links - working_links
    return total_links, working_links, dead_links

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

def jalali_now():
    """بازگرداندن تاریخ و زمان حال به شمسی (تهران)"""
    now_utc = datetime.now(timezone.utc)
    # ایران UTC+3:30 (بدون تغییر ساعت در تابستان - ساده‌سازی)
    tehran_offset = 3.5
    tehran_time = now_utc + timedelta(hours=tehran_offset)
    # تبدیل به شمسی
    jalali_dt = jdatetime.datetime.fromgregorian(datetime=tehran_time)
    return jalali_dt.strftime("%Y/%m/%d - %H:%M:%S")

# نیاز به timedelta برای محاسبه offset
from datetime import timedelta

def generate_readme():
    # جمع‌آوری آمار
    total_links, working_links, dead_links = get_link_stats()
    raw_total = get_raw_total()
    unique_total = read_file_lines("cleaned_configs.txt")
    working_total = read_file_lines("success_config.txt")
    
    duplicate_count = raw_total - unique_total
    bad_configs = unique_total - working_total
    
    # محاسبه درصدها (بر مبنای مناسب)
    perc_working_links = (working_links / total_links * 100) if total_links else 0
    perc_dead_links = (dead_links / total_links * 100) if total_links else 0
    perc_unique = (unique_total / raw_total * 100) if raw_total else 0
    perc_duplicate = (duplicate_count / raw_total * 100) if raw_total else 0
    perc_working_configs = (working_total / unique_total * 100) if unique_total else 0
    perc_bad_configs = (bad_configs / unique_total * 100) if unique_total else 0
    
    last_update_jalali = jalali_now()
    
    # جدول بر اساس خواسته شما
    table = f"""
## 🤖 تولید شده با Vibe Coding
این کدها با کمک **Vibe Coding**، نظارت انسانی و پیشنهادات هوش مصنوعی ساخته و بهینه‌سازی شده‌اند.

### 📡 لینک‌های ساب‌اسکریپشن
لینک‌های اشتراک (ساب‌اسکریپشن) به صورت خودکار از مخازن عمومی گیت‌هاب که محتوای مرتبط با ایران دارند و در ۱۵ روز گذشته به‌روز شده‌اند، استخراج می‌شوند. سپس با بررسی مستقیم هر لینک (درخواست HEAD) لینک‌های معتبر در فایل `pool_address.txt` ذخیره می‌گردند. این فرآیند هر ۵ روز یکبار انجام می‌شود.

---

**📅 آخرین بروزرسانی (به وقت تهران):** {last_update_jalali}

| آیتم | 🔗 کل لینکهای ساب‌اسکریپشن پیدا شده | ✅ لینک‌های دارای کانفیگ واقعی | ❌ لینک‌های خراب | 📥 کل کانفیگ‌های استخراج شده | 🗑️ تعداد کانفیگ‌های تکراری حذف شده | 🔄 کل کانفیگ‌های بدون تکرار | 🔴 کل کانفیگ‌های خراب | 🟢 کل کانفیگ‌های سالم و تست شده |
|------|-----------------------------------|----------------------------------|----------------|----------------------------|----------------------------------|---------------------------|-----------------------|----------------------------------|
| **تعداد** | {total_links} | {working_links} | {dead_links} | {raw_total} | {duplicate_count} | {unique_total} | {bad_configs} | {working_total} |
| **درصد** | 100% | {perc_working_links:.1f}% | {perc_dead_links:.1f}% | 100% | {perc_duplicate:.1f}% | {perc_unique:.1f}% | {perc_bad_configs:.1f}% | {perc_working_configs:.1f}% |

> **نکته:** درصد کانفیگ‌های سالم و خراب نسبت به کل کانفیگ‌های بدون تکرار (ستون `🔄 کل کانفیگ‌های بدون تکرار`) محاسبه شده است.

### 🧪 روش تست کانفیگ‌ها
- هر کانفیگ با ارسال درخواست HTTP به آدرس `host:port` در کمتر از ۱ ثانیه تست می‌شود.
- کد پاسخ کمتر از 500 به معنی سالم بودن است.
- تعداد همزمانی: ۱۰ رشته (برای سرعت بالا و جلوگیری از بلاک شدن IP)
- هر ۷۰۰۰ کانفیگ، نتایج میانی در مخزن ذخیره می‌شوند.

### 📁 فایل‌های خروجی
- `cleaned_configs.txt` ← همه کانفیگ‌های یکتا (بدون تکرار)
- `success_config.txt` ← فقط کانفیگ‌های سالم (به‌تدریج append می‌شود)
- `link_stats.json` ← جزئیات وضعیت هر لینک اشتراک
- `pool_address.txt` ← لیست لینک‌های ساب‌اسکریپشن (بروزرسانی هر ۵ روز)

> این گزارش هر ۲۴ ساعت یکبار به‌روز می‌شود و در میانه‌ی تست کانفیگ‌ها (هر ۷۰۰۰ کانفیگ) نیز نتایج در مخزن commit می‌گردد.
"""
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(table)
    print("README.md successfully generated!")

if __name__ == "__main__":
    generate_readme()
