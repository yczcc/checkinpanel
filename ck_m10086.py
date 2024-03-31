#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
cron: 31 7 * * *
new Env('中国移动');
"""
import time
import json
from sys import stdout
import requests
import random

# from notify_mtr import send
# from utils import get_data

class M10086:
    def __init__(self, check_items):
        self.check_items = check_items

    def print_now(self, content):
        print(content)
        stdout.flush()

    def update_token(self, refresh_token):
        url = "https://"
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        response = requests.post(url=url, json=data).json()
        access_token = response["access_token"]
        return access_token

    def sign_records(self, token):
        timestamp_s = int(time.time())
        nonce = random.randint(100000, 999999)
        url = "https://"
        headers = {
            "Host": "tm-web.pin-dao.cn",
            "Accept": "application/json, text/plain, */*",
            "Authorization": "Bearer " + token,
            "Sec-Fetch-Site": "same-origin",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors",
            "Content-Type": "application/json",
            "Origin": "https://tm-web.pin-dao.cn",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.43(0x18002b2f) NetType/4G Language/zh_CN miniProgram/wxab7430e6e8b9a4ab",
            "Referer" : "https://tm-web.pin-dao.cn/user/sign/records"
        }

        data = {
            "common": {
                "platform": "wxapp",
                "version": "5.2.7",
                "imei": "",
                "osn": "iPhone XR<iPhone11,8>",
                "sv": "iOS 16.6",
                "lat": 39.0645884874132,
                "lng": 117.62045355902778,
                "lang": "zh_CN",
                "currency": "CNY",
                "timeZone": "",
                "nonce": nonce,
                "openId": "QL6ZOftGzbziPlZwfiXM",
                "timestamp": timestamp_s,
                "signature": "qU4OHxfBsS0syiKab1EgTOnIJSw="
            },
            "params": {
                "businessType": 1,
                "brand": 26000252,
                "tenantId": 1,
                "channel": 2,
                "stallType": "PD_S_004",
                "storeId": 26074241,
                "storeType": 1,
                "cityId": 120100,
                "appId": "wxab7430e6e8b9a4ab",
                "signDate": "2024-2-01",
                "startDate": "2024-2-2"}
        }
        response = requests.post(url=url, headers=headers, json=data).json()
        res_code = response["code"]
        if 0 != res_code:
            return None
        res_data = response["data"]
        return res_data

    # 公众号签到
    def sign(self, token):
        url = "https://wx.10086.cn/qwhdhub/api/mark/do/mark"
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.42(0x18002a2a) NetType/4G Language/zh_CN",
            "login-check": "1",
            "Cookie": f"SESSION_TOKEN={token}"
        }
        result = requests.get(url=url, headers=headers).json()
        sign_days = result["result"]["signInCount"]
        data = {"signInDay": sign_days}
        url_reward = "https://member.aliyundrive.com/v1/activity/sign_in_reward"
        requests.post(url=url_reward, headers=headers, data=json.dumps(data))
        if "success" in result:
            print("签到成功")
            for i, j in enumerate(result["result"]["signInLogs"]):
                if j["status"] == "miss":
                    day_json = result["result"]["signInLogs"][i - 1]
                    if not day_json["isReward"]:
                        msg = [
                            {
                                "name": "累计签到",
                                "value": result["result"]["signInCount"],
                            },
                            {
                                "name": "阿里云盘",
                                "value": "签到成功，今日未获得奖励",
                            }
                        ]
                    else:
                        msg = [
                            {
                                "name": "累计签到",
                                "value": result["result"]["signInCount"],
                            },
                            {
                                "name": "阿里云盘",
                                "value": "获得奖励：{}{}".format(
                                    day_json["reward"]["name"],
                                    day_json["reward"]["description"],
                                ),
                            },
                        ]

                    return msg

    def main(self):
        msg_all = ""
        i = 0
        for check_item in self.check_items:
            i += 1
            print(f'开始帐号{i}签到')
            refresh_token = check_item["refresh_token"]
            access_token = self.update_token(refresh_token)
            msg = self.sign(access_token)
            msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
            msg_all += msg + '\n'
        return msg_all


if __name__ == "__main__":
    # _data = get_data()
    # _check_items = _data.get("NAIXUE", [])

    _check_items = [{
        "refresh_token": "",
        "token": ".."
    }]
    result = M10086(check_items=_check_items).main()
    # send("奈雪", result)
