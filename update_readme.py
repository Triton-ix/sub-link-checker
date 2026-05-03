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
    # آمار واقعی
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

    now_utc = datetime.now(timezone.utc)
    jalali_str = to_jalali(now_utc)  # مثال: 1402/02/13 21:39:20

    # لینک مخزن کاربر
    repo_link = "https://github.com/farzanfarhangi/sub-link-checker/blob/main/success_config.txt"

    # تولید محتوای README با راست‌چین و جدول RTL
    readme_content = f"""<div dir="rtl" align="center">

# 🚀 V2Ray Subscription Cleaner & Tester

این کدها با کمک **Vibe Coding** و نظارت انسان با هوش مصنوعی ساخته شده‌اند.

## 📌 نحوه جمع‌آوری خودکار لینک‌های اشتراک
لینک‌های ساب‌اسکریپشن (`pool_address.txt`) هر ۵ روز یکبار با جستجو در ریپازیتوری‌های گیت‌هاب مرتبط با ایران یافت می‌شوند (فقط لینک‌هایی که در ۱۵ روز گذشته بروز شده باشند انتخاب می‌گردند).  
کانفیگ‌های درون همه لینک‌ها استخراج شده و همه کانفیگ‌های تکراری حذف می‌شوند، سپس تمام کانفیگ‌های باقیمانده تست می‌شوند و در نهایت در فایل `success_config.txt` فقط کانفیگ‌هایی که در تست سالم تشخیص داده شده‌اند ذخیره می‌گردد تا شما بتوانید به‌راحتی از آنها استفاده کنید.

---

## 📊 گزارش خودکار وضعیت کانفیگ‌ها

**📅 آخرین بروزرسانی:** در تاریخ {jalali_str} به وقت ایران

<div align="center">

| آیتم | 🔗 کل لینک‌های SUB | ✅ لینک‌های سالم | ❌ لینک‌های خراب | 📥 کل کانفیگ‌ها | 🗑️ کانفیگ‌ تکراری | 🔄 کانفیگ‌ بدون تکرار | 🔴 کانفیگ‌ خراب | 🟢 کانفیگ‌ تست شده |
|------|-------------------|----------------|----------------|----------------|-------------------|---------------------|---------------|-------------------|
| **تعداد** | {total_links} | {working_links} | {dead_links} | {raw_total} | {duplicate_total} | {unique_total} | {dead_configs} | {working_total} |
| **درصد** | 100% | {perc_links_working:.1f}% | {perc_links_dead:.1f}% | 100% | {perc_duplicate:.1f}% | {perc_unique:.1f}% | {perc_dead:.1f}% | {perc_working:.1f}% |

</div>

> درصد ستون **کانفیگ‌ها** نسبت به کل کانفیگ‌های بدون تکرار محاسبه شده است.

---

## 🚀 استفاده آسان

برای استفاده از لیست به‌روز کانفیگ‌های سالم، فقط کافی است لینک زیر را در نرم‌افزارهای V2Ray خود وارد کنید:

👉 **[`{repo_link}`]({repo_link})**

این لینک شامل **{working_total}** کانفیگ تست‌شده و فعال است که در بیش از **{total_links}** لینک اشتراک و در مجموع از بین **{raw_total}** کانفیگ مختلف تکراری و خراب تست و استخراج شده‌اند.

---

## 📁 فایل‌های خروجی

• `pool_address.txt` : لینک‌های ساب‌اسکریپشن پیدا شده  
• `cleaned_configs.txt` : کانفیگ‌های یکتا  
• `success_config.txt` : کانفیگ‌های سالم (تست شده)

</div>
"""
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    print("README.md generated with RTL layout and centered table.")

if __name__ == "__main__":
    generate_readme()
