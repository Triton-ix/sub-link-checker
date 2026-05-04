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

def hours_ago(dt_utc):
    """Returns number of hours since given UTC datetime, as a string e.g. '3 ساعت پیش'"""
    now = datetime.now(timezone.utc)
    diff = now - dt_utc
    hours = int(diff.total_seconds() // 3600)
    if hours < 1:
        return "همین الان"
    return f"{hours} ساعت پیش"

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

    # درصدها (نسبت به مبنای مناسب)
    perc_links_working = (working_links / total_links * 100) if total_links else 0
    perc_links_dead = (dead_links / total_links * 100) if total_links else 0
    perc_raw = 100.0
    perc_duplicate = (duplicate_total / raw_total * 100) if raw_total else 0
    perc_unique = (unique_total / raw_total * 100) if raw_total else 0
    perc_dead_configs = (dead_configs / unique_total * 100) if unique_total else 0
    perc_working = (working_total / unique_total * 100) if unique_total else 0

    # زمان بروزرسانی (از زمان آخرین commit این فایل یا حالا)
    # برای نمایش "ساعت پیش" از زمان حال استفاده می‌کنیم (لحظه تولید)
    now_utc = datetime.now(timezone.utc)
    last_update_str = hours_ago(now_utc)  # در لحظه تولید 0 ساعت است، ولی برای نمایش "همین الان" خوب است
    # اما برای واقعیت، بهتر است زمان آخرین commit را بگیریم. ساده می‌گیریم زمان حال:
    # چون README تازه تولید شده، می‌نویسیم "همین الان"
    if last_update_str == "همین الان":
        last_update_display = "همین الان"
    else:
        last_update_display = last_update_str

    # تولید جدول HTML با راست به چپ و وسط‌چین
    html_table = f"""
<div dir="rtl" style="text-align: center; overflow-x: auto;">
<table style="margin-left: auto; margin-right: auto; border-collapse: collapse; width: 100%; text-align: center;">
<thead>
<tr style="background-color: #f2f2f2;">
<th>آیتم</th>
<th>🔗 کل لینکهای SUB</th>
<th>✅ لینک‌های سالم</th>
<th>❌ لینک‌های خراب</th>
<th>📥 کل کانفیگ‌ها</th>
<th>🗑️ کانفیگ‌ تکراری</th>
<th>🔄 کانفیگ‌ بدون تکرار</th>
<th>🔴 کانفیگ‌ خراب</th>
<th>🟢 کانفیگ‌ تست شده</th>
</tr>
</thead>
<tbody>
<tr>
<td style="font-weight: bold;">تعداد</td>
<td>{total_links}</td>
<td>{working_links}</td>
<td>{dead_links}</td>
<td>{raw_total}</td>
<td>{duplicate_total}</td>
<td>{unique_total}</td>
<td>{dead_configs}</td>
<td>{working_total}</td>
</tr>
<tr>
<td style="font-weight: bold;">درصد</td>
<td>100%</td>
<td>{perc_links_working:.1f}%</td>
<td>{perc_links_dead:.1f}%</td>
<td>100%</td>
<td>{perc_duplicate:.1f}%</td>
<td>{perc_unique:.1f}%</td>
<td>{perc_dead_configs:.1f}%</td>
<td>{perc_working:.1f}%</td>
</tr>
</tbody>
</table>
</div>
<p style="text-align: center;">درصد کانفیگ‌ها نسبت به کل کانفیگ‌های بدون تکرار محاسبه شده است.<br>
کانفیگ‌های تست شده فقط کانفیگ‌هایی هستند که در تست سریع زیر ۳۰۰ میلی ثانیه پینگ داده‌اند.</p>
"""

    # تاریخ شمسی برای نمایش (اختیاری، ولی برای ساعت پیش نیازی نیست)
    jalali_date = to_jalali(now_utc)  # برای استفاده در جای دیگر

    # متن اصلی با اعداد داینامیک (بولد و زیرخط دار)
    readme_content = f"""
<div dir="rtl" style="text-align: justify;">

این کدها با کمک **Vibe Coding** و با نظارت انسان با هوش مصنوعی ساخته شده‌اند.

## نحوه جمع‌آوری خودکار لینک‌های اشتراک
لینک‌های سابسکریپشن (`pool_address.txt`) هر ۵ روز یکبار با جستجو در ریپازیتوری‌های گیت‌هاب مرتبط با ایران یافت می‌شوند ( فقط لینک‌هایی که در ۵ روز گذشته بروز شده باشند انتخاب می‌گردند).  
کانفیگ‌های درون همه لینکها استخراج شده و همه کانفیگ‌های تکراری حذف می‌شوند سپس تمام کانفیگ‌های باقیمانده تست می‌شوند و در نهایت در فایل `success_config.txt` فقط کانفیگ‌هایی که در تست سالم تشخیص داده شده‌اند ذخیره می‌گردد تا شما بتوانید به‌راحتی از آنها استفاده کنید.

لینک زیر شامل **<u>{working_total} کانفیگ تست‌شده و فعال</u>** است که در بیش از **<u>{total_links} لینک سابسکریپشن</u>** و در مجموع از بین **<u>{raw_total} کانفیگ مختلف</u>** تکراری و خراب تست و استخراج شده‌اند.

برای استفاده از کانفیگ‌های سالم، فقط کافی است لینک زیر را در نرم‌افزار های کلاینت V2Ray خود وارد کنید:  
👉 [https://github.com/kagemoosha/sub-link-checker/blob/main/success_config.txt](https://github.com/kagemoosha/sub-link-checker/blob/main/success_config.txt)

## گزارش خودکار وضعیت کانفیگ‌ها

**آخرین بروزرسانی :** {last_update_display}

{html_table}

## فایل‌های خروجی
- `pool_address.txt` : لینک های سابسکرایب پیدا شده  
- `cleaned_configs.txt` : کانفیگ‌های یکتا  
- `success_config.txt` : کانفیگ‌های سالم (تست شده)

</div>
"""
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    print("README.md updated with RTL table and dynamic numbers.")

if __name__ == "__main__":
    generate_readme()
