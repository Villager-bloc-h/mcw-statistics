import json
import sys
from datetime import timedelta

import openpyxl
from openpyxl.styles import NamedStyle

import base

datafile = base.editperiod_get_config()

try:
    with open(f"{datafile}.json", "r", encoding="utf-8") as contribs_file:
        contribs_data = json.load(contribs_file)
except FileNotFoundError:
    print("指定的文件不存在！")
    input("按任意键退出")
    sys.exit(1)

username = contribs_data[0]["user"]

wb = openpyxl.Workbook()
ws = wb.active
date_style = NamedStyle(name="date_style", number_format="YYYY-MM-DD")
wb.add_named_style(date_style)
ws.column_dimensions['A'].width = 10.89
ws['A1'] = "日期"
ws['B1'] = "总编辑数"

start_timestamp = base.extract_from_timestamp(contribs_data[0]["timestamp"])
end_timestamp = base.extract_from_timestamp(contribs_data[-1]["timestamp"])

edit_count = {}

for item in contribs_data:
    date_str = base.extract_from_timestamp(item["timestamp"]).strftime("%Y-%m-%d")
    edit_count[date_str] = edit_count.get(date_str, 0) + 1

row = 2
one_day = timedelta(days=1)
cur_timestamp = start_timestamp
while cur_timestamp <= end_timestamp:
    date_str = cur_timestamp.strftime("%Y-%m-%d")
    if row == 2:
        value = edit_count[date_str]
    elif date_str in edit_count:
        value = ws[f'B{row-1}'].value + edit_count[date_str]
    else:
        value = ws[f'B{row-1}'].value

    ws.cell(row=row, column=1, value=cur_timestamp).style = "date_style"
    ws.cell(row=row, column=2, value=value)
    row += 1
    cur_timestamp += one_day

current_time = datafile[-14:]
wb.save(f"{username}-editintegration-{current_time}.xlsx")

print(f"结果已保存至{username}-editintegration-{current_time}.xlsx")
input("按任意键退出")
