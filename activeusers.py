import time
from datetime import datetime
import openpyxl

import base

# 读取配置，包括：用户组排列顺序和用户组名称
usergroup_order, usergroup_mapping = base.activeusers_get_config()

'''
设置时间段：
如果当前是2月，那么统计1月28日到2月25日的数据；
如果当前是3月，那么统计2月25日到3月28日的数据；
如果不符合上述情况，那么统计上月28日到本月28日的数据。

API只接受UTC时间的时间戳，因此需要根据时区做合适处理。
'''
now = datetime.now()
year = now.year
month = now.month
day1 = 28
day2 = 25
day = day1 # 此变量用于固定文件名显示的日期

if base.timezone > 0: # 这些时区0点时，UTC时间在上一天
    day1 -= 1
    day2 -= 1

if month == 2:
    start_date = datetime(year, 1, day1)
    end_date = datetime(year, 2, day2)
    day = day2
elif month == 3:
    start_date = datetime(year, 2, day2)
    end_date = datetime(year, 3, day1)
else:
    if month == 1:
        start_date = datetime(year - 1, 12, day1)
    else:
        start_date = datetime(year, month - 1, day1)

    end_date = datetime(year, month, day1)

'''
day只会有三种情况：
1. 默认值28，这个时候day1有可能是27或28，不过不重要
2. 25，这个时候day2也是25，即UTC时间的日期与当前时区的日期相同，因此不需要更改
3. 24，这个时候day2也是24，即UTC时间的日期是当前时区的日期的前一天，因此需要加1
'''
if day == 24:
    day = 25

hour = (24 - base.timezone) % 24
start_timestamp = start_date.strftime("%Y-%m-%d") + f"T{hour:02d}:00:00Z"
end_timestamp = end_date.strftime("%Y-%m-%d") + f"T{hour:02d}:00:00Z"

api_url = base.WIKI_API_URL + "?action=query&format=json&list=recentchanges&formatversion=2&rcprop=user|loginfo&rclimit=500&rctype=edit|new|log"
api_url = api_url + f"&rcstart={end_timestamp}&rcend={start_timestamp}"

# 设置excel表格格式
wb = openpyxl.Workbook()
ws = wb.active
ws['A1'] = "排名"
ws['B1'] = "用户名"
ws['C1'] = "操作数"
ws['D1'] = "本地用户组"
ws.column_dimensions['B'].width = 20.00
ws.column_dimensions['D'].width = 10.89

user_list = {}
last_rccontinue = ""
loop_count = 0

print("启动成功", end='\n\n')

while True: # 获取过去30天的最近更改详情
    time.sleep(3)

    if last_rccontinue != "": # 不是首次循环，使用这个继续
        last_api_url = api_url + "&rccontinue=" + last_rccontinue
    else: # 首次循环
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

    if 'continue' not in rc_data: # 已经全部获取完成，跳出循环
        break

    last_rccontinue = rc_data['continue']['rccontinue']

print("所有数据已经获取完毕，正在处理中...")

# 获取用户组信息
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

# 过滤IP用户，将用户组信息放入列表
for user, count in user_list.items():
    if base.is_ip_address(user):
        continue

    # 获取用户组信息
    usergroup = user_permissions.get(user)
    group_name = usergroup_mapping[usergroup] if usergroup else "无"

    sorted_data.append((user, count, group_name))

sorted_data.sort(key=lambda x: x[1], reverse=True)

ranks = []
current_rank = 1
prev_count = sorted_data[0][1]

# 添加排名数据
for i, data in enumerate(sorted_data):
    count = data[1]
    if count != prev_count:
        current_rank = i + 1
    ranks.append(current_rank)
    prev_count = count

# 将排序后的数据写入工作表
for idx, (user, count, group_name) in enumerate(sorted_data):
    row_idx = idx + 2
    ws.cell(row=row_idx, column=1, value=ranks[idx] if ranks else idx + 1)
    ws.cell(row=row_idx, column=2, value=user)
    ws.cell(row=row_idx, column=3, value=count)
    ws.cell(row=row_idx, column=4, value=group_name)

excel_filename = f"activeusers-{year}-{month:02d}-{day}.xlsx"
wb.save(excel_filename)
print(f"Excel结果已保存至{excel_filename}")

# 将排序后的内容变为wikitable
start_date_str = f"{start_date.year}年{start_date.month}月{start_date.day}日"
end_date_str = f"{end_date.year}年{end_date.month}月{end_date.day}日"

wiki_content = '''{| class="wikitable sortable collapsible"
|+ %s-%s活跃用户列表
|-
! 排名 !! 用户名 !! 操作数 !! 本地用户组
''' % (start_date_str, end_date_str)

for idx, (user, count, group_name) in enumerate(sorted_data):
    group_display = group_name
    if group_name != "无":
        group_display = f"[[Minecraft Wiki:{group_name}|{group_name}]]"

    rank = ranks[idx] if ranks else idx + 1
    wiki_content += "|-\n"
    wiki_content += f"| {rank} || [[User:{user}|{user}]] || {count} || {group_display}\n"

wiki_content += "|}"

# 将wikitable写入文本文件
txt_filename = f"activeusers-{year}-{month:02d}-{day}.txt"
with open(txt_filename, "w", encoding="utf-8") as f:
    f.write(wiki_content)
print(f"Wiki表格已保存至{txt_filename}")

input("按任意键退出")
