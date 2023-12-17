#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
cron: 56 18 12 * * *
new Env('携程');
"""

import json
from os import system
from sys import stdout

# from notify_mtr import send
# from utils import get_data

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


class Ctrip:
    def __init__(self, check_items):
        self.check_items = check_items
        self.user_agent = UserAgent().chrome
        self.headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
            "Referer": "https://m.ctrip.com/activitysetupapp/mkt/index/membersignin2021?isHideNavBar=YES&pushcode=h5main&secondwakeup=true&from=https%3A%2F%2Fm.ctrip.com%2Fhtml5%2F"
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

    def sign(self, cticket, guid):
        msg = ' * 每日签到' + '\n\t'
        try:
            # 签到
            # https://m.ctrip.com/restapi/soa2/22769/signToday?_fxpcqlniredt=09031059115068292037&x-traceID=09031059115068292037-1702810594161-7311028
            urlSign = "https://m.ctrip.com/restapi/soa2/22769/signToday"

            # "https://m.ctrip.com/restapi/soa2/22769/getSignDetail?_fxpcqlniredt=09031059115068292037&x-traceID=09031059115068292037-1702810594305-9686484"
            urlSign = "https://m.ctrip.com/restapi/soa2/22769/getSignDetail"

            cookiesSign = {
                "GUID": guid,
                "cticket": cticket,
                "login_type": 0
            }
            bodySign = {
                "platform": "H5",
                "openId": "",
                "rmsToken": "",
                "head": {
                    "cid": guid,
                    "ctok": "",
                    "cver": "1.0",
                    "lang": "01",
                    "sid": "8888",
                    "syscode": "09",
                    "auth": "",
                    "xsid": "",
                    "extension": []
                }
            }
            resSign = self.req(urlSign, "post", cookiesSign, None, bodySign)
            if resSign.get("code") == 0:
                msg += "签到成功, 连续签到 " + resSign.get('continueDay') + " 天"
                return [True, msg]
            elif resSign.get("code") == 2:
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
            cticket = check_item["cticket"]
            guid = check_item["guid"]
            # 签到
            resSign = self.sign(cticket=cticket, guid=guid)
            if not resSign[0]:
                msg_all += resSign[1] + "\n"
                continue
            msg_all += resSign[1] + "\n"
        return msg_all


if __name__ == "__main__":
    # data = get_data()
    # _check_items = data.get("Ctrip", [])
    _check_items = [
        {
            "cticket": "xx",
            "guid": "xx"
        }
    ]
    result = Ctrip(check_items=_check_items).main()
    # send("携程", result)
