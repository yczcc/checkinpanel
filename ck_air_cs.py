#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
cron: 56 13 12 * * *
new Env('南方航空');
"""

import json
import datetime
from calendar import monthrange
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


class AirCS:
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

    def getAwardList(self, token):
        msg = " * 奖励列表" + '\n\t'
        try:
            cookies = {
                "sign_user_token": token,
                "TOKEN": token,
                "cs1246643sso": token,
            }
            params = {
                "type": "APPTYPE",
                "chanel": "ss",
                "lang": "zh"
            }
            # 奖励列表
            urlAwardList = "https://wxapi.csair.com/marketing-tools/award/awardList"
            bodyAwardList = {
                "activityType": "sign",
                "awardStatus": "waitReceive",
                "pageNum": 1,
                "pageSize": 100
            }
            resAwardList = self.req(urlAwardList, "post", cookies, params, bodyAwardList)
            if resAwardList.get("respCode") != "0000":
                msg += "请求失败[" + resAwardList.get("respMsg") + "]"
            else:
                if 0 == len(resAwardList['data']['list']):
                    msg += '奖励已领完'
                    return [True, msg]
                for award in resAwardList["data"]["list"]:
                    urlAward = "https://wxapi.csair.com/marketing-tools/award/getAward"
                    bodyAward = {
                        "activityType": "sign",
                        "signUserRewardId": award["id"]
                    }
                    resAwardList = self.req(urlAward, "post", cookies, params, bodyAward)
                    msg += "获取奖励：" + resAwardList["data"]["result"] + '\n'
                return [True, msg]
        except Exception:
            msg += '南航签到异常'
        return [False, msg]

    def getSignCalendar(self, token):
        msg = " * 签到日历" + '\n\t'
        try:
            month_start = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, 1).strftime(
                "%Y%m%d")
            month_end = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,
                                          monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[
                                              1]).strftime("%Y%m%d")
            urlSignCalendar = "https://wxapi.csair.com/marketing-tools/sign/getSignCalendar"
            paramsSignCalendar = {
                "type": "APPTYPE",
                "chanel": "ss",
                "lang": "zh",
                "startQueryDate": month_start,
                "endQueryDate": month_end
            }
            cookiesSignCalendar = {
                "sign_user_token": token
            }
            resSignCalendar = self.req(urlSignCalendar, "get", cookiesSignCalendar, paramsSignCalendar, None)
            if resSignCalendar.get("respCode") == "0000":
                msg += f'当月累计已签到 {resSignCalendar["data"]["totalActivitySignDay"]} 天'
                return [True, msg]
            else:
                msg += "请求失败[" + resSignCalendar.get("respMsg") + "]"
        except Exception:
            msg += '请求异常'
        return [False, msg]

    def sign(self, token):
        msg = ' * 每日签到' + '\n\t'
        try:
            # 签到
            urlSign = "https://wxapi.csair.com/marketing-tools/activity/join"
            cookiesSign = {
                "sign_user_token": token,
                "TOKEN": token,
                "cs1246643sso": token,
            }
            paramsSign = {
                "type": "APPTYPE",
                "chanel": "ss",
                "lang": "zh"
            }
            bodySign = {
                "activityType": "sign",
                "channel": "app",
                "entrance": None
            }
            resSign = self.req(urlSign, "post", cookiesSign, paramsSign, bodySign)
            if resSign.get("respCode") == "0000":
                msg += "签到成功"
                return [True, msg]
            elif resSign.get("respCode") == "S2001":
                msg += "今天已签到"
                return [True, msg]
            else:
                msg = "签到失败，请检查token是否有效[" + resSign.get("respMsg") + "]"
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

            # 获取奖励
            resAwardList = self.getAwardList(token=token)
            msg_all += resAwardList[1] + "\n"

            # 获取奖励
            resSignCalendar = self.getSignCalendar(token=token)
            msg_all += resSignCalendar[1] + "\n"
        return msg_all


if __name__ == "__main__":
    data = get_data()
    _check_items = data.get("AirCS", [])
    result = AirCS(check_items=_check_items).main()
    send("南方航空", result)
