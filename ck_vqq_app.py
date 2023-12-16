# -*- coding: utf-8 -*-
"""
cron: 55 10 * * *
new Env('腾讯视频APP');
"""

import requests
import requests.utils
import time, json

from notify_mtr import send
from utils import get_data

class VQQ:
    def __init__(self, check_items):
        self.check_items = check_items

    def tx_videoApp_cookie(self, qimei36, appid, openid, access_token, vuserid, login, ip):
        cookie = 'vdevice_qimei36=' + qimei36 + ';vqq_appid=' + appid + ';vqq_openid=' + openid \
                 + ';vqq_access_token=' + access_token + ';main_login=' + login + ';vqq_vuserid=' + vuserid \
                 + ';ip=' + ip
        return cookie

    def tx_videoApp_checkInIsDone(self, cookie):
        isDone = -1
        log = ''
        # 任务状态
        url_taskList = 'https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/ReadTaskList?rpc_data=%7B%22business_id%22:%221%22,%22platform%22:3%7D'
        headers_taskList = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; M2104K10AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046237 Mobile Safari/537.36 QQLiveBrowser/8.7.85.27058',
            'Content-Type': 'application/json',
            'referer': 'https://film.video.qq.com/x/vip-center/?entry=common&hidetitlebar=1&aid=V0%24%241%3A0%242%3A8%243%3A8.7.85.27058%244%3A3%245%3A%246%3A%247%3A%248%3A4%249%3A%2410%3A&isDarkMode=0',
            'cookie': cookie
        }
        response_taskList = requests.get(url_taskList, headers=headers_taskList)
        try:
            res_taskList = json.loads(response_taskList.text)
            taskList = res_taskList["task_list"]
            for task in taskList:
                if 101 == task["task_id"]:
                    # VIP会员签到任务
                    isDone = 0
                    if 1 == task["task_status"]:
                        # 已完成
                        isDone = 1
                        log = log + '\n标题:' + task["task_maintitle"] + '\n状态:' + task["task_subtitle"]
                else:
                    continue
                return [isDone, log]
        except:
            log = log + "获取状态异常，可能是cookie失效"
        return [isDone, log]

    def tx_videoApp_checkIn(self, cookie):
        success = False
        log = ''
        url_checkIn = 'https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/CheckIn?rpc_data=%7B%7D'
        headers_checkIn = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; M2104K10AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046237 Mobile Safari/537.36 QQLiveBrowser/8.7.85.27058',
            'Content-Type': 'application/json',
            'referer': 'https://film.video.qq.com/x/vip-center/?entry=common&hidetitlebar=1&aid=V0%24%241%3A0%242%3A8%243%3A8.7.85.27058%244%3A3%245%3A%246%3A%247%3A%248%3A4%249%3A%2410%3A&isDarkMode=0',
            'cookie': cookie
        }
        response_checkIn = requests.get(url_checkIn, headers=headers_checkIn)
        try:
            res_checkIn = json.loads(response_checkIn.text)
            log = log + "\n签到获得v力值:" + str(res_checkIn['check_in_score'])
            success = True
        except:
            try:
                res_1 = json.loads(response_checkIn.text)
                log = log + "\n腾讯视频签到异常，返回内容：\n" + str(res_1)
            except:
                log = log + "\n腾讯视频签到异常，无法返回内容"
        return [success, log]

    def tx_videoApp_jifen(self, cookie):
        success = False
        log = ''
        url_jifen = 'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_vscore_user_mashup&cmd=&otype=xjson&type=1'
        headers_jifen = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; M2104K10AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046237 Mobile Safari/537.36 QQLiveBrowser/8.7.85.27058',
            'Content-Type': 'application/json',
            'cookie': cookie
        }
        response_jifen = requests.get(url_jifen, headers=headers_jifen)
        try:
            res_jifen = json.loads(response_jifen.text)
            log = log + "\n会员等级:" + str(res_jifen['lscore_info']['level']) + "\n积分:" + str(
                res_jifen['cscore_info']['vip_score_total']) + "\nV力值:" + str(res_jifen['lscore_info']['score'])
            success = True
        except:
            try:
                res_jifen = json.loads(response_jifen.text)
                log = log + "\n腾讯视频领获取积分异常,返回内容:\n" + str(res_jifen)
            except:
                log = log + "\n腾讯视频获取积分异常,无法返回内容"
        return [success, log]

    def tx_videoApp_userInfo(self, cookie):
        success = False
        log = ''
        url_userInfo = 'https://vip.video.qq.com/rpc/trpc.query_vipinfo.vipinfo.QueryVipInfo/GetVipUserInfoH5'
        headers_userInfo = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; M2104K10AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046237 Mobile Safari/537.36 QQLiveBrowser/8.7.85.27058',
            'Content-Type': 'text/plain;charset=UTF-8',
            'cookie': cookie
        }
        data = '{"geticon":1,"viptype":"svip|nfl","platform":8}'
        response_userInfo = requests.post(url_userInfo, data=data, headers=headers_userInfo)
        try:
            res_userInfo = json.loads(response_userInfo.text)
            log = log + "\nVIP开始时间:" + str(res_userInfo['beginTime']) + "\nVIP到期时间:" + str(
                res_userInfo['endTime'])
            if res_userInfo['endmsg'] != '':
                log = log + '\nendmsg:' + res_userInfo['endmsg']
            success = True
        except:
            try:
                res_3 = json.loads(response_userInfo.text)
                log = log + "\n腾讯视频领获取用户信息异常,返回内容:\n" + str(res_3)
            except:
                log = log + "\n腾讯视频获取用户信息异常,无法返回内容"
        return [success, log]

    def tx_videoApp(self, qimei36, appid, openid, access_token, vuserid, login, ip):
        cookie = self.tx_videoApp_cookie(qimei36, appid, openid, access_token, vuserid, login, ip)

        time_now = time.localtime(int(time.time()))
        now = time.strftime("%Y-%m-%d %H:%M:%S", time_now)
        log = "腾讯视频会员签到执行任务\n" + now

        res_checkInIsDone = self.tx_videoApp_checkInIsDone(cookie)
        if -1 == res_checkInIsDone[0]:
            return log + res_checkInIsDone[1]
        elif 0 == res_checkInIsDone[0]:
            # 签到
            res_checkIn = self.tx_videoApp_checkIn(cookie)
            if res_checkIn[0] != True:
                return log + res_checkIn[1]
            log += res_checkIn[1]
        else:
            log += res_checkInIsDone[1]

        # 用户信息查询
        res_userInfo = self.tx_videoApp_userInfo(cookie)
        if res_userInfo[0] != True:
            return log + res_userInfo[1]
        log += res_userInfo[1]

        # 积分查询
        res_jifen = self.tx_videoApp_jifen(cookie)
        if res_jifen[0] != True:
            return log + res_jifen[1]
        log += res_jifen[1]

        # 观看
        # url_2 = 'https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/ProvideAward?rpc_data=%7B%22task_id%22:1%7D'
        # headers_2 = {
        #     'user-agent': 'Mozilla/5.0 (Linux; Android 11; M2104K10AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046237 Mobile Safari/537.36 QQLiveBrowser/8.7.85.27058',
        #     'Content-Type': 'application/json',
        #     'referer': 'https://film.video.qq.com/x/vip-center/?entry=common&hidetitlebar=1&aid=V0%24%241%3A0%242%3A8%243%3A8.7.85.27058%244%3A3%245%3A%246%3A%247%3A%248%3A4%249%3A%2410%3A&isDarkMode=0',
        #     'cookie': cookie
        # }
        # response_2 = requests.get(url_2, headers=headers_2)
        # try:
        #     res_2 = json.loads(response_2.text)
        #     log = log + "\n观看获得v力值:" + str(res_2['provide_value'])
        #     print(res_2)
        # except:
        #     try:
        #         res_2 = json.loads(response_2.text)
        #         log = log + "\n腾讯视频领取观看v力值异常,返回内容:\n" + str(res_2)
        #         print(res_2)
        #     except:
        #         log = log + "\n腾讯视频领取观看v力值异常,无法返回内容"

        return log

    def tx_videoWeb(self, login_cookie, auth_cookie):
        millisecond_time = round(time.time() * 1000)
        # 替换成自己的
        login_url = "https://access.video.qq.com/user/auth_refresh?vappid=90355472&vsecret=b5a6aa567a55d84008e258a9f69bfdb8e929aa97c4c12c24&type=qq&g_tk=&g_vstk=1726529982&g_actk=2008470811"
        login_headers = {
            'Referer': 'https://v.qq.com',
            'Cookie': login_cookie
        }

        login_rsp = requests.get(url=login_url, headers=login_headers)
        print(login_rsp)
        login_rsp_cookie = requests.utils.dict_from_cookiejar(login_rsp.cookies)

        if login_rsp.status_code == 200 and login_rsp_cookie:
            auth_cookie = auth_cookie + 'vqq_vusession=' + login_rsp_cookie[
                'vqq_vusession'] + ';' + 'vqq_access_token=' + login_rsp_cookie[
                              'vqq_access_token'] + ';' + 'vqq_appid=' + login_rsp_cookie[
                              'vqq_appid'] + ';' + 'vqq_openid=' + login_rsp_cookie[
                              'vqq_openid'] + ';' + 'vqq_refresh_token=' + login_rsp_cookie[
                              'vqq_refresh_token'] + ';' + 'vqq_vuserid=' + login_rsp_cookie['vqq_vuserid'] + ';'
            print(auth_cookie)

            sign_in_url = "https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/CheckIn?rpc_data={}"
            referer = 'https://film.video.qq.com/x/grade/?ovscroll=0&ptag=Vgrade.card&source=page_id=default&ztid=default&pgid=page_personal_center&page_type=personal&is_interactive_flag=1&pg_clck_flag=1&styletype=201&mod_id=sp_mycntr_vip&sectiontype=2&business=hollywood&layouttype=1000&section_idx=0&mod_title=会员资产&blocktype=6001&vip_id=userCenter_viplevel_entry&mod_idx=11&item_idx=4&eid=button_mycntr&action_pos=jump&hidetitlebar=1&isFromJump=1&isDarkMode=1&uiType=HUGE'
            referer = referer.encode("utf-8").decode("latin1")
            sign_headers = {
                'Referer': referer,
                'Host': 'vip.video.qq.com',
                'Origin': 'https://film.video.qq.com',
                'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_2 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Mobile/11A465 QQLiveBrowser/8.8.10 AppType/HD WebKitCore/WKWebView iOS GDTTangramMobSDK/4.370.6 GDTMobSDK/4.370.6 cellPhone/Unknown iPad AppBuild/25828',
                'Accept-Encoding': 'gzip, deflate, br',
                "Cookie": auth_cookie
            }
            sign_rsp = requests.get(url=sign_in_url, headers=sign_headers)

            sign_rsp_json = sign_rsp.json()
            print(sign_rsp_json)

            rsp_ret = sign_rsp_json['ret']
            rsp_score = sign_rsp_json['check_in_score']

            msg = "本次签到结果：" + str(rsp_ret) + " 签到积分：" + str(rsp_score)
            return msg

    def main(self):
        msg_all = ""
        for i, check_item in enumerate(self.check_items, start=1):
            # login_cookie = str(check_item.get("login_cookie"))
            # auth_cookie = str(check_item.get("auth_cookie"))
            # sign_msg = self.tx_videoWeb(login_cookie, auth_cookie)
            # msg = (
            #     f"账号 {i}"
            #     + "\n------ 腾讯视频签到结果 ------\n"
            #     + sign_msg
            # )
            # msg_all += msg + "\n\n"

            vdevice_qimei36 = str(check_item.get("vdevice_qimei36"))
            vqq_appid = str(check_item.get("vqq_appid"))
            vqq_openid = str(check_item.get("vqq_openid"))
            vqq_access_token = str(check_item.get("vqq_access_token"))
            vqq_vuserid = str(check_item.get("vqq_vuserid"))
            main_login = str(check_item.get("main_login"))
            if 'ip' in check_item:
                ip = str(check_item.get("ip"))
            else:
                ip = "111.30.240.161"
            self.tx_videoApp(vdevice_qimei36, vqq_appid, vqq_openid, vqq_access_token, vqq_vuserid, main_login, ip)
        return msg_all

if __name__ == "__main__":
    data = get_data()
    _check_items = data.get("VQQ_APP", [])
    result = VQQ(check_items=_check_items).main()
    send("腾讯视频", result)
