import os
import json
from datetime import datetime

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
    
    working_links_percent = (working_links / total_links * 100) if total_links > 0 else 0
    dead_links_percent = (dead_links / total_links * 100) if total_links > 0 else 0
    unique_percent = (unique_total / raw_total * 100) if raw_total > 0 else 0
    duplicate_percent = 100 - unique_percent if raw_total > 0 else 0
    working_percent = (working_total / unique_total * 100) if unique_total > 0 else 0
    dead_configs_percent = 100 - working_percent if unique_total > 0 else 0
    
    last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    table = f"""
## 🤖 تولید شده توسط هوش مصنوعی
این کدها با کمک **GitHub Copilot** و **پیشنهادات هوش مصنوعی** ساخته و بهینه‌سازی شده‌اند.

## 📊 گزارش خودکار وضعیت کانفیگ‌ها (به‌روزرسانی خودکار هر ۲۴ ساعت)

**📅 آخرین بروزرسانی:** {last_update}

| آیتم | تعداد | درصد |
|------|-------|-------|
| 🔗 لینک‌های اشتراک (کل) | {total_links} | 100% |
| ✅ لینک‌های فعال | {working_links} | {working_links_percent:.1f}% |
| ❌ لینک‌های غیرفعال | {dead_links} | {dead_links_percent:.1f}% |
| 📥 کانفیگ خام استخراج شده | {raw_total} | 100% |
| 🔄 کانفیگ یکتا (بدون تکرار) | {unique_total} | {unique_percent:.1f}% |
| 🗑️ کانفیگ تکراری حذف شده | {raw_total - unique_total} | {duplicate_percent:.1f}% |
| 🟢 کانفیگ سالم (تست شده) | {working_total} | {working_percent:.1f}% |
| 🔴 کانفیگ خراب | {unique_total - working_total} | {dead_configs_percent:.1f}% |

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

> این گزارش به‌طور خودکار هر ۲۴ ساعت یکبار تولید می‌شود و در میانه کار نیز به‌روز می‌گردد.
"""
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(table)
    print("README.md successfully generated!")

if __name__ == "__main__":
    generate_readme()
