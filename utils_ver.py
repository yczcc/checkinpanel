# -*- coding: utf-8 -*-

import re
import time

import requests

__version__ = "20231216-1-001"
ver_re = re.compile("__version__ = .(\\d+-\\d+-...).")


def get_present_ver() -> str:
    return f"checkinpanel 当前版本：{__version__}"


def get_latest_ver() -> str:
    url = "https://ghproxy.com/https://raw.githubusercontent.com/yczcc/checkinpanel/master/utils_ver.py"
    if time.localtime().tm_hour < 8 or time.localtime().tm_hour > 18:
        return "不在 8-18 点内，跳过版本检查。"
    try:
        r = requests.get(url=url, timeout=3)
    except Exception as e:
        ver_msg = f"获取最新版本失败，错误信息如下：\n{e}"
    else:
        latest_ver = ver_re.findall(r.text)[0] if ver_re.findall(r.text) else "无效版本"
        ver_msg = f"最新版本：{latest_ver}"
    return ver_msg


def print_ver():
    print(f"{get_present_ver()}，{get_latest_ver()}\n")
