import json
import sys
import openpyxl
from datetime import datetime

import base

datafile = base.editperiod_get_config()

try:
    with open(f"{datafile}.json", "r", encoding="utf-8") as contribs_file:
        contribs_data = json.load(contribs_file)
except FileNotFoundError:
    print("指定的文件不存在！")
    sys.exit(1)

username = contribs_data[0]["user"]

wb = openpyxl.Workbook()
sheet1 = wb.active
sheet1.title = "按每小时计"
sheet1['A1'] = "时间段"
sheet1['B1'] = "编辑数"
sheet1.column_dimensions['A'].width = 12.00

row = 2
hours = ["00:00-01:00","01:00-02:00","02:00-03:00","03:00-04:00","04:00-05:00","05:00-06:00","06:00-07:00","07:00-08:00","08:00-09:00","09:00-10:00","10:00-11:00","11:00-12:00","12:00-13:00","13:00-14:00","14:00-15:00","15:00-16:00","16:00-17:00","17:00-18:00","18:00-19:00","19:00-20:00","20:00-21:00","21:00-22:00","22:00-23:00","23:00-00:00"]

while row < 26: # 第一个表格内容初始化
    sheet1[f'A{row}'] = hours[row-2]
    sheet1[f'B{row}'] = 0
    row += 1

sheet2 = wb.create_sheet("按一周七天计")
sheet2['A1'] = "星期"
sheet2['B1'] = "编辑数"

row = 2
weekdays = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]

while row < 9: # 第二个表格内容初始化
    sheet2[f'A{row}'] = weekdays[row-2]
    sheet2[f'B{row}'] = 0
    row += 1

print("启动成功", end='\n\n')

for item in contribs_data:
    dt = base.extract_from_timestamp(item["timestamp"])
    hour = dt.hour
    sheet1.cell(row=hour+2, column=2).value += 1

    weekday = dt.weekday()
    sheet2.cell(row=weekday+2, column=2).value += 1

current_time = datetime.now().strftime("%Y%m%d%H%M%S")
wb.save(f"{username}-editperiod-{current_time}.xlsx")

print(f"结果已保存至{username}-editperiod-{current_time}.xlsx")
input("按任意键退出")
