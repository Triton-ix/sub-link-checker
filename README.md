
<div dir="rtl" style="text-align: justify;">

این کدها با کمک **Vibe Coding** و با نظارت انسان با هوش مصنوعی ساخته شده‌اند.

## نحوه جمع‌آوری خودکار لینک‌های اشتراک
لینک‌های سابسکریپشن (`pool_address.txt`) هر ۵ روز یکبار با جستجو در ریپازیتوری‌های گیت‌هاب مرتبط با ایران یافت می‌شوند ( فقط لینک‌هایی که در ۵ روز گذشته بروز شده باشند انتخاب می‌گردند).  
کانفیگ‌های درون همه لینکها استخراج شده و همه کانفیگ‌های تکراری حذف می‌شوند سپس تمام کانفیگ‌های باقیمانده تست می‌شوند و در نهایت در فایل `success_config.txt` فقط کانفیگ‌هایی که در تست سالم تشخیص داده شده‌اند ذخیره می‌گردد تا شما بتوانید به‌راحتی از آنها استفاده کنید.

لینک زیر شامل **<u>30812 کانفیگ تست‌شده و فعال</u>** است که در بیش از **<u>158 لینک سابسکریپشن</u>** و در مجموع از بین **<u>619479 کانفیگ مختلف</u>** تکراری و خراب تست و استخراج شده‌اند.

برای استفاده از کانفیگ‌های سالم، فقط کافی است لینک زیر را در نرم‌افزار های کلاینت V2Ray خود وارد کنید:  
👉 [https://github.com/kagemoosha/sub-link-checker/blob/main/success_config.txt](https://github.com/kagemoosha/sub-link-checker/blob/main/success_config.txt)

## گزارش خودکار وضعیت کانفیگ‌ها

**آخرین بروزرسانی :** همین الان


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
<td>158</td>
<td>158</td>
<td>0</td>
<td>619479</td>
<td>361164</td>
<td>258315</td>
<td>227503</td>
<td>30812</td>
</tr>
<tr>
<td style="font-weight: bold;">درصد</td>
<td>100%</td>
<td>100.0%</td>
<td>0.0%</td>
<td>100%</td>
<td>58.3%</td>
<td>41.7%</td>
<td>88.1%</td>
<td>11.9%</td>
</tr>
</tbody>
</table>
</div>
<p style="text-align: center;">درصد کانفیگ‌ها نسبت به کل کانفیگ‌های بدون تکرار محاسبه شده است.<br>
کانفیگ‌های تست شده فقط کانفیگ‌هایی هستند که در تست سریع زیر ۳۰۰ میلی ثانیه پینگ داده‌اند.</p>


## فایل‌های خروجی
- `pool_address.txt` : لینک های سابسکرایب پیدا شده  
- `cleaned_configs.txt` : کانفیگ‌های یکتا  
- `success_config.txt` : کانفیگ‌های سالم (تست شده)

</div>
