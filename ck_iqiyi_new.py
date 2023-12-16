#!/usr/bin/python3
# -- coding: utf-8 --
# cron "30 7,10 * * *" script-path=xxx.py,tag=匹配cron用
# new Env('爱奇艺签到加刷时长')

"""
#变量 爱奇艺 iqy_ck  iqiyi_dfp 放在青龙config.sh里面或者在青龙变量分别设置这2个参数 此脚本不要瞎改
# export iqy_ck = ''
# export iqiyi_dfp = ''
"""

import time
from random import randint, choice
from json import dumps
from hashlib import md5 as md5Encode
from string import digits, ascii_lowercase, ascii_uppercase
from sys import exit, stdout
from os import system
from re import findall

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
        if "__dfp" in iqy_ck:
            iqiyi_dfp = findall(r"__dfp=(.*?)(;|$)", iqy_ck)[0][0]
            iqiyi_dfp = iqiyi_dfp.split("@")[0]
        if "P00001" in iqy_ck:
            iqy_ck = findall(r"P00001=(.*?)(;|$)", iqy_ck)[0][0]
        if 'iqiyi_dfp' in check_items:
            iqiyi_dfp = check_items.get('iqiyi_dfp')
        else:
            iqiyi_dfp = "a1a7d52af83b304b908ebf41bd819df745221e9419b36b112537fd117235d7df95"
        if 'sleep_await' in check_items:
            sleep_await = int(check_items.get("sleep_await"))
        else:
            sleep_await = 1
        if 'get_iqiyi_dfp' in check_items:
            self.get_iqiyi_dfp = check_items.get('get_iqiyi_dfp')
        else:
            self.get_iqiyi_dfp = 0

        self.ck = iqy_ck
        self.session = Session()
        self.user_agent = UserAgent().chrome
        self.headers = {
            "User-Agent": self.user_agent,
            "Cookie": f"P00001={self.ck}",
            "Content-Type": "application/json"
        }
        self.dfp = iqiyi_dfp
        self.uid = ""
        self.msg = ""
        self.user_info = ""
        self.sleep_await = sleep_await

    """工具"""

    def req(self, url, req_method="GET", body=None):
        data = {}
        if req_method.upper() == "GET":
            try:
                data = self.session.get(url, headers=self.headers, params=body).json()
            except:
                self.print_now("请求发送失败,可能为网络异常")
            #     data = self.session.get(url, headers=self.headers, params=body).text
            return data
        elif req_method.upper() == "POST":
            try:
                data = self.session.post(url, headers=self.headers, data=dumps(body)).json()
            except:
                self.print_now("请求发送失败,可能为网络异常")
            #     data = self.session.post(url, headers=self.headers, data=dumps(body)).text
            return data
        elif req_method.upper() == "OTHER":
            try:
                self.session.get(url, headers=self.headers, params=dumps(body))
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

    def get_dfp_params(self):
        get_params_url = "https://api.lomoruirui.com/iqiyi/get_dfp"
        data = get(get_params_url).json()
        return data

    def get_dfp(self):
        body = self.get_dfp_params()
        url = "https://cook.iqiyi.com/security/dfp_pcw/sign"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Length": "1059",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "cook.iqiyi.com",
            "Origin": "https://www.iqiyi.com",
            "Pragma": "no-cache",
            "Referer": "https://www.iqiyi.com/",
            "sec-ch-ua": f"\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"{body['data']['sv']}\", \"Google Chrome\";v=\"{body['data']['sv']}\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": self.user_agent
        }
        try:
            data = post(url, headers=headers, data=body["data"]["body"]).json()
            self.dfp = data["result"]["dfp"]
            return [True, self.dfp]
        except:
            log = "请求get_dfp api失败 最大可能是cookie失效了 也可能是网络问题"
            self.print_now(log)
        return [False, log]

    def get_userinfo(self):
        url = f"https://tc.vip.iqiyi.com/growthAgency/v2/growth-aggregation?messageId={self.qyid}&platform=97ae2982356f69d8&P00001={self.ck}&responseNodes=duration%2Cgrowth%2Cupgrade%2CviewTime%2CgrowthAnnualCard&_={self.timestamp()}"
        data = self.req(url)
        msg = data['data']['growth']
        try:
            self.user_info = f"查询成功: 到期时间{msg['deadline']}\t当前等级为{msg['level']}\n\t今日获得成长值{msg['todayGrowthValue']}\t总成长值{msg['growthvalue']}\t距离下一等级还差{msg['distance']}成长值"
            self.print_now(self.user_info)
        except:
            self.user_info = f"查询失败,未获取到用户信息"
        return self.user_info + '\n'

    """获取用户id"""
    def getUid(self):
        success = False
        log = ''
        url = f'https://passport.iqiyi.com/apis/user/info.action?authcookie={self.ck}&fields=userinfo%2Cqiyi_vip&timeout=15000'
        try:
            data = self.req(url)
            if data.get("code") == 'A00000':
                self.uid = data['data']['userinfo']['pru']
                success = True
            else:
                log = "请求getUid api失败 最大可能是cookie失效了 也可能是网络问题"
                self.print_now(log)
        except:
            log = "请求getUid api失败 最大可能是cookie失效了 也可能是网络问题"
            self.print_now(log)
        return [success, log]

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

    # 获取签名URL
    def getSignUrl(self):
        self.qyid = self.md5(self.uuid(16))
        time_stamp = self.timestamp()
        if self.uid == "":
            log = "获取用户id失败 可能为cookie设置错误或者网络异常,请重试或者检查cookie"
            self.print_now(log)
            return [False, log]
        data = f'agentType=1|agentversion=1|appKey=basic_pcw|authCookie={self.ck}|qyid={self.qyid}|task_code=natural_month_sign|timestamp={time_stamp}|typeCode=point|userId={self.uid}|UKobMjDMsDoScuWOfp6F'
        url = f'https://community.iqiyi.com/openApi/task/execute?agentType=1&agentversion=1&appKey=basic_pcw&authCookie={self.ck}&qyid={self.qyid}&sign={self.md5(data)}&task_code=natural_month_sign&timestamp={time_stamp}&typeCode=point&userId={self.uid}'
        return [True, url]

    def getUrl(self, time, dfp):
        return f'https://msg.qy.net/b?u=f600a23f03c26507f5482e6828cfc6c5&pu={self.uid}&p1=1_10_101&v=5.2.66&ce={self.uuid(32)}&de=1616773143.1639632721.1639653680.29&c1=2&ve={self.uuid(32)}&ht=0&pt={randint(1000000000, 9999999999) / 1000000}&isdm=0&duby=0&ra=5&clt=&ps2=DIRECT&ps3=&ps4=&br=mozilla%2F5.0%20(windows%20nt%2010.0%3B%20win64%3B%20x64)%20applewebkit%2F537.36%20(khtml%2C%20like%20gecko)%20chrome%2F96.0.4664.110%20safari%2F537.36&mod=cn_s&purl=https%3A%2F%2Fwww.iqiyi.com%2Fv_1eldg8u3r08.html%3Fvfrm%3Dpcw_home%26vfrmblk%3D712211_cainizaizhui%26vfrmrst%3D712211_cainizaizhui_image1%26r_area%3Drec_you_like%26r_source%3D62%2540128%26bkt%3DMBA_PW_T3_53%26e%3Db3ec4e6c74812510c7719f7ecc8fbb0f%26stype%3D2&tmplt=2&ptid=01010031010000000000&os=window&nu=0&vfm=&coop=&ispre=0&videotp=0&drm=&plyrv=&rfr=https%3A%2F%2Fwww.iqiyi.com%2F&fatherid={randint(1000000000000000, 9999999999999999)}&stauto=1&algot=abr_v12-rl&vvfrom=&vfrmtp=1&pagev=playpage_adv_xb&engt=2&ldt=1&krv=1.1.85&wtmk=0&duration={randint(1000000, 9999999)}&bkt=&e=&stype=&r_area=&r_source=&s4={randint(100000, 999999)}_dianshiju_tbrb_image2&abtest=1707_B%2C1550_B&s3={randint(100000, 999999)}_dianshiju_tbrb&vbr={randint(100000, 999999)}&mft=0&ra1=2&wint=3&s2=pcw_home&bw=10&ntwk=18&dl={randint(10, 999)}.27999999999997&rn=0.{randint(1000000000000000, 9999999999999999)}&dfp={dfp}&stime={self.timestamp()}&r={randint(1000000000000000, 9999999999999999)}&hu=1&t=2&tm={time}&_={self.timestamp()}'

    # 签到
    def checkIn(self):
        url = self.getSignUrl()
        body = {
            "natural_month_sign": {
                "taskCode": "iQIYI_mofhr",
                "agentType": 1,
                "agentversion": 1,
                "authCookie": self.ck,
                "qyid": self.qyid,
                "verticalCode": "iQIYI"
            }
        }
        try:
            data = self.req(url, "post", body)
            if data.get('code') == 'A00000':
                self.print_now(f"签到执行成功, {data['data']['msg']}")
                return [True, "签到执行成功"]
            else:
                log = "签到失败，原因可能是签到接口又又又又改了"
                self.print_now(log)
        except:
            log = "签到失败，原因可能是签到接口又又又又改了"
            self.print_now(log)
        return [False, log]

    def dailyTask(self):
        log = ''
        taskCodeList = {
            'b6e688905d4e7184': "浏览生活福利",
            'a7f02e895ccbf416': "看看热b榜",
            '8ba31f70013989a8': "每日观影成就",
            "freeGetVip": "浏览会员兑换活动",
            "GetReward": "逛领福利频道"
        }
        for taskCode in taskCodeList:
            # 领任务
            url = f'https://tc.vip.iqiyi.com/taskCenter/task/joinTask?P00001={self.ck}&taskCode={taskCode}&platform=b6c13e26323c537d&lang=zh_CN&app_lm=cn'
            if self.req(url)['code'] == 'A00000':
                log += f'领取{taskCodeList[taskCode]}任务成功'
                time.sleep(10)
            else:
                log += f'领取{taskCodeList[taskCode]}任务失败' + '\n'
                continue
            # 完成任务
            url = f'https://tc.vip.iqiyi.com/taskCenter/task/notify?taskCode={taskCode}&P00001={self.ck}&platform=97ae2982356f69d8&lang=cn&bizSource=component_browse_timing_tasks&_={self.timestamp()}'
            if self.req(url)['code'] == 'A00000':
                log += f',完成{taskCodeList[taskCode]}任务成功'
                time.sleep(2)
            else:
                log += f',完成{taskCodeList[taskCode]}任务失败' + '\n'
                continue
            # 领取奖励
            # url = f'https://tc.vip.iqiyi.com/taskCenter/task/getTaskRewards?P00001={self.ck}&taskCode={taskcode}&dfp={self.dfp}&platform=b6c13e26323c537d&lang=zh_CN&app_lm=cn&deviceID={self.md5(self.uuid(8))}&token=&multiReward=1&fv=bed99b2cf5722bfe'
            url = f"https://tc.vip.iqiyi.com/taskCenter/task/getTaskRewards?P00001={self.ck}&taskCode={taskCode}&lang=zh_CN&platform=b2f2d9af351b8603"
            try:
                price = self.req(url)['dataNew'][0]["value"]
                self.print_now(f"领取{taskCodeList[taskCode]}任务奖励成功, 获得{price}点成长值")
                log += f",获得{price}点成长值" + '\n'
            except:
                self.print_now(f"领取{taskCodeList[taskCode]}任务奖励可能出错了 也可能没出错 只是你今天跑了第二次")
                log += f",任务奖励可能出错了 也可能没出错 只是你今天跑了第二次" + '\n'
            time.sleep(5)
        return log

    def lottery_draw(self, lottery=True):
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
                log = f'抽奖成功, 获得{data["awardName"]}'
                self.print_now(log)
                return [data["daysurpluschance"], log]
            elif data.get("code") == 3:
                log = '抽奖成功, 但是获得奖励信息错误, 大概率是没用的开通会员优惠券'
                self.print_now(log)
                return [data["daysurpluschance"], log]
            else:
                self.print_now("抽奖结束")
                return [0, "抽奖结束"]
        except:
            self.print_now("抽奖失败")
            return [0, "抽奖失败"]

    def start(self):
        self.print_now("正在执行刷观影时长脚本 为减少风控 本过程运行时间较长 大概半个小时")
        resWatchTime = self.getWatchTime()
        if not resWatchTime[0]:
            return resWatchTime
        totalTime = int(resWatchTime[1])
        if totalTime >= 7200:
            log = f"你的账号今日观影时长大于2小时 不执行刷观影时长"
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
        return [True, f"观影时长现在已经刷到了{totalTime}秒, 数据同步有延迟, 仅供参考"]

    def main(self):
        time_now = time.localtime(int(time.time()))
        now = time.strftime("%Y-%m-%d %H:%M:%S", time_now)
        log = "VIP会员签到任务\n" + now + '\n'

        if 1 == self.get_iqiyi_dfp:
            resDfp = self.get_dfp()
            if not resDfp[0]:
                return log + resDfp[1]
        # 获取用户uid
        resUid = self.getUid()
        if not resUid[0]:
            return log + resUid[1]
        log += resUid[1] + '\n'

        # 检查签名url
        resSignUrl = self.getSignUrl()
        if not resSignUrl[0]:
            return log + resSignUrl[1]

        # 刷观影时长
        resStart = self.start()
        if not resStart[0]:
            log += resStart[1] + '\n'
        else:
            log += resStart[1] + '\n'

        # 抽奖
        for i in range(10):
            resLottery = self.lottery_draw()
            if int(resLottery[0]) == 0:
                break
            log += resLottery[1] + '\n'
            time.sleep(3)

        # 签到
        resCheckIn = self.checkIn()
        if not resCheckIn[0]:
            log += resCheckIn[1] + '\n'
        else:
            log += resCheckIn[1] + '\n'

        # 完成日常任务
        log += self.dailyTask()

        self.print_now(f"任务已经执行完成, 因爱奇艺观影时间同步较慢,这里等待3分钟再查询今日成长值信息,若不需要等待直接查询,请设置环境变量名 sleep_await = 0 默认为等待")
        if int(self.sleep_await) == 1:
            time.sleep(180)

        # 获取用户信息
        log += self.get_userinfo()

        return log

if __name__ == '__main__':
    data = get_data()
    _check_items = data.get("IQIYI_NEW", [])
    if len(_check_items) < 1:
        send("爱奇艺", "IQIYI_NEW配置错误")
        exit(0)
    result = Iqiyi(check_items=_check_items).main()
    send("爱奇艺", result)