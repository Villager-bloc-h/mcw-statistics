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
    username = config["username"] if "username" in config else None
    password = config["password"] if "password" in config else None

wiki_lang = ['de', 'en', 'es', 'fr', 'it', 'ja', 'ko', 'lzh', 'nl', 'pt', 'ru', 'th', 'uk', 'zh', 'meta']

if wiki not in wiki_lang:
    print("不存在此语言的Minecraft Wiki！")
    input("按任意键退出")
    sys.exit(1)

elif wiki == 'en':
    WIKI_BASE_URL = "https://minecraft.wiki"

else:
    WIKI_BASE_URL = f"https://{wiki}.minecraft.wiki"

WIKI_API_URL = WIKI_BASE_URL + "/api.php"

if username and password:
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})

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

else:
    print("未提供用户名和密码，将以未登录状态运作")
    islogin = False


def get_data(params):  # 从Mediawiki API获取数据
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


def get_last_diff():  # 获取当前最大revid
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


def extract_from_timestamp(timestamp_str):  # 提取日期、时间数据，将UTC时间改为当前时区
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
