import json
import requests
import datetime

WIKI_BASE_URL = "https://zh.minecraft.wiki"
WIKI_API_URL = WIKI_BASE_URL + "/api.php"

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    user_agent = config["user_agent"]

def get_data(api_url): # 从Mediawiki API获取数据
    response = requests.get(api_url, headers={"User-Agent": user_agent})
    response.raise_for_status()
    return response.json()

def get_last_diff(): # 获取当前最大revid
    api_url = WIKI_API_URL + "?action=query&format=json&list=recentchanges&formatversion=2&rcprop=timestamp|ids&rclimit=1&rctype=edit|new"
    response = requests.get(api_url, headers={"User-Agent": user_agent})
    response.raise_for_status()
    return response.json()

def extract_from_timestamp(timestamp_str): # 提取日期、时间数据，将UTC时间改为UTC+8
    # 时间格式：2025-06-16T12:24:55Z
    dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")

    dt = dt + datetime.timedelta(hours=8)

    return (dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second)