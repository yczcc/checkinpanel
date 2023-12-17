#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
cron: 31 7 * * *
new Env('阿里云盘');
"""

import json
import requests
import os
from sys import exit, stdout

##变量export ali_refresh_token=''
ali_refresh_token=os.getenv("ali_refresh_token").split('&')
#refresh_token是一成不变的呢，我们使用它来更新签到需要的access_token
#refresh_token获取教程：https://github.com/bighammer-link/Common-scripts/wiki/%E9%98%BF%E9%87%8C%E4%BA%91%E7%9B%98refresh_token%E8%8E%B7%E5%8F%96%E6%96%B9%E6%B3%95
# ali_refresh_token = os.getenv("ali_refresh_token")

class ALiYun:
    def __init__(self, check_items):
        self.check_items = check_items

    def print_now(self, content):
        print(content)
        stdout.flush()

    # 使用refresh_token更新access_token
    def update_token(self, refresh_token):
        url = 'https://auth.aliyundrive.com/v2/account/token'
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        try:
            response = requests.post(url=url, json=data).json()
            access_token = response['access_token']
            return [True, access_token]
        except:
            msg = " * 请求update_token api失败 最大可能是refresh_token失效了 也可能是网络问题"
            self.print_now(msg)
        return [False, msg]

    # 签到函数
    def daily_check(self, access_token):
        url_sign = 'https://member.aliyundrive.com/v1/activity/sign_in_list'
        headers = {
            'Authorization': access_token,
            'Content-Type': 'application/json'
        }
        try:
            response_sign = requests.post(url=url_sign, headers=headers, json={}).text
            result_sign = json.loads(response_sign)
            sign_days = result_sign['result']['signInCount']
            if 'success' not in result_sign:
                return [False, "签到失败"]
            self.print_now('签到成功')
            for i, j in enumerate(result_sign['result']['signInLogs']):
                if j['status'] == 'miss':
                    day_json = result_sign['result']['signInLogs'][i - 1]
                    if not day_json['isReward']:
                        contents = '签到成功，今日未获得奖励'
                    else:
                        contents = '本月累计签到{}天,今日签到获得{}{}'.format(result_sign['result']['signInCount'],
                                                                              day_json['reward']['name'],
                                                                              day_json['reward']['description'])
                    self.print_now(contents)
                    return [True, contents]
            # data = {
            #     'signInDay': sign_days
            # }
            # url_reward = 'https://member.aliyundrive.com/v1/activity/sign_in_reward'
            # resp2 = requests.post(url=url_reward, headers=headers, data=json.dumps(data))
            # result2 = json.loads(resp2.text)
            # print(result2)
        except:
            msg = " 签到失败"
            self.print_now(msg)
        return [False, msg]

    def mian(self):
        msg_all = ""
        i = 0
        for check_item in self.check_items:
            i += 1
            print(f'开始帐号{i}签到')
            refresh_token = check_item["refresh_token"]
            resUpdateToken = self.update_token(refresh_token)
            if not resUpdateToken[0]:
                msg_all += resUpdateToken[1] + '\n'
                continue
            access_token = resUpdateToken[1]
            resDailyCheck = self.daily_check(access_token)
            if not resDailyCheck[0]:
                msg_all += resDailyCheck[1] + '\n'
                continue
            msg_all += resDailyCheck[1] + '\n'
        return msg_all

if __name__ == "__main__":
    # _data = get_data()
    # _check_items = _data.get("ALIYUN", [])

    _check_items = [{
        "refresh_token" : ""
    }]
    result = ALiYun(check_items=_check_items).main()
    # send("阿里云盘", result)
