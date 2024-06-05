#!/usr/bin/python3
# -- coding: utf-8 --
"""
cron "30 7,10 * * *" script-path=xxx.py,tag=匹配cron用
new Env('爱奇艺签到加刷时长');
"""

import time
from random import randint, choice
import json
from hashlib import md5 as md5Encode
from urllib.parse import unquote
from string import digits, ascii_lowercase, ascii_uppercase
from sys import exit, stdout
from os import system
import re

from notify_mtr import send
from utils import get_data

try:
    from requests import Session, get, post
    from fake_useragent import UserAgent
except:
    print(
        "你还没有安装requests库和fake_useragent库 正在尝试自动安装 请在安装结束后重新执行此脚本\n若还是提示本条消息 请自行运行pip3 install requests和pip3 install fake-useragent或者在青龙的依赖管理里安装python的requests和fake-useragent")
    system("pip3 install fake-useragent")
    system("pip3 install requests")
    print("安装完成 脚本退出 请重新执行")
    exit(0)

class Iqiyi:
    def __init__(self, check_items):
        self.check_items = check_items
        check_items = self.check_items[0]
        if 'iqy_ck' not in check_items:
            print("未填写cookie 青龙可在配置文件中设置 iqy_ck")
            exit(0)
        iqy_ck = check_items.get('iqy_ck')
        p00001, p00002, p00003, dfp, qyid = self.parse_cookie(iqy_ck)
        self.ck = p00001
        try:
            user_info = json.loads(unquote(p00002, encoding="utf-8"))
            self.user_name = user_info.get("user_name")
            self.user_name = self.user_name.replace(self.user_name[3:7], "****")
            self.nick_name = user_info.get("nickname")
        except Exception as e:
            print(f"获取账号信息失败，错误信息: {e}")
            self.user_name = "未获取到用户名，请检查 Cookie 中 P00002 字段"
            self.nick_name = "未获取到昵称，请检查 Cookie 中 P00002 字段"
        self.uid = p00003
        self.dfp = dfp
        self.qyid = qyid

        if 'sleep_await' in check_items:
            self.sleep_await = int(check_items.get("sleep_await"))
        else:
            self.sleep_await = 1

        self.session = Session()
        self.user_agent = UserAgent().chrome
        self.headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/json"
        }
        self.msg = ""

    @staticmethod
    def parse_cookie(cookie):
        p00001 = (
            re.findall(r"P00001=(.*?);", cookie)[0]
            if re.findall(r"P00001=(.*?);", cookie)
            else ""
        )
        p00002 = (
            re.findall(r"P00002=(.*?);", cookie)[0]
            if re.findall(r"P00002=(.*?);", cookie)
            else ""
        )
        p00003 = (
            re.findall(r"P00003=(.*?);", cookie)[0]
            if re.findall(r"P00003=(.*?);", cookie)
            else ""
        )
        __dfp = (
            re.findall(r"__dfp=(.*?);", cookie)[0]
            if re.findall(r"__dfp=(.*?);", cookie)
            else ""
        )
        __dfp = __dfp.split("@")[0]
        qyid = (
            re.findall(r"QC005=(.*?);", cookie)[0]
            if re.findall(r"QC005=(.*?);", cookie)
            else ""
        )
        return p00001, p00002, p00003, __dfp, qyid

    """工具"""
    def req(self, url, req_method="GET", params=None, body=None):
        data = {}
        if req_method.upper() == "GET":
            try:
                data = self.session.get(url, headers=self.headers, params=params).json()
            except:
                self.print_now("请求发送失败,可能为网络异常")
            #     data = self.session.get(url, headers=self.headers, params=body).text
            return data
        elif req_method.upper() == "POST":
            try:
                data = self.session.post(url, headers=self.headers, params=params, data=json.dumps(body)).json()
            except:
                self.print_now("请求发送失败,可能为网络异常")
            #     data = self.session.post(url, headers=self.headers, data=dumps(body)).text
            return data
        elif req_method.upper() == "OTHER":
            try:
                self.session.get(url, headers=self.headers, params=params)
            except:
                self.print_now("请求发送失败,可能为网络异常")
        else:
            self.print_now("您当前使用的请求方式有误,请检查")

    def timestamp(self, short=False):
        if (short):
            return int(time.time())
        return int(time.time() * 1000)

    def md5(self, str):
        m = md5Encode(str.encode(encoding='utf-8'))
        return m.hexdigest()

    def uuid(self, num, upper=False):
        str = ''
        if upper:
            for i in range(num):
                str += choice(digits + ascii_lowercase + ascii_uppercase)
        else:
            for i in range(num):
                str += choice(digits + ascii_lowercase)
        return str

    def print_now(self, content):
        print(content)
        stdout.flush()

    """账号信息查询"""
    def get_userinfo(self):
        msg = ' * 账号信息'
        url = "http://serv.vip.iqiyi.com/vipgrowth/query.action"
        params = {"P00001": self.ck}
        try:
            res = self.req(url, "get", params)
            if "A00000" == res["code"]:
                try:
                    res_data = res.get("data", {})
                    level = res_data.get("level", 0)
                    growthvalue = res_data.get("growthvalue", 0)
                    distance = res_data.get("distance", 0)
                    deadline = res_data.get("deadline", "非 VIP 用户")
                    today_growth_value = res_data.get("todayGrowthValue", 0)
                    msg += "\n\tVIP等级" + str(level)
                    msg += "\n\t当前成长值" + str(growthvalue)
                    msg += "\n\t今日获得成长值" + str(today_growth_value)
                    msg += "\n\t升级还需成长值" + str(distance)
                    msg += "\n\tVIP到期日期" + str(deadline)
                except Exception as e:
                    msg += "\n账号信息获取失败," + str(e)
            else:
                msg += "\n账号信息获取失败," + res.get("msg")
        except Exception as e:
            msg += "\n账号信息获取失败," + str(e)
        self.print_now(msg)
        return msg

    # 获取观影时长
    def getWatchTime(self):
        url = "https://tc.vip.iqiyi.com/growthAgency/watch-film-duration"
        try:
            data = self.req(url)
            watch_time = data['data']['viewtime']['time']
            return [True, str(watch_time)]
        except:
            log = "请求getWatchTime api失败 最大可能是cookie失效了 也可能是网络问题"
            self.print_now(log)
        return [False, log]

    def k(self, secret_key, data, split="|"):
        result_string = split.join(f"{key}={data[key]}" for key in sorted(data))
        return md5Encode((result_string + split + secret_key).encode("utf-8")).hexdigest()

    # def checkInStatus(self):
    #     msg = ''
    #     time_stamp = self.timestamp()
    #     if self.uid == "":
    #         msg += "获取签到状态失败 可能为cookie设置错误或者网络异常,请重试或者检查cookie"
    #         self.print_now(msg)
    #         return [-1, msg]
    #     task_code = 'natural_month_sign_status'
    #     data = f'agentType=1|agentversion=1.0|appKey=basic_pcw|authCookie={self.ck}|qyid={self.qyid}|task_code={task_code}|timestamp={time_stamp}|typeCode=point|userId={self.uid}|UKobMjDMsDoScuWOfp6F'
    #     url = f'https://community.iqiyi.com/openApi/task/execute?agentType=1&agentversion=1.0&appKey=basic_pcw&authCookie={self.ck}&qyid={self.qyid}&task_code={task_code}&timestamp={time_stamp}&typeCode=point&userId={self.uid}&sign={self.md5(data)}'
    #     body = {
    #         task_code: {
    #             "agentType": 1,
    #             "agentversion": 1,
    #             "authCookie": self.ck,
    #             "qyid": self.qyid,
    #             "verticalCode": "iQIYI",
    #             "taskCode": "iQIYI_mofhr"
    #         }
    #     }
    #     try:
    #         res = self.req(url, "post", body)
    #         if res.get('code') == 'A00000':
    #             res_data = res.get('data')
    #             if res_data.get('code') == 'A000' or res_data.get('success'):
    #                 self.print_now(f"签到成功, {res_data['msg']}")
    #                 msg += "获取签到状态成功"
    #                 if res_data['data'].get('todaySign') == True:
    #                     msg += ',今日已签到'
    #                     msg += ',已累计签到' + str(res_data['data'].get('cumulateSignDays')) + '天'
    #                     return [1, msg]
    #                 msg += ',已累计签到' + str(res_data['data'].get('cumulateSignDays')) + '天'
    #                 return [0, msg]
    #         msg += "获取签到状态失败，原因可能是签到接口又又又又改了"
    #         self.print_now(msg)
    #     except:
    #         msg += "获取签到状态失败，原因可能是签到接口又又又又改了"
    #         self.print_now(msg)
    #     return [-2, msg]

    def checkInSign(self):
        msg = ''
        time_stamp = self.timestamp()
        if self.uid == "":
            msg = " * 获取用户id失败 可能为cookie设置错误或者网络异常,请重试或者检查cookie"
            self.print_now(msg)
            return [False, msg]

        try:
            sign_data = {
                "agenttype": 20,
                "agentversion": "15.4.6",
                "appKey": "lequ_rn",
                "appver": "15.4.6",
                "authCookie": self.ck,
                "qyid": self.qyid,
                "srcplatform": 20,
                "task_code": "natural_month_sign",
                "timestamp": time_stamp,
                "userId": self.uid,
            }
            sign = self.k("cRcFakm9KSPSjFEufg3W", sign_data)
            sign_data["sign"] = sign
            data = {
                "natural_month_sign": {
                    "verticalCode": "iQIYI",
                    "taskCode": "iQIYI_mofhr",
                    "authCookie": self.ck,
                    "qyid": self.qyid,
                    "agentType": 20,
                    "agentVersion": "15.4.6",
                    "dfp": self.dfp,
                    "signFrom": 1,
                }
            }
            url = "https://community.iqiyi.com/openApi/task/execute"
            res = self.req(url, "post", sign_data, data)
            if res.get('code') == 'A00000':
                res_data = res.get('data')
                if res_data.get('code') == 'A000' or res_data.get('success'):
                    self.print_now(f"签到成功, {res_data['msg']}")
                    res_data_data = res_data['data']
                    msg += "签到成功"
                    if res_data['msg']:
                        msg += ",签到天数" + res_data['msg']
                    else:
                        try:
                            msg += ",签到天数" + res_data_data['signDays']
                        except Exception as e:
                            msg += ",签到天数" + str(e)

                    for reward in res_data_data.get('rewards'):
                        if reward.get('rewardType') == 1:
                            msg += ",获取" + str(reward.get('rewardCount')) + '点成长值'
                            break
                    return [True, msg]
                else:
                    if res_data.get('code') == 'A0014':
                        msg += "今日已签到"
                        return [True, msg]
                    else:
                        msg += "签到失败," + res_data.get("msg")
            else:
                msg += "签到失败," + res.get("message")
            self.print_now(msg)
        except Exception as e:
            msg += "签到失败," + str(e)
            self.print_now(msg)
        return [False, msg]

    # 签到
    def checkIn(self):
        msg = ' * 会员签到'
        # 获取签到状态
        # resCheckInStatus = self.checkInStatus()
        # msg += resCheckInStatus[1]
        # if resCheckInStatus[0] < 0:
        #     return [False, msg]
        # elif 1 == resCheckInStatus[0]:
        #     return [True, msg]

        # 执行签到
        resCheckInSign = self.checkInSign()
        msg += '\n\t' + resCheckInSign[1]
        return [resCheckInSign[0], msg]

    def give_times(self, p00001):
        url = "https://pcell.iqiyi.com/lotto/giveTimes"
        times_code_list = ["browseWeb", "browseWeb", "bookingMovie"]
        for times_code in times_code_list:
            params = {
                "actCode": "bcf9d354bc9f677c",
                "timesCode": times_code,
                "P00001": p00001,
            }
            res = self.req(url, "get", params=params)
            print(res)

    def lotto_lottery(self):
        msg = ' * 抽奖'
        self.give_times(p00001=self.ck)
        gift_list = []
        for _ in range(5):
            url = "https://pcell.iqiyi.com/lotto/lottery"
            params = {"actCode": "bcf9d354bc9f677c", "P00001": self.ck}
            res = self.req(url, "get", params=params)
            gift_name = res["data"]["giftName"]
            if gift_name and "未中奖" not in gift_name:
                gift_list.append(gift_name)
        if gift_list:
            msg += "\n\t白金抽奖:" + "、".join(gift_list)
        else:
            msg += "\n\t白金抽奖未中奖"
        return msg

    def dailyTask(self):
        msg = ''
        taskCodeList = {
            'b6e688905d4e7184': "浏览生活福利",
            'a7f02e895ccbf416': "看看热b榜",
            '8ba31f70013989a8': "每日观影成就",
            "freeGetVip": "浏览会员兑换活动",
            "GetReward": "逛领福利频道"
        }
        for taskCode in taskCodeList:
            msg += f' * 日常任务-{taskCodeList[taskCode]}:\n\t'
            try:
                # 领任务
                url = f'https://tc.vip.iqiyi.com/taskCenter/task/joinTask?P00001={self.ck}&taskCode={taskCode}&platform=b6c13e26323c537d&lang=zh_CN&app_lm=cn'
                if self.req(url)['code'] == 'A00000':
                    msg += f'领取成功'
                    time.sleep(10)
                else:
                    msg += f'领取失败' + '\n'
                    continue
                # 完成任务
                url = f'https://tc.vip.iqiyi.com/taskCenter/task/notify?taskCode={taskCode}&P00001={self.ck}&platform=97ae2982356f69d8&lang=cn&bizSource=component_browse_timing_tasks&_={self.timestamp()}'
                if self.req(url)['code'] == 'A00000':
                    msg += f',完成成功'
                    time.sleep(2)
                else:
                    msg += f',完成失败' + '\n'
                    continue
                # 领取奖励
                url = f"https://tc.vip.iqiyi.com/taskCenter/task/getTaskRewards?P00001={self.ck}&taskCode={taskCode}&lang=zh_CN&platform=b2f2d9af351b8603"
                price = self.req(url)['dataNew'][0]["value"]
                self.print_now(f"领取{taskCodeList[taskCode]}任务奖励成功, 获得{price}点成长值")
                msg += f",获得{price}点成长值" + '\n'
            except:
                self.print_now(f"领取{taskCodeList[taskCode]}任务奖励可能出错了 也可能没出错 只是你今天跑了第二次")
                msg += f",任务奖励可能出错了 也可能没出错 只是你今天跑了第二次" + '\n'
            time.sleep(5)
        return msg

    def lottery_draw(self, lottery=True):
        msg = ' * '
        """
        查询剩余抽奖次数和抽奖
        True 抽
        False 查
        """
        url = "https://iface2.iqiyi.com/aggregate/3.0/lottery_activity"
        lottery_params = {
            "app_k": "0",
            "app_v": "0",
            "platform_id": 10,
            "dev_os": "2.0.0",
            "dev_ua": "COL-AL10",
            "net_sts": 1,
            "qyid": self.qyid,
            "psp_uid": self.uid,
            "psp_cki": self.ck,
            "psp_status": 3,
            "secure_v": 1,
            "secure_p": "0",
            "req_sn": self.timestamp()
        }
        params = lottery_params
        try:
            data = self.req(url, "get", params)
            if data.get("code") == 0:
                msg += f'抽奖成功, 获得{data["awardName"]}'
                self.print_now(msg)
                return [data["daysurpluschance"], msg]
            elif data.get("code") == 3:
                msg += '抽奖成功, 但是获得奖励信息错误, 大概率是没用的开通会员优惠券'
                self.print_now(msg)
                return [data["daysurpluschance"], msg]
            else:
                msg += "抽奖结束"
                self.print_now(msg)
                return [0, msg]
        except:
            msg += "抽奖失败"
            self.print_now(msg)
            return [0, msg]

    def getUrl(self, time, dfp):
        return f'https://msg.qy.net/b?u=f600a23f03c26507f5482e6828cfc6c5&pu={self.uid}&p1=1_10_101&v=5.2.66&ce={self.uuid(32)}&de=1616773143.1639632721.1639653680.29&c1=2&ve={self.uuid(32)}&ht=0&pt={randint(1000000000, 9999999999) / 1000000}&isdm=0&duby=0&ra=5&clt=&ps2=DIRECT&ps3=&ps4=&br=mozilla%2F5.0%20(windows%20nt%2010.0%3B%20win64%3B%20x64)%20applewebkit%2F537.36%20(khtml%2C%20like%20gecko)%20chrome%2F96.0.4664.110%20safari%2F537.36&mod=cn_s&purl=https%3A%2F%2Fwww.iqiyi.com%2Fv_1eldg8u3r08.html%3Fvfrm%3Dpcw_home%26vfrmblk%3D712211_cainizaizhui%26vfrmrst%3D712211_cainizaizhui_image1%26r_area%3Drec_you_like%26r_source%3D62%2540128%26bkt%3DMBA_PW_T3_53%26e%3Db3ec4e6c74812510c7719f7ecc8fbb0f%26stype%3D2&tmplt=2&ptid=01010031010000000000&os=window&nu=0&vfm=&coop=&ispre=0&videotp=0&drm=&plyrv=&rfr=https%3A%2F%2Fwww.iqiyi.com%2F&fatherid={randint(1000000000000000, 9999999999999999)}&stauto=1&algot=abr_v12-rl&vvfrom=&vfrmtp=1&pagev=playpage_adv_xb&engt=2&ldt=1&krv=1.1.85&wtmk=0&duration={randint(1000000, 9999999)}&bkt=&e=&stype=&r_area=&r_source=&s4={randint(100000, 999999)}_dianshiju_tbrb_image2&abtest=1707_B%2C1550_B&s3={randint(100000, 999999)}_dianshiju_tbrb&vbr={randint(100000, 999999)}&mft=0&ra1=2&wint=3&s2=pcw_home&bw=10&ntwk=18&dl={randint(10, 999)}.27999999999997&rn=0.{randint(1000000000000000, 9999999999999999)}&dfp={dfp}&stime={self.timestamp()}&r={randint(1000000000000000, 9999999999999999)}&hu=1&t=2&tm={time}&_={self.timestamp()}'

    def start(self):
        self.print_now("正在执行刷观影时长脚本 为减少风控 本过程运行时间较长 大概半个小时")
        resWatchTime = self.getWatchTime()
        if not resWatchTime[0]:
            return resWatchTime
        totalTime = int(resWatchTime[1])
        if totalTime >= 7200:
            log = f" * 你的账号今日观影时长大于2小时 不执行刷观影时长"
            self.print_now(log)
            return [False, log]
        for i in range(150):
            Time = randint(60, 120)
            url = self.getUrl(Time, self.dfp)
            self.req(url, 'other')
            totalTime += Time
            time.sleep(randint(20, 40))
            if i % 20 == 3:
                self.print_now(f"观影时长现在已经刷到了{totalTime}秒, 数据同步有延迟, 仅供参考")
            if totalTime >= 7600:
                break
        return [True, f" * 观影时长现在已经刷到了{totalTime}秒, 数据同步有延迟, 仅供参考"]

    def main(self):
        time_now = time.localtime(int(time.time()))
        now = time.strftime("%Y-%m-%d %H:%M:%S", time_now)
        msg = "VIP会员签到任务\n" + now + '\n'

        # 刷观影时长
        resStart = self.start()
        if not resStart[0]:
            msg += resStart[1] + '\n'
        else:
            msg += resStart[1] + '\n'

        # 抽奖
        for i in range(10):
            resLottery = self.lottery_draw()
            if int(resLottery[0]) == 0:
                break
            msg += resLottery[1] + '\n'
            time.sleep(3)

        # 签到
        resCheckIn = self.checkIn()
        if not resCheckIn[0]:
            msg += resCheckIn[1] + '\n'
        else:
            msg += resCheckIn[1] + '\n'

        # 抽奖
        msg += self.lotto_lottery() + '\n'

        # 完成日常任务
        msg += self.dailyTask()

        # self.print_now(f"任务已经执行完成, 因爱奇艺观影时间同步较慢,这里等待3分钟再查询今日成长值信息,若不需要等待直接查询,请设置环境变量名 sleep_await = 0 默认为等待")
        if int(self.sleep_await) == 1:
            time.sleep(180)

        # 获取用户信息
        msg += self.get_userinfo()

        return msg

if __name__ == '__main__':
    data = get_data()
    _check_items = data.get("IQIYI_NEW", [])
    if len(_check_items) < 1:
        send("爱奇艺", "IQIYI_NEW配置错误")
        exit(0)
    result = Iqiyi(check_items=_check_items).main()
    send("爱奇艺", result)