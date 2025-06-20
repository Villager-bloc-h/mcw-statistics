import time
from datetime import datetime, timedelta
import openpyxl

import base

current_dt = datetime.now()
end_dt = current_dt - timedelta(hours=base.timezone)
end_timestamp = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

start_dt = end_dt - timedelta(days=30)
start_timestamp = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

api_url = base.WIKI_API_URL + "?action=query&format=json&list=recentchanges&formatversion=2&rcprop=user|loginfo&rclimit=500&rctype=edit|new|log"
api_url = api_url + f"&rcstart={end_timestamp}&rcend={start_timestamp}"

wb = openpyxl.Workbook()
ws = wb.active
ws['A1'] = "用户名"
ws['B1'] = "操作数"

user_list = {}
last_rccontinue = ""
loop_count = 0

print("启动成功", end='\n\n')

while True: # 获取过去30天的最近更改详情
    time.sleep(3)

    if last_rccontinue != "":
        last_api_url = api_url + "&rccontinue=" + last_rccontinue
    else:
        last_api_url = api_url

    rc_data = base.get_data(last_api_url)

    loop_count += 1
    print(f"成功获取第{loop_count}组数据")

    for item in rc_data['query']['recentchanges']:
        if item['type'] == "log":
            if 'actionhidden' in item: # 日志详情已移除，忽略
                continue
            elif item['logtype'] == "newusers": # 用户创建日志不计入操作数
                continue

        username = item["user"]
        # 更新计数：存在则+1，不存在则初始化为1
        user_list[username] = user_list.get(username, 0) + 1

    if 'continue' not in rc_data:
        break

    last_rccontinue = rc_data['continue']['rccontinue']

print("所有数据已经获取完毕，正在处理中...")

for user, count in user_list.items():
    row = ws.max_row + 1
    ws.cell(row=row, column=1, value=user)
    ws.cell(row=row, column=2, value=count)

current_timestamp = current_dt.strftime("%Y%m%d%H%M%S")
wb.save(f"activeusers-{current_timestamp}.xlsx")