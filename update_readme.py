import os
import json
import time
from datetime import datetime

def read_file_lines(filename):
    if not os.path.exists(filename):
        return 0, []
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        return len(lines), lines

def get_link_stats():
    stats_file = "link_stats.json"
    if not os.path.exists(stats_file):
        return 0, 0
    with open(stats_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    total_links = len(data)
    working_links = sum(1 for v in data.values() if v.get("success", False))
    return total_links, working_links

def time_since_last_update():
    # زمان آخرین commit را از فایل README.md نمی‌توان به راحتی گرفت،
    # به جای آن از زمان فعلی سیستم استفاده می‌کنیم و در جدول می‌نویسیم:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

def generate_readme():
    # 1. آمار لینک‌های اشتراک
    total_links, working_links = get_link_stats()
    dead_links = total_links - working_links

    # 2. آمار کانفیگ‌ها
    raw_count, _ = read_file_lines("cleaned_configs.txt")  # unique configs (after dedup)
    # برای تعداد خام (قبل از dedup) باید از link_stats.json جمع بزنیم یا از خروجی؟ ساده‌تر:
    # ما در sub_link_checker خروجی چاپ می‌کند ولی فایل جدا ندارد. بیایید یک فایل raw_count.txt هم ایجاد کنیم؟
    # برای دقت بیشتر، از خود cleaned_configs.txt که همان یکتاست استفاده می‌کنیم و درصد تکراری را تخمین می‌زنیم.
    # اما برای نمایش درصد تکراری به اطلاعات خام نیاز داریم. راه حل: در sub_link_checker یک فایل raw_configs_count.txt بنویسیم.
    # تغییر کوچک: اجازه دهید از link_stats.json تعداد configهای خام را جمع کنیم (هر لینک configs_found دارد).
    raw_total = 0
    if os.path.exists("link_stats.json"):
        with open("link_stats.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            for v in data.values():
                if v.get("success", False):
                    raw_total += v.get("configs_found", 0)
    unique_total = raw_count  # cleaned_configs.txt lines
    duplicate_percent = 0
    if raw_total > 0:
        duplicate_percent = ((raw_total - unique_total) / raw_total) * 100

    # 3. آمار کانفیگ‌های سالم
    working_total, _ = read_file_lines("success_config.txt")
    working_percent = (working_total / unique_total * 100) if unique_total > 0 else 0

    # 4. زمان آخرین بروزرسانی
    last_update = time_since_last_update()

    # ساخت جدول Markdown
    table = f"""
## 📊 گزارش خودکار وضعیت کانفیگ‌ها

**📅 آخرین بروزرسانی:** {last_update}

| آیتم | تعداد | درصد |
|------|-------|-------|
| 🔗 لینک‌های اشتراک (کل) | {total_links} | 100% |
| ✅ لینک‌های فعال | {working_links} | { (working_links/total_links*100) if total_links>0 else 0:.1f}% |
| ❌ لینک‌های غیرفعال | {dead_links} | { (dead_links/total_links*100) if total_links>0 else 0:.1f}% |
| 📥 کانفیگ خام استخراج شده | {raw_total} | 100% |
| 🔄 کانفیگ یکتا (بدون تکرار) | {unique_total} | { (unique_total/raw_total*100) if raw_total>0 else 0:.1f}% |
| 🗑️ کانفیگ تکراری حذف شده | {raw_total - unique_total} | {duplicate_percent:.1f}% |
| 🟢 کانفیگ سالم (تست شده) | {working_total} | {working_percent:.1f}% |
| 🔴 کانفیگ خراب | {unique_total - working_total} | { (100 - working_percent) if unique_total>0 else 0:.1f}% |

### 🧪 روش تست
- هر کانفیگ با ارسال درخواست HTTP به آدرس `host:port` تست می‌شود.
- کد پاسخ کمتر از 500 به معنی سالم بودن است.
- تعداد همزمانی در تست: ۵ رشته (برای جلوگیری از مسدود شدن IP)
- فاصله تصادفی بین درخواست‌ها: ۰٫۱ تا ۰٫۵ ثانیه

### 📁 فایل‌های خروجی
- `cleaned_configs.txt` → همه کانفیگ‌های یکتا (بدون تکرار)
- `success_config.txt` → فقط کانفیگ‌های سالم
- `link_stats.json` → جزئیات وضعیت هر لینک اشتراک

> این گزارش به‌طور خودکار هر ۲۴ ساعت یکبار تولید می‌شود.
"""
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(table)
    print("README.md successfully generated!")

if __name__ == "__main__":
    generate_readme()
