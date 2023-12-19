#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
cron: 56 13 12 * * *
new Env('美团');
"""

import json, time
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


class MeiTuan:
    def __init__(self, check_items):
        self.check_items = check_items
        self.user_agent = UserAgent().chrome
        self.headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/json;charset=utf-8"
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
            time_now_ms = int(time.time() * 1000)
            time_now_ns_str = str(time.time_ns())
            instanceId = f'{time_now_ns_str[:14]}.{time_now_ns_str[14:].zfill(16)}'
            urlSign = "https://mediacps.meituan.com/gundam/gundamGrabV4"
            cookiesSign = {
                "token": token
            }
            paramsSign = {
                "yodaReady": "h5",
                "csecplatform": "4",
                "csecversion": "2.2.1",
                "mtgsig": {
                    "a1": "1.1",
                    "a2": time_now_ms,
                    "a3": "u626yx251w20527zyu3u86u04986u3u581y62xzuyu597958zz4xw60z",
                    "a5": "El5tTKIDIoaunAdQRzBvNtJBlIIZKjUZLZ==",
                    "a6": "hs1.4a4gsvX1s4RLQYqBR3sFhAcJZUrn8+3VWbJ+meaysJ2qQF48MWzawMI/8cXpLkxCgeHru+9OaWxcRKi7x76XJ3HkJvJ3GxbJAa4mOXU4A8LE=",
                    "x0": 4,
                    "d1": "0b94373b8946cbddef86192182d2fcfd"
                }
            }
            bodySign = {
                "gundamId": 531693,
                "instanceId": instanceId,
                "actualLongitude": 113404419,
                "actualLatitude": 23163929,
                "needTj": True,
                "couponConfigIdOrderCommaString": "620969479,2189245219456,2237835510400,4298495230601,10393817973385,8650758750857,9217094451849,9769502114441,9285949325961,7458408104585,11075935339145,4987378139785,9219588883081,8368840966793,7285182431881,7349815083657,9123712533129,7281017291401,9218550006409,7282280694409,5513815065225,603844019,11131204469385,9137512120969,11040176931465,516213972,622936732,622197908,622740453,10494188389001,10495566742153",
                "couponAllConfigIdOrderString": "620969479,2189245219456,2237835510400,4298495230601,10393817973385,8650758750857,9217094451849,9769502114441,9285949325961,7458408104585,11075935339145,4987378139785,9219588883081,8368840966793,7285182431881,7349815083657,9123712533129,7281017291401,9218550006409,7282280694409,5513815065225,603844019,11131204469385,9137512120969,11040176931465,516213972,622936732,622197908,622740453,10494188389001,10495566742153",
                "rubikCouponKey": "PrizePool-200043026",
                "platform": 13,
                "app": -1,
                "h5Fingerprint": "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"
            }

            resSign = self.req(urlSign, "post", cookiesSign, paramsSign, bodySign)
            self.print_now(json.dumps(resSign))


            urlDoAction = "https://promotion.waimai.meituan.com/playcenter/common/v1/doaction"
            bodyDoAction = {
                "activityViewId": "jXL-9iEaRTsv-FZdpX4Z4g",
                "actionCode": 1000,
                "lat": 23.16397476196289,
                "lng": 113.40444946289062,
                "gdId": 422324,
                "instanceId": instanceId,
                "fpPlatform": 13,
                "utmSource": "",
                "utmCampaign": "",
            }
            resDoAction = self.req(urlDoAction, "post", cookiesSign, {}, bodyDoAction)
            self.print_now(json.dumps(resDoAction))
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
    # data = get_data()
    # _check_items = data.get("MeiTuan", [])
    _check_items = [
        {
            "token": ""
        }
    ]
    result = MeiTuan(check_items=_check_items).main()
    # send("美团", result)
