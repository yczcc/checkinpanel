#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
cron: 31 7 * * *
new Env('阿里云盘');
"""

import json
import requests
from sys import stdout

from notify_mtr import send
from utils import get_data

##变量export ali_refresh_token=''
# ali_refresh_token=os.getenv("ali_refresh_token").split('&')
#refresh_token是一成不变的呢，我们使用它来更新签到需要的access_token
#refresh_token获取教程：https://github.com/bighammer-link/Common-scripts/wiki/%E9%98%BF%E9%87%8C%E4%BA%91%E7%9B%98refresh_token%E8%8E%B7%E5%8F%96%E6%96%B9%E6%B3%95
# ali_refresh_token = os.getenv("ali_refresh_token")

error = False

class ALiYun:
    def __init__(self, check_items):
        self.check_items = check_items

    def print_now(self, content):
        print(content)
        stdout.flush()

    def update_token(self, refresh_token) -> [bool, str]:
        url = "https://auth.aliyundrive.com/v2/account/token"
        data = {
            "grant_type": "refresh_token",
            "app_id": "25dzX3vbYqktVxyX",
            "refresh_token": refresh_token
        }
        try:
            response = requests.post(url=url, json=data).json()
            if 'access_token' in response:
                access_token = response["access_token"]
                return [True, access_token]
            return [False, "更新token失败，" + response["message"]]
        except Exception as e:
            self.print_now("更新token异常")
            self.print_now(e)
        return [False, "更新token异常，请检查refresh_token是否有效"]

    def sign(self, access_token) -> [bool, list]:
        success = True
        url = "https://member.aliyundrive.com/v1/activity/sign_in_list"
        headers = {"Authorization": access_token, "Content-Type": "application/json"}
        data = {"isReward": False}
        try:
            result_sign = requests.post(url=url, headers=headers, json=data).json()
            if "success" not in result_sign or not result_sign["success"]:
                msg = "签到失败，" + result_sign["message"]
                self.print_now(msg)
                return [False, [{"name": "签到&奖励", "value": msg}]]
            sign_days = result_sign["result"]["signInCount"]
            data = {"signInDay": sign_days}
            url_reward = "https://member.aliyundrive.com/v1/activity/sign_in_goods"
            result_reward = requests.post(url=url_reward, headers=headers, data=json.dumps(data)).json()
            if "success" in result_reward and result_reward.get("success"):
                self.print_now("签到成功")
                res = [
                    {
                        "name": "连续签到",
                        "value": str(sign_days) + "天",
                    },
                    {
                        "name": "获得奖励",
                        "value": "{},{},{}".format(
                            result_reward["result"]["goodsName"],
                            result_reward["result"]["rewardName"],
                            result_reward["result"]["rewardDesc"])
                    }
                ]
            else:
                msg = "签到成功，连续签到" + str(sign_days) + "天，查询奖励失败，" + result_reward["message"]
                self.print_now(msg)
                res = [{"name": "签到&奖励", "value": msg}]
        except Exception as e:
            self.print_now("签到或者查询奖励异常")
            self.print_now(e)
            res = [{"name": "签到&奖励", "value": "签到或者查询奖励异常，请检查refresh_token是否有效"}]
            success = False
        return [success, res]

    def main(self):
        global error
        msg_all = ""
        i = 0
        for check_item in self.check_items:
            i += 1
            print(f'开始帐号{i}签到')
            refresh_token = check_item["refresh_token"]
            access_token = self.update_token(refresh_token)
            if access_token[0]:
                res = self.sign(access_token[1])
                if not res[0]:
                    error = True
                msg = res[1]
            else:
                msg = [{"name": "更新token", "value": access_token[1]}]
                error = True
            msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
            msg_all += msg + '\n'
        return msg_all

if __name__ == "__main__":
    _data = get_data()
    _check_items = _data.get("ALIYUN", [])

    # _check_items = [{
        # "refresh_token" : ""
    # }]
    result = ALiYun(check_items=_check_items).main()
    send("阿里云盘", result, error)
