import json
import sys
import time
import re

import requests
import datetime

with open("config.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)
    wiki = config["wiki"]
    user_agent = config["user_agent"]
    timezone = int(config["timezone"])
    username = config["username"]
    password = config["password"]

if wiki not in ['de', 'en', 'es', 'fr', 'it', 'ja', 'ko', 'lzh', 'nl', 'pt', 'ru', 'th', 'uk', 'zh', 'meta']:
    print("不存在此语言的Minecraft Wiki！")
    input("按任意键退出")
    sys.exit(1)

elif wiki == 'en':
    WIKI_BASE_URL = "https://minecraft.wiki"

else:
    WIKI_BASE_URL = f"https://{wiki}.minecraft.wiki"

WIKI_API_URL = WIKI_BASE_URL + "/api.php"

session = requests.Session()

# 获取登录token
r1 = session.get(WIKI_API_URL, params={
    'action': 'query',
    'meta': 'tokens',
    'type': 'login',
    'format': 'json'
})
login_token = r1.json()['query']['tokens']['logintoken']

# 提交用户名和密码
r2 = session.post(WIKI_API_URL, data={
    'action': 'login',
    'lgname': username,
    'lgpassword': password,
    'lgtoken': login_token,
    'format': 'json'
})

# 检查登录结果
result = r2.json()
if result['login']['result'] == 'Success':
    islogin = True
    print("登录成功")
else:
    islogin = False
    print("登录失败：", result['login'])

def difftime_get_config(): # difftime.py读取配置
    difftime_config = config.get("difftime", {})
    num_diff = int(difftime_config.get("num_diff"))

    minrev_val = difftime_config.get("minrev")
    minrev = int(minrev_val) if minrev_val and minrev_val.strip() != '' else None
    maxrev_val = difftime_config.get("maxrev")
    maxrev = int(maxrev_val) if maxrev_val and maxrev_val.strip() != '' else None

    return num_diff, minrev, maxrev

def usercontribs_get_config(): # usercontribs.py读取配置
    usercontribs_config = config.get("usercontribs", {})
    queryusername = usercontribs_config.get("username")
    ucend = usercontribs_config.get("starttime")
    ucstart = usercontribs_config.get("endtime")
    return queryusername, ucend, ucstart

def editperiod_get_config(): # editperiod.py读取配置
    editperiod_config = config.get("editperiod", {})
    datafile = editperiod_config.get("datafile")
    return datafile

def activeusers_get_config(): # activeusers.py读取配置
    activeusers_config = config.get("activeusers", {})
    usergroup_order = activeusers_config.get("usergroup_order")
    usergroup_mapping = activeusers_config.get("usergroup_mapping")
    mode = activeusers_config.get("mode")
    return usergroup_order, usergroup_mapping, mode

def get_data(params): # 从Mediawiki API获取数据
    tries = 0
    while 1:
        try:
            if islogin:
                response = session.post(WIKI_API_URL, data=params)
            else:
                response = requests.get(WIKI_API_URL, params=params, headers={"User-Agent": user_agent})

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            tries += 1
            if tries > 1:
                break

            print("未获取到数据，20秒后重试。")
            time.sleep(20)

    print("重试失败，请检查网络连接。")
    input("按任意键退出")
    sys.exit(1)

def get_last_diff(): # 获取当前最大revid
    params = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "list": "recentchanges",
        "rcprop": "ids",
        "rclimit": 1,
        "rctype": "edit|new"
    }
    return get_data(params)

def extract_from_timestamp(timestamp_str): # 提取日期、时间数据，将UTC时间改为当前时区
    # 时间格式：2025-06-16T12:24:55Z
    dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")

    dt = dt + datetime.timedelta(hours=timezone)

    return dt

def is_ip_address(s):
    ipv4_pattern = r'^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.'
    ipv4_pattern += r'(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.'
    ipv4_pattern += r'(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.'
    ipv4_pattern += r'(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$'

    # IPv6仅匹配大写和完整格式
    ipv6_pattern = r'^([0-9A-F]{1,4}:){7}[0-9A-F]{1,4}$'

    return (
        re.match(ipv4_pattern, s) is not None or
        re.match(ipv6_pattern, s) is not None
    )
