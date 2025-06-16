import time
import openpyxl
from datetime import datetime

from openpyxl.styles import NamedStyle

import base

num_diff = 1000 # 未来可能会改成从配置文件加载

api_url = base.WIKI_API_URL + "?action=compare&format=json&prop=timestamp&formatversion=2"
minrev = 1
maxrev = base.get_last_diff()['query']['recentchanges'][0]['revid']

rev = minrev
fromrev = rev
torev = rev

wb = openpyxl.Workbook()
ws = wb.active
date_style = NamedStyle(name="date_style", number_format="YYYY-MM-DD")
wb.add_named_style(date_style)
ws.column_dimensions['A'].width = 10.89
ws.column_dimensions['C'].width = 10.89
ws['A1'] = "日期"
ws['B1'] = "revid"

while rev < maxrev:
    time.sleep(1)

    current_url = api_url + f"&fromrev={fromrev}&torev={torev}"

    data = base.get_data(current_url)

    if 'compare' in data:
        row = ws.max_row + 1
        fromtimestamp = data['compare']['fromtimestamp']
        totimestamp = data['compare']['totimestamp']
        year1, month1, day1, hour1, minute1, second1 = base.extract_from_timestamp(fromtimestamp)
        year2, month2, day2, hour2, minute2, second2 = base.extract_from_timestamp(totimestamp)
        from_date_obj = datetime(year1, month1, day1)

        if year1 != year2 or month1 != month2 or day1 != day2:
            to_date_obj = datetime(year2, month2, day2)
            ws.cell(row=row, column=3, value=to_date_obj).style = date_style

        ws.cell(row=row, column=1, value=from_date_obj).style = date_style
        ws.cell(row=row, column=2, value=fromrev)

        print(f"成功获取revid为{fromrev}的差异数据")

        rev = rev + num_diff
        fromrev = rev
        torev = rev

    elif rev - fromrev > 5 or torev - rev > 5: # 防止大量修订数据被删除时拖慢程序速度
        print(f"{fromrev}-{torev}的差异数据均无法查询！")

        rev = rev + num_diff
        fromrev = rev
        torev = rev

    else:
        fromrev_url = api_url + f"&fromrev={fromrev}&torev={fromrev}"
        torev_url = api_url + f"&torev={torev}&fromrev={torev}"

        fromrev_data = base.get_data(fromrev_url)
        time.sleep(0.5)
        torev_data = base.get_data(torev_url)

        if 'error' in fromrev_data and fromrev > minrev:
            fromrev = fromrev - 1

        if 'error' in torev_data and torev < maxrev:
            torev = torev + 1

current_time = datetime.now().strftime("%H%M%S")
wb.save(f"output-{current_time}.xlsx")