import time
from datetime import datetime
import openpyxl

import base

usergroup_order, usergroup_mapping = base.activeusers_get_config()

# 指定时间段
now = datetime.now()
year = now.year
month = now.month

if month == 2:
    start_date = datetime(year, 1, 28)
    end_date = datetime(year, 2, 25)
elif month == 3:
    start_date = datetime(year, 2, 25)
    end_date = datetime(year, 3, 28)
else:
    if month == 1:
        start_date = datetime(year - 1, 12, 28)
    else:
        start_date = datetime(year, month - 1, 28)

    end_date = datetime(year, month, 28)

start_timestamp = start_date.strftime("%Y-%m-%d") + "T00:00:00Z"
end_timestamp = end_date.strftime("%Y-%m-%d") + "T00:00:00Z"

api_url = base.WIKI_API_URL + "?action=query&format=json&list=recentchanges&formatversion=2&rcprop=user|loginfo&rclimit=500&rctype=edit|new|log"
api_url = api_url + f"&rcstart={end_timestamp}&rcend={start_timestamp}"

wb = openpyxl.Workbook()
ws = wb.active
ws['A1'] = "用户名"
ws['B1'] = "操作数"
ws['C1'] = "本地用户组"
ws.column_dimensions['A'].width = 20.00
ws.column_dimensions['C'].width = 10.89

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

usergroups_api = base.WIKI_API_URL + "?action=query&format=json&list=allusers&formatversion=2&augroup=autopatrol|bot|bureaucrat|interface-admin|patrollers|sysop&auprop=groups&aulimit=500"
usergroups_data = base.get_data(usergroups_api)

user_permissions = {}

# 置为最高级别用户组
for user in usergroups_data['query']['allusers']:
    username = user['name']
    groups = set(user['groups'])

    highest_perm = None
    for perm in usergroup_order:
        if perm in groups:
            highest_perm = perm
            break

    user_permissions[username] = highest_perm

sorted_data = []

for user, count in user_list.items(): # 准备排序的数据
    # 过滤IP用户
    if base.is_ip_address(user):
        continue

    # 获取用户组信息
    usergroup = user_permissions.get(user)
    group_name = usergroup_mapping[usergroup] if usergroup else "无"

    sorted_data.append((user, count, group_name))

sorted_data.sort(key=lambda x: x[1], reverse=True)

# 将排序后的数据写入工作表
for row_idx, (user, count, group_name) in enumerate(sorted_data, start=2):
    ws.cell(row=row_idx, column=1, value=user)
    ws.cell(row=row_idx, column=2, value=count)
    ws.cell(row=row_idx, column=3, value=group_name)

wb.save(f"activeusers-{year}-{month}.xlsx")

print(f"结果已保存至activeusers-{year}-{month}.xlsx")
input("按任意键退出")
