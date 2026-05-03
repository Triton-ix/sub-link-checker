import os
import json
from datetime import datetime, timezone, timedelta
import subprocess
import sys

def install_jdatetime():
    try:
        import jdatetime
        return jdatetime
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'jdatetime'])
        import jdatetime
        return jdatetime

def to_jalali(gregorian_dt):
    jdatetime = install_jdatetime()
    tehran_tz = timezone(timedelta(hours=3, minutes=30))
    local = gregorian_dt.astimezone(tehran_tz)
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
    # آمار مورد نیاز
    total_links, working_links, dead_links = get_link_stats()
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

    # تاریخ و زمان شمسی
    now_utc = datetime.now(timezone.utc)
    jalali_str = to_jalali(now_utc)

    # تولید متن README با جدول RTL و اعداد پویا
    readme_content = f"""این کدها با کمک **Vibe Coding** و با نظارت انسان با هوش مصنوعی ساخته شده‌اند.

## نحوه جمع‌آوری خودکار لینک‌های اشتراک
لینک‌های سابسکریپشن (`pool_address.txt`) هر ۵ روز یکبار با جستجو در ریپازیتوری‌های گیت‌هاب مرتبط با ایران یافت می‌شوند (فقط لینک‌هایی که در ۱۵ روز گذشته بروز شده باشند انتخاب می‌گردند).  
کانفیگ‌های درون همه لینکها استخراج شده و همه کانفیگهای تکراری حذف می‌شوند، سپس تمام کانفیگ‌های باقیمانده تست می‌شوند و در نهایت در فایل `success_config.txt` فقط کانفیگ‌هایی که در تست سالم تشخیص داده شده‌اند ذخیره می‌گردد تا شما بتوانید به‌راحتی از آنها استفاده کنید.

لینک زیر شامل **{working_total}** کانفیگ تست‌شده و فعال است که از بیش از **{total_links}** لینک سابسکریپشن و در مجموع از بین **{raw_total}** کانفیگ مختلف (تکراری و خراب) تست و استخراج شده‌اند.

برای استفاده از کانفیگ‌های سالم، فقط کافی است لینک زیر را در نرم‌افزار های کلاینت V2Ray خود وارد کنید:  
👉 **https://github.com/farzanfarhangi/sub-link-checker/blob/main/success_config.txt**

---

## 📊 گزارش خودکار وضعیت کانفیگ‌ها

**📅 آخرین بروزرسانی :** در تاریخ **{jalali_str}** به وقت ایران

<div dir="rtl" align="center">

| آیتم | 🔗 کل لینکهای SUB | ✅ لینک‌های سالم | ❌ لینک‌های خراب | 📥 کل کانفیگ‌ها | 🗑️ کانفیگ تکراری | 🔄 کانفیگ بدون تکرار | 🔴 کانفیگ خراب | 🟢 کانفیگ تست شده |
|------|------------------|----------------|----------------|----------------|------------------|---------------------|---------------|------------------|
| **تعداد** | {total_links} | {working_links} | {dead_links} | {raw_total} | {duplicate_total} | {unique_total} | {dead_configs} | {working_total} |
| **درصد** | 100% | {perc_links_working:.1f}% | {perc_links_dead:.1f}% | 100% | {perc_duplicate:.1f}% | {perc_unique:.1f}% | {perc_dead:.1f}% | {perc_working:.1f}% |

</div>

> درصد ستون‌های **کانفیگ بدون تکرار**، **کانفیگ خراب** و **کانفیگ تست شده** نسبت به کل کانفیگ‌های بدون تکرار محاسبه شده است.

### 📁 فایل‌های خروجی
- **`pool_address.txt`** : لینک‌های سابسکرایب پیدا شده
- **`cleaned_configs.txt`** : کانفیگ‌های یکتا (بدون تکرار)
- **`success_config.txt`** : کانفیگ‌های سالم و تست شده

> این ریپازیتوری توسط **Vibe Coding** با هدایت انسان و کمک هوش مصنوعی مدیریت می‌شود.
"""
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    print("README.md successfully generated with RTL table and Persian date.")

if __name__ == "__main__":
    generate_readme()
