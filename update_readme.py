import os
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone

def persian_date_time():
    """تبدیل UTC به ساعت تهران (ایران) و نمایش به صورت شمسی"""
    try:
        # نصب کتابخانه jdatetime اگر نصب نبود
        subprocess.run([sys.executable, "-m", "pip", "install", "jdatetime"], capture_output=True)
        import jdatetime
        # زمان فعلی UTC را به منطقه تهران (UTC+3:30) تبدیل می‌کنیم
        tehran_tz = timezone(timedelta(hours=3, minutes=30))
        now_utc = datetime.now(timezone.utc)
        now_tehran = now_utc.astimezone(tehran_tz)
        # تبدیل به شمسی
        shamsi = jdatetime.datetime.fromgregorian(datetime=now_tehran.replace(tzinfo=None))
        return shamsi.strftime("%Y/%m/%d %H:%M:%S")
    except:
        # fallback
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

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

def generate_readme():
    total_links, working_links, dead_links = get_link_stats()
    raw_total = get_raw_total()
    unique_total = read_file_lines("cleaned_configs.txt")
    working_total = read_file_lines("success_config.txt")
    
    # محاسبه درصدها
    working_links_percent = (working_links / total_links * 100) if total_links > 0 else 0
    dead_links_percent = (dead_links / total_links * 100) if total_links > 0 else 0
    unique_percent = (unique_total / raw_total * 100) if raw_total > 0 else 0
    duplicate_count = raw_total - unique_total
    duplicate_percent = (duplicate_count / raw_total * 100) if raw_total > 0 else 0
    working_percent = (working_total / unique_total * 100) if unique_total > 0 else 0
    dead_configs_percent = 100 - working_percent if unique_total > 0 else 0
    
    last_update_shamsi = persian_date_time()
    
    table = f"""
## 🤖 این کدها با کمک **vibe coding** با نظارت انسانی و پیشنهادات هوش مصنوعی ساخته و بهینه‌سازی شده‌اند.

## 📊 گزارش خودکار وضعیت کانفیگ‌ها (به‌روزرسانی خودکار هر ۲۴ ساعت)

**📅 آخرین بروزرسانی (به وقت تهران):** {last_update_shamsi}

| آیتم | 🔗 کل لینک‌های ساب‌اسکریپشن پیدا شده | ✅ لینک‌های دارای کانفیگ واقعی | ❌ لینک‌های خراب | 📥 کل کانفیگ‌های استخراج شده | 🗑️ تعداد کانفیگ‌های تکراری حذف شده | 🔄 کل کانفیگ‌های بدون تکرار | 🔴 کل کانفیگ‌های خراب | 🟢 کل کانفیگ‌های سالم و تست شده |
|------|------|------|------|------|------|------|------|------|
| تعداد | {total_links} | {working_links} | {dead_links} | {raw_total} | {duplicate_count} | {unique_total} | {unique_total - working_total} | {working_total} |
| درصد | 100% | {working_links_percent:.1f}% | {dead_links_percent:.1f}% | 100% | {duplicate_percent:.1f}% | {unique_percent:.1f}% | {dead_configs_percent:.1f}% | {working_percent:.1f}% |

### 🧪 روش تست
- هر کانفیگ با ارسال درخواست HTTP به آدرس `host:port` تست می‌شود.
- کد پاسخ کمتر از 500 به معنی سالم بودن است.
- تعداد همزمانی در تست: ۱۰ رشته (برای سرعت بالا و جلوگیری از بلاک)
- فاصله تصادفی بین بسته‌های ۷۰۰۰ تایی: ۱ تا ۲ ثانیه
- بعد از هر بسته ۷۰۰۰ کانفیگ، نتایج در مخزن ذخیره می‌شود.

### 📁 فایل‌های خروجی
- `cleaned_configs.txt` → همه کانفیگ‌های یکتا (بدون تکرار)
- `success_config.txt` → فقط کانفیگ‌های سالم (به‌تدریج append می‌شود)
- `link_stats.json` → جزئیات وضعیت هر لینک اشتراک
- `pool_address.txt` → لیست لینک‌های ساب‌اسکریپشن (هر ۵ روز به‌روز می‌شود)

> این گزارش به‌طور خودکار هر ۲۴ ساعت یکبار تولید می‌شود و در میانه کار نیز به‌روز می‌گردد.
"""
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(table)
    print("README.md successfully generated!")

if __name__ == "__main__":
    generate_readme()
