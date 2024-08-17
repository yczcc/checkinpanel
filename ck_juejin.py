# -*- coding: utf-8 -*-
"""
cron: 7 11 * * *
new Env('掘金');
"""
import datetime
import time

import requests
from sys import stdout

from notify_mtr import send
from utils import get_data

error = False

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
    def getCurPoint(self, cookie, uuid, msToken, a_bogus):
        msg = " * 当前矿石:" + '\n\t'
        url = f"{self.base_url}growth_api/v1/get_cur_point?aid=2608&uuid={uuid}&spider=0&msToken=" + msToken + "&a_bogus=" + a_bogus
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

    # 获取签到矿石数
    def getSignPointCount(self, cookie, uuid):
        msg = " * 签到矿石数:" + '\n\t'
        url = f"{self.base_url}growth_api/v1/get_by_month?aid=2608&uuid={uuid}&spider=0"
        try:
            day_time = int(time.mktime(datetime.date.today().timetuple()))
            res = requests.get(url=url, headers=self.headers, cookies={"Cookie": cookie}).json()
            if 0 == res.get('err_no'):
                resData = res.get('data')
                get_cur_day = False
                point_cur_day = 0
                for resDataPoint in resData:
                    if not 'date' in resDataPoint or not 'status' in resDataPoint or not 'point' in resDataPoint:
                        msg += "获取矿石数失败," + res.get("err_msg")
                        return [0, msg]
                    if 1 != resDataPoint.get('status') or day_time != resDataPoint.get('date'):
                        continue
                    point_cur_day = resDataPoint.get('point')
                    get_cur_day = True
                    break
                if not get_cur_day:
                    msg += "获取矿石数失败,未获取到今天的矿石数"
                    return [0, msg]
                msg += ("今日签到获取" + str(point_cur_day))
                return [0, msg]
            msg += "获取失败," + res.get('err_msg')
        except Exception as e:
            msg += "获取异常"
            self.print_now(msg)
            self.print_now(e)
        return [-1, msg]

    # 获取签到天数
    def getSignDayCount(self, cookie, uuid):
        msg = " * 签到天数:" + '\n\t'
        url = f"{self.base_url}growth_api/v1/get_counts?aid=2608&uuid={uuid}&spider=0"
        try:
            res = requests.get(url=url, headers=self.headers, cookies={"Cookie": cookie}).json()
            if 0 == res.get('err_no'):
                resData = res.get('data')
                if not 'cont_count' in resData or not 'sum_count' in resData:
                    msg += "获取天数失败," + res.get("err_msg")
                    return [0, msg]
                msg += ("连续" + str(resData.get('cont_count')) + "天,累计"
                        + str(resData.get('sum_count')) + "天")
                return [0, msg]
            msg += "获取失败," + res.get('err_msg')
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
    def doSign(self, cookie, uuid, msToken, a_bogus) -> [bool, str]:
        msg = ' * 签到任务:' + '\n\t'
        sign_url = f"{self.base_url}growth_api/v1/check_in?aid=2608&uuid={uuid}&spider=0&msToken=" + msToken + "&a_bogus=" + a_bogus
        try:
            resSign = requests.post(url=sign_url, headers=self.headers, cookies={"Cookie": cookie}).json()
            if 0 == resSign.get('err_no'):
                resSignData = resSign.get('data')
                msg += "签到成功\n\t签到矿石数" + str(resSignData['incr_point']) + "\n\t目前总矿石数" + str(resSignData['sum_point'])
                return [True, msg]
            msg += "签到失败," + resSign.get('err_msg')
        except Exception as e:
            msg += "签到异常"
            self.print_now(msg)
            self.print_now(e)
        return [False, msg]

    # 获取幸运值
    def my_lucky(self, cookie, uuid):
        msg = ' * 获取幸运值:' + '\n\t'
        lottery_url = f"{self.base_url}growth_api/v1/lottery_lucky/my_lucky?aid=2608&uuid={uuid}&spider=0"
        try:
            resLucky = requests.post(url=lottery_url, headers=self.headers, cookies={"Cookie": cookie}).json()
            if 0 == resLucky.get('err_no'):
                resLuckyData = resLucky.get('data')
                if not 'total_value' in resLuckyData:
                    msg += "解析幸运值失败," + resLucky.get("err_msg")
                    return [False, msg]
                msg += ("当前幸运值" + str(resLuckyData.get('total_value')) + "/6000")
                return [True, msg]
            msg += "获取幸运值失败," + resLucky.get('err_msg')
        except Exception as e:
            msg += "获取幸运值异常"
            self.print_now(msg)
            self.print_now(e)
        return [False, msg]

    # 抽奖
    def lottery(self, cookie, uuid):
        msg = ' * 抽奖:' + '\n\t'
        lottery_url = f"{self.base_url}growth_api/v1/lottery/draw?aid=2608&uuid={uuid}&spider=0"
        try:
            res = requests.post(url=lottery_url, headers=self.headers, cookies={"Cookie": cookie}).json()
            if 0 == res.get('err_no'):
                resData = res.get('data')
                if not 'lottery_name' in resData:
                    msg += "解析抽奖失败," + res.get("err_msg")
                    return [False, msg]
                msg += ("抽奖获得【" + resData.get('lottery_name') + "】")
                return [True, msg]
            msg += "抽奖失败," + res.get('err_msg')
        except Exception as e:
            msg += "抽奖异常"
            self.print_now(msg)
            self.print_now(e)
        return [False, msg]

    def main(self):
        msg_all = ""
        global error
        for i, check_item in enumerate(self.check_items, start=1):
            cookie = str(check_item.get("cookie"))
            user_unique_id = str(check_item.get("user_unique_id"))
            ms_token = str(check_item.get("ms_token"))
            a_bogus = str(check_item.get("a_bogus"))
            msg_all += f"账号 {i}" + '\n'
            resCurPoint = self.getCurPoint(cookie, user_unique_id, ms_token, a_bogus)
            if not resCurPoint[0]:
                # 请求异常了
                msg_all += resCurPoint[1] + '\n'
                error = True
                continue
            msg_all += resCurPoint[1] + '\n'

            resGetSignStatus = self.getSignStatus(cookie, user_unique_id)
            if resGetSignStatus[0] < 0:
                # 请求异常了
                msg_all += resGetSignStatus[1] + '\n'
                error = True
                continue
            elif 1 == resGetSignStatus[0]:
                msg_all += resGetSignStatus[1] + '\n'
                resPointCount = self.getSignPointCount(cookie, user_unique_id)
                msg_all += resPointCount[1] + '\n'
                resDayCount = self.getSignDayCount(cookie, user_unique_id)
                msg_all += resDayCount[1] + '\n'
            elif 0 == resGetSignStatus[0]:
                msg_all += resGetSignStatus[1] + '\n'
                resDoSign = self.doSign(cookie, user_unique_id)
                msg_all += resDoSign[1] + '\n'
                if resDoSign[0]:
                    # 签到成功
                    myLuckyRes = self.my_lucky(cookie,user_unique_id)
                    msg_all += myLuckyRes[1] + '\n'
                    lotteryRes = self.lottery(cookie,user_unique_id)
                    msg_all += lotteryRes[1] + '\n'
                else:
                    error = True
                resPointCount = self.getSignPointCount(cookie, user_unique_id)
                msg_all += resPointCount[1] + '\n'
                resDayCount = self.getSignDayCount(cookie, user_unique_id)
                msg_all += resDayCount[1] + '\n'
            resGetCoderCalendar = self.getCoderCalendar(cookie, user_unique_id)
            msg_all += resGetCoderCalendar[1] + '\n'
            msg_all += '\n'
        return msg_all


if __name__ == "__main__":
    _data = get_data()
    _check_items = _data.get("JUEJIN", [])
    result = Juejin(check_items=_check_items).main()
    send("掘金", result, error)
