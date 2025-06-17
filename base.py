import json
import sys
import time

import requests
import datetime

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    wiki = config["wiki"]
    user_agent = config["user_agent"]

if wiki not in ['de', 'en', 'es', 'fr', 'it', 'ja', 'ko', 'lzh', 'nl', 'pt', 'ru', 'th', 'uk', 'zh', 'meta']:
    print("不存在此语言的Minecraft Wiki！")
    sys.exit(1)

elif wiki == 'en':
    WIKI_BASE_URL = "https://minecraft.wiki"

else:
    WIKI_BASE_URL = f"https://{wiki}.minecraft.wiki"

WIKI_API_URL = WIKI_BASE_URL + "/api.php"

def difftime_get_config(): # difftime.py读取配置
    difftime_config = config.get("difftime", {})
    num_diff = int(difftime_config.get("num_diff"))

    minrev_val = difftime_config.get("minrev")
    minrev = int(minrev_val) if minrev_val and minrev_val.strip() != '' else None
    maxrev_val = difftime_config.get("maxrev")
    maxrev = int(maxrev_val) if maxrev_val and maxrev_val.strip() != '' else None

    return num_diff, minrev, maxrev

def get_data(api_url): # 从Mediawiki API获取数据
    tries = 0
    while 1:
        try:
            response = requests.get(api_url, headers={"User-Agent": user_agent})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            tries += 1
            if tries > 1:
                break

            print("未获取到数据，20秒后重试。")
            time.sleep(20)

    print("重试失败，请检查网络连接。")
    sys.exit(1)

def get_last_diff(): # 获取当前最大revid
    api_url = WIKI_API_URL + "?action=query&format=json&list=recentchanges&formatversion=2&rcprop=ids&rclimit=1&rctype=edit|new"
    return get_data(api_url)

def extract_from_timestamp(timestamp_str): # 提取日期、时间数据，将UTC时间改为UTC+8
    # 时间格式：2025-06-16T12:24:55Z
    dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")

    dt = dt + datetime.timedelta(hours=8)

    return (dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second)
