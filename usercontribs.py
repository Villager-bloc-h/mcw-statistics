import time
import sys
from datetime import datetime
import json

import base

username, ucend, ucstart = base.usercontribs_get_config()

api_url = base.WIKI_API_URL + f"?action=query&format=json&list=usercontribs&formatversion=2&uclimit=500&ucuser={username}&ucprop=ids|title|timestamp|comment|size|flags|sizediff|tags"

if ucend != "":
    api_url = api_url + "&ucend=" + ucend

if ucstart != "":
    api_url = api_url + "&ucstart=" + ucstart

contribs_result = []
last_uccontinue = ""
loop_count = 0

print("启动成功", end='\n\n')

while True:
    time.sleep(3)

    if last_uccontinue != "":
        last_api_url = api_url + "&uccontinue=" + last_uccontinue
    else:
        last_api_url = api_url

    contribs_data = base.get_data(last_api_url)

    if 'error' in contribs_data:
        print("API返回错误信息，请检查时间戳格式是否正确。")
        sys.exit(1)

    if not contribs_data['query']['usercontribs']:
        print("API未返回有效数据，请检查用户是否存在、用户是否有贡献或时间范围是否正确。")
        sys.exit(1)

    contribs_result.extend(contribs_data['query']['usercontribs'])

    loop_count += 1
    print(f"成功获取第{loop_count}组数据")

    if 'continue' not in contribs_data:
        break

    last_uccontinue = contribs_data['continue']['uccontinue']

contribs_result = contribs_result[::-1]

current_time = datetime.now().strftime("%Y%m%d%H%M%S")
with open(f'usercontribs-{username}-{current_time}.json', 'w', encoding='utf-8') as file:
    json.dump(contribs_result, file, ensure_ascii=False, indent=4)
