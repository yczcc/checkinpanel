# -*- coding: utf-8 -*-
"""
cron: 7 11 * * *
new Env('掘金');
"""

import requests
from sys import stdout

from notify_mtr import send
from utils import get_data


class Juejin:
    def __init__(self, check_items):
        self.check_items = check_items
        self.base_url = "https://api.juejin.cn/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/91.0.4472.106 Safari/537.36"
        }

    def print_now(self, content):
        print(content)
        stdout.flush()

    # 获取当前矿石数
    def getCurPoint(self, cookie, uuid):
        msg = " * 当前矿石:" + '\n\t'
        url = f"{self.base_url}growth_api/v1/get_cur_point?aid=2608&uuid={uuid}&spider=0"
        try:
            resSignStatus = requests.get(url=url, headers=self.headers, cookies={"Cookie": cookie}).json()
            if 0 == resSignStatus.get('err_no'):
                msg += "总数" + str(resSignStatus.get('data'))
                return [True, msg]
            msg += "获取失败," + resSignStatus.get('err_msg')
        except Exception as e:
            msg += "获取异常"
            self.print_now(msg)
            self.print_now(e)
        return [False, msg]

    # 获取签到状态
    def getSignStatus(self, cookie, uuid):
        msg = " * 签到状态:" + '\n\t'
        url = f"{self.base_url}growth_api/v2/get_today_status?aid=2608&uuid={uuid}&spider=0"
        try:
            resSignStatus = requests.get(url=url, headers=self.headers, cookies={"Cookie": cookie}).json()
            if 0 == resSignStatus.get('err_no'):
                resSignStatusData = resSignStatus.get('data')
                if not resSignStatusData.get('check_in_done'):
                    msg += "今日未签到"
                    return [0, msg]
                msg += "今日已签到"
                return [1, msg]
            msg += "获取失败," + resSignStatus.get('err_msg')
        except Exception as e:
            msg += "获取异常"
            self.print_now(msg)
            self.print_now(e)
        return [-1, msg]

    # 获取程序员日历
    def getCoderCalendar(self, cookie, uuid):
        msg = " * 程序员日历:" + '\n\t'
        url = f"{self.base_url}growth_api/v1/get_coder_calendar?aid=2608&uuid={uuid}&spider=0"
        try:
            resCoderCalendar = requests.get(url=url, headers=self.headers, cookies={"Cookie": cookie}).json()
            if 0 == resCoderCalendar.get('err_no'):
                resCoderCalendarData = resCoderCalendar.get('data')
                if resCoderCalendarData.get('aphorism') and resCoderCalendarData.get('should_or_not'):
                    msg += resCoderCalendarData.get('aphorism') + "\n\t" + resCoderCalendarData.get('should_or_not')
                    return [True, msg]
            msg += "获取失败," + resCoderCalendar.get('err_msg')
        except Exception as e:
            msg += "获取异常"
            self.print_now(msg)
            self.print_now(e)
        return [False, msg]

    # 签到
    def doSign(self, cookie, uuid):
        msg = ' * 签到任务:' + '\n\t'
        sign_url = f"{self.base_url}growth_api/v1/check_in?aid=2608&uuid={uuid}&spider=0"
        try:
            resSign = requests.post(url=sign_url, headers=self.headers, cookies={"Cookie": cookie}).json()
            if 0 == resSign.get('err_no'):
                resSignData = resSign.get('data')
                msg += "签到成功\n\t签到矿石数" + resSignData['incr_point'] + "\n\t目前总矿石数" + resSignData['sum_point']
                return [True, msg]
            msg += "获取失败," + resSign.get('err_msg')
        except Exception as e:
            msg += "获取异常"
            self.print_now(msg)
            self.print_now(e)
        return [False, msg]

    # 抽奖
    def lottery(self, cookie, uuid):
        lottery_url = f"{self.base_url}growth_api/v1/lottery/draw?aid=2608&uuid={uuid}&spider=0"
        return requests.post(url=lottery_url, headers=self.headers, cookies={"Cookie": cookie}).json()

    def main(self):
        msg_all = ""
        for i, check_item in enumerate(self.check_items, start=1):
            cookie = str(check_item.get("cookie"))
            user_unique_id = str(check_item.get("user_unique_id"))
            msg_all += f"账号 {i}" + '\n'
            resCurPoint = self.getCurPoint(cookie, user_unique_id)
            if not resCurPoint[0]:
                # 请求异常了
                msg_all += resCurPoint[1] + '\n'
                continue
            msg_all += resCurPoint[1] + '\n'

            resGetSignStatus = self.getSignStatus(cookie, user_unique_id)
            if resGetSignStatus[0] < 0:
                # 请求异常了
                msg_all += resGetSignStatus[1] + '\n'
                continue
            elif 1 == resGetSignStatus[0]:
                msg_all += resGetSignStatus[1] + '\n'
            elif 0 == resGetSignStatus[0]:
                msg_all += resGetSignStatus[1] + '\n'
                resDoSign = self.doSign(cookie, user_unique_id)
                msg_all += resDoSign[1] + '\n'
                if resDoSign[0]:
                    # 签到成功
                    lottery_msg = self.lottery(cookie,user_unique_id)["err_msg"]
                    msg_all += ' * 抽奖任务:' + '\n\t' + "抽奖结果:" + lottery_msg + "\n"

            resGetCoderCalendar = self.getCoderCalendar(cookie, user_unique_id)
            msg_all += resGetCoderCalendar[1] + '\n'
            msg_all += '\n'
        return msg_all


if __name__ == "__main__":
    _data = get_data()
    _check_items = _data.get("JUEJIN", [])
    result = Juejin(check_items=_check_items).main()
    send("掘金", result)
