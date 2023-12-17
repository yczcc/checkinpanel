#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
cron: 56 15 12 * * *
new Env('四川航空');
"""

import json
from os import system
from sys import stdout

from notify_mtr import send
from utils import get_data

try:
    import requests
    from fake_useragent import UserAgent
except:
    print(
        "你还没有安装requests库和fake_useragent库 正在尝试自动安装 请在安装结束后重新执行此脚本\n若还是提示本条消息 请自行运行pip3 install requests和pip3 install fake-useragent或者在青龙的依赖管理里安装python的requests和fake-useragent")
    system("pip3 install fake-useragent")
    system("pip3 install requests")
    print("安装完成 脚本退出 请重新执行")
    exit(0)


class AirSiChuan:
    def __init__(self, check_items):
        self.check_items = check_items
        self.user_agent = UserAgent().chrome
        self.headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/json"
        }

    def print_now(self, content):
        print(content)
        stdout.flush()

    def req(self, url, req_method="GET", cookies=None, params=None, body=None):
        data = {}
        if req_method.upper() == "GET":
            try:
                data = requests.get(url, headers=self.headers, cookies=cookies, params=params).json()
            except:
                self.print_now("请求发送失败,可能为网络异常")
            return data
        elif req_method.upper() == "POST":
            try:
                data = requests.post(url, headers=self.headers, cookies=cookies, params=params,
                                     data=json.dumps(body)).json()
            except:
                self.print_now("请求发送失败,可能为网络异常")
            return data
        elif req_method.upper() == "OTHER":
            try:
                requests.get(url, headers=self.headers, cookies=cookies, params=json.dumps(params))
            except:
                self.print_now("请求发送失败,可能为网络异常")
        else:
            self.print_now("您当前使用的请求方式有误,请检查")

    def sign(self, token):
        msg = ' * 每日签到' + '\n\t'
        try:
            # 签到
            urlSign = "https://fx.sichuanair.com/api/v1/sign/get-sign-rotation"
            paramsSign = {
                "access-token": token
            }
            resSign = self.req(urlSign, "post", None, paramsSign, None)
            if resSign.get("code") == 200:
                msg += "签到成功"
                return [True, msg]
            elif resSign.get("code") == "S2001":
                msg += "今天已签到"
                return [True, msg]
            else:
                msg = "签到失败，请检查token是否有效[" + resSign.get("message") + "]"
        except Exception:
            msg += '请求异常'
        return [False, msg]

    def main(self):
        msg_all = ""
        for check_item in self.check_items:
            token = check_item["token"]
            # 签到
            resSign = self.sign(token=token)
            if not resSign[0]:
                msg_all += resSign[1] + "\n"
                continue
            msg_all += resSign[1] + "\n"
        return msg_all


if __name__ == "__main__":
    data = get_data()
    _check_items = data.get("AirSiChuan", [])
    result = AirSiChuan(check_items=_check_items).main()
    send("四川航空", result)