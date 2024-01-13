#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
cron: 56 13 12 * * *
new Env('美团米粒');
"""

import datetime
import json
import time
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


class MeiTuanML:
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

    def sign(self, token, uuid, user_id, open_id):
        msg = ' * 美团米粒签到:' + '\n\t'
        self.print_now("----------美团米粒中心执行----------")
        sjtime = str(round(time.time() * 1000))

        # ui=46525309&region_id=1000110100&region_version=1699672616801&yodaReady=wx&csecappid=wx2c348cf579062e56&csecplatform=3&csecversionname=9.37.6&csecversion=1.4.0
        wm_visitid = '150a2515-5784-4be9-b019-5bf2a211ee8b'

        urlSignInTask = "https://wx.waimai.meituan.com/mtandroid_wmgroup/v1/wlwc/signintask/signin?ui=46525309&region_id=1000110100&region_version=1699672616801"
        resSignInTask = f"wm_dtype=iPhone%20XR&wm_dversion=8.0.43&wm_dplatform=ios&wm_uuid={uuid}&wm_visitid={wm_visitid}&wm_appversion=9.37.6&wm_logintoken={token}&userToken={token}&req_time={sjtime}&waimai_sign=%2F&userid={user_id}&user_id={user_id}&lch=1027&sessionId=RYY9AA&province=%E9%95%BF%E6%B2%99&nickName=yczcc&gender=0&country=%E4%B8%AD%E5%9B%BD&city=%E9%95%BF%E6%B2%99&vatarUrl=https%3A%2F%2Fimg.meituan.net%2Fkangaroox%2F3a057d48536606aaaaa3c0c64ba5e5c92741.png&optimusCode=20&riskLevel=71&partner=4&platform=13&uuid={uuid}&open_id={open_id}&rc_app=4&rc_platform=13&host_version=12.9.404&fpApp=0&fpPlatform=4&host_ctype=mtandroid&wm_uuid_source=client&sdkVersion=3.2.5&wxPrint=WX__ver1.2.0_CCCC_fcD9ZMAVg%2BgPZVbBxMC2CpiSZxaxYmT4tj6qknbdw4a%2BOpidKPfLRpF0qAe8i9yvXkU8gn7BKE71hesT9yiZYt2Sw6oDX4h6MHclI4m98EFgVoPB%2BF8uBAv0mUTxxo6JAsk6IWxvjQuPW8Rx2ZpHFP70bqscIa%2BMtLiyke8zmmpya%2BWPE1JcwTHSEERgMBpyc3jhwywHfd1WBVrOfo4JATqzzZs16Yg%2F6H%2BYLAEghjqjFXhR9Rs19A%2FhnN3FLVyk09MVMKY2CpQrVUlrg5tnVKRxfU19XZZxWtctX7v8wEOV8IrANE7TXlAdc%2BZIlVHuf3gkSgAL0zyvG%2Bvhk%2BUKqN6OjjPcYDqs%2Feikl7r%2F%2FQ1YW2enoHD%2FaRMXCF%2FQUuxcbYsxZqosFbVUnoKxPI7POO4NwJ7Jv%2B0hB5%2Bz2oVbsBAut2g86nnkMbPsZEkzjmrQJB%2BB7r8N6rvxij8ygXaOWc1g2HQlfIQYRlcYhfkoqknFM8cCDTO4pAsyrr11zPYiJXGKNZOixnWx9IQf6rQsIu%2BIFr9nBHQuRNuFJPtKBelPd8Ad9m%2B4bdhtkuElZ6cwNud%2BfeP8Y4OItb7MBTNVUNNI3ERx8fCEO%2FoKJe%2BDXDEMasvLkOdwohapA9LW%2FaUgBICbf9FcrfAaj5hiGMmmyiBYBk7CAXfwrg0RHalLgY9lUY2l6mMWjIajBeacjBvmh1UbZpl4yY8Pn7agDqV2rI4cX4a4i2gGJ0A0pb%2BNT%2FDdZKd8IR6jbe2io6oRtHbC2z%2FMdPJ8Nu%2F%2FPXQj0vQ7gxYLGDT7ov6rgxFjQWkDE91uXZQ0vw%2Fe%2BtRelBTLHCmhYSsKTJbmTiUlZaLu%2BhSajAzmNRNKTL%2FGTO8jVEJAkMf%2BB0vqYf5el%2F0789zCXqCbDY8fB0mdpD5ZNgfFe9PfvKndaW3xWU0gY5jLMiJhYNPf5eGCLzpuQfsnq3FJq5A0ohWD2RV%2BL9EyGz1FVcgj8elBoBLaQ5O6u60%2BBsWzCvuDNJzXkuT6c330%2F91fsNDQ%2BFNWkt5JscTX0nZOBse%2BLqkdoC7PPRswDUQ3dL1s0LuyIdx%2BbFIK1jBYJm7R4GYrQOFlzl1uEtGO7dVJnykLc9jfr8UFXmgq3SiqTv8kJg8nm%2FYKWSSqkior5TqLvQnSOLxpeR30MONpSSafTERUVYxBiTnoFsJu96c9w2VIJB7ou79%2BLk2Pn1iau4JkBulz2myPCZUjTlzgUi%2BM1Q6SnbfzSwzCYLFLEyoD2QgMSDuWaSjG1%2FSyjYFrSmJb5zeCVeA34C9wEHD8hYtByOC29%2FzT9tFfBMcxOvsFH5NIOHYJ5KtYqjIOvTRgFBp1pd0WBz4tZsSvbH6onjRJrmhcZR1RBMvzmd0l317ysRBMuSqumcXM%2BU8hX83JVeG8dCUEjyUXXNp6y2E1oXoNw1LG8Xn3cX2hbBvD%2F83cCkpJJiM2p4YkaU8PQOly%2BdozOrR02aQLJagJoUN4ZHWyjkw9iIu17MbWUsCHHcPZBOFrgw0mJvdykviOyuAfQXMypF0Amgu17aI5VXxe6p8fhv0o%2F2DNi1u9GrrO62STUs1wbibdWeLFgrWYfFRA7gw9wA3YJ63hnulY8IZqqhql1OEF5sM2VGRPk8deiWTntK98v2CaTkX3EP6gJ2Z7t0NdZ6%2BMJdV3OaknuU80Z0XC2yuoGGMAajn6mCNOwEgSO8dp2q0gtHWlxALIviFDAgZLJgLVDO89oHtTc6v0%2FnnABf2%2FIkIfLIKVNrUOm0vZPGFCAeZEcKnL%2FULp0DuBMaW6xwutjnxnrwSn2Xa4JBsLguqii4GevfR21foZMF9USRGsshCnGvdfjzRfc5%2FLff5aiXALmmkztFtScivuJBUZw73%2ByOR%2B4eC7PTDTGssK17UdaCYykQitK2yMLuNTLx19LkMCQdYJAIVmgE0lIlyt2%2F1Xi5YasnTtwmWTOJZ5vp53lzY1DzXFUcYk95AAPzeUnI2bqiEIJy7kUNb3ZNwW2LX2JoTqywpxNRzfT2VmBWY%2BWU3I9Nj7cFQQQtKe3FTaAYBkfmSGEBT47J1GycrKHvX%2FhG5S2g4m%2BigHUfKtN0Quna6oh78GHCkx0RG0Ip5WX0h7WOpRZcxrwIM22Jg%2BWpm6X7xkZaYeVeNJiKOsW%2FPA9SrJodTfea4GXjDsd2frOJP%2FOD%2FAfX%2FZDs%2B%2FsbcarAE2xcdgYPmzASKpg7WQ7LTdKprgoZkg4sKJT8ISxYR49Y7j3y7wyh5Ti7oiOEgVgMOhTr57wdf9U4BK8dwdXbQ7gu7SBupFt8LwOLUeUYGK6tnZDo7Geo0d0my5n22LPtQRIAMEQQuR%2FYdMdTv7FMfmUj7WyHPNdYKJEuVCwCEGTKMG6oMWpUrBa4Na%2Bxy8mn1Z4LNoUzdIbchBcZ7sECqRiL1fIgljPeeje2mcGuEDQ7OOWRWu575vMjoZjNgLYB9rUXLl9tELmFvCcJqrGihdVDYgwrgLW%2FDsh9nA5xE2uVdsQcNBTBbsdmeg0lfOFrXH%2Fk8XKrfGtWc3BHycC4ZlSQHfeg9LQell0rs2swnh0Lyn59mn%2B%2BX4wHWknctv76nV%2B4caU38fP%2BOqvo2081bnqC8O2geCD%2FshLcRMWqfysG91qQgd9qEqR1HqCLy76mI7qRpDx81%2BWuqWeg6gpyF%2BRiDdVfNHNmCkfFL4lFr3yZUTNQa02zAnaFlqlmhOdNWxUUq8Edib%2B5WZySLqddNJmn8DLN61JMj%2BsxcMG7ivrDOJ4%2BVW0jGnjZS4x%2Frg1Xy9yulp6uVEuqcknwigTfwVHUjTHj%2BNkvB5BIt4R3qT%2B2kS6Hryspevt947s9YFejZux7g8PstPjqOzIRdlsNiDENYoBG8pO7f3WfEE6Ljf7ArAfdpda4Uku1cxXyVUXGR0D32RDG44gKPlxy5NUG166MUB%2BhoZhOhfvvELS%2BGEo4CWadpMarPweFLwberD4gPgGa95SbV2yE%2F6vETUzxbq5K7HNFRMKefvXHLFAdHEaay4ZdbTXfk4U7TZwPQWQi7RhWGFBGrtFBNaPxMPu6kKGQ7uMawsVP334zuT7DoGXXpDhGH6QRDgCwwszadCn%2BCweNq%2BJCYuAPaNfVKj6ZRydLzE1kJgM6rgfjCp5qQyiOGEWg9NmdZ6ozBPiEvVkADEDqVp0hKIb7PpA%2F4Aamt8C2ecSBve4IFSJCp6uUrELc0MA%2FJt2b2oWd86gXkKfW9Qdip3rqpR%2BT4LWVcdG8b2zrr6xExlOa%2BZPohNTSnr%2BO%2Fwt%2FIzxosKpQyVm%2Fp%2BnM5p2Xz4HZ%2FjO9YfWdV%2F01%2Bz5QlLQB%2FqH3A1llJ9TruaXsqTMtO%2BeVoawJ84Qmz5LHGFLxlCf%2BMSKBAlsgzY2Mn4qMuS8jLgFUpzWlhpuLB%2F0hi8s1D%2FNzZ5rI0fDMNetQ9d5yQm1FSGWUyObIRERsjTnz48VaYqhAwMOEMzyuy564l4eMM%2BneIk%2FmgTQg0eahsjI6FFq9i%2FLSUujjR2M49qZ8qovPV6u4d0h9Xw1Yyloel1&wxNickName=%E9%BB%91%E6%9A%97%E9%9D%A2182&wxAvatar=https%3A%2F%2Fimg.meituan.net%2Favatar%2Fddcd13692022b8d5e31020988b38299514234.jpg&city_id_level2=430100&city_id_level3=430102&actual_city_id_level2=430100&actual_city_id_level3=430102&rank_list_id=134b18045ae336624b867a9c3a167570&wm_ctype=mtandroid_wmgroup"
        headersSignInTask = {
            'Host': 'wx.waimai.meituan.com',
            'Connection': 'keep-alive',
            # 'Content-Length': '5192',
            'content-type': 'application/x-www-form-urlencoded',
            'R2X-Referer': 'https://servicewechat.com/wx2c348cf579062e56/0/page-frame.html',
            'retrofit_exec_time': sjtime,
            'openId': open_id,
            'csecuuid': uuid,
            'csecuserid': user_id,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; V2055A Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.74 Mobile Safari/537.36 MicroMessenger/6.5.7  miniprogram MMP/1.24.0.4.335 group/12.9.404',
            'uuid': uuid,
            'wm-ctype': 'wxapp',
            'Accept-Encoding': 'gzip, deflate'
        }
        resSignInTask = requests.request("POST", urlSignInTask, headers=headersSignInTask, data=resSignInTask)
        resSignInTask = json.loads(resSignInTask.text)
        resCodeSignInTask = resSignInTask.get("code")
        resMsgSignInTask = resSignInTask.get("msg")
        if resCodeSignInTask == 0 and resMsgSignInTask == '成功':
            msg += "签到成功(" + resMsgSignInTask + ")"
            self.print_now("开始签到：" + resMsgSignInTask)
        elif resCodeSignInTask == 1:
            msg += "今日已签到(" + resMsgSignInTask + ")"
            self.print_now("今日已签到：" + resMsgSignInTask)
        else:
            msg += "签到失败(" + resMsgSignInTask + ")"
            self.print_now(resMsgSignInTask)
            return [False, msg]

        msg += '\n' + ' * 美团米粒三餐任务:' + '\n\t'
        urlDinnerSignIn = "https://wx.waimai.meituan.com/weapp/v1/wlwc/dinnersignin/sign?ui=46525309&region_id=1000110100&region_version=1699672616801&yodaReady=wx&csecappid=wx2c348cf579062e56&csecplatform=3&csecversionname=9.39.2&csecversion=1.4.0"
        resDataDinnerSignIn = f"action_id=3&ad_personalized_switch=1&content_personalized_switch=1&lch=1089&nickName=yczcc&open_id={open_id}&openIdCipher=AwQAAABJAgAAAAEAAAAyAAAAPLgC95WH3MyqngAoyM%2Fhf1hEoKrGdo0pJ5DI44e1wGF9AT3PH7Wes03actC2n%2FGVnwfURonD78PewMUppAAAADj6uorZJLWKw6oU1dTz5Aoay0VGb98bvc2LmVcxLu8v0Vv0UxeNhJQs3Qrz%2FdwUW9yxaXq6OoBizQ%3D%3D&optimusCode=20&partner=4&platform=13&rank_list_id=134d6efdb164ab2114cd6b7b19001a9b&rc_app=4&rc_platform=13&ref_list_id=134d6ef8fbf8db2114b99a001620fbf7&req_time={sjtime}&riskLevel=71&sdkVersion=3.2.5&sessionId=J2JDXB&user_id={user_id}&userid={user_id}&userIdCanceled=0&userToken={token}&uuid={uuid}&uuidCanceled=0&vatarUrl=https%3A%2F%2Fimg.meituan.net%2Fkangaroox%2F3a057d48536606aaaaa3c0c64ba5e5c92741.png&waimai_sign=%2F&wm_actual_latitude=39071433&wm_actual_longitude=117618593&wm_appversion=9.39.2&wm_ctype=wxapp&wm_dplatform=ios&wm_dtype=iPhone%20XR%3CiPhone11%2C8%3E&wm_dversion=8.0.43&wm_latitude=39067215&wm_logintoken={token}&wm_longitude=117616776&wm_uuid_source=client&wm_uuid={uuid}&wm_visitid={wm_visitid}&wxAvatar=https%3A%2F%2Fimg.meituan.net%2Fkangaroox%2F3a057d48536606aaaaa3c0c64ba5e5c92741.png&wxNickName=yczcc&wxPrint=WX__ver1.2.0_CCCC_dfwOgF35EQNYzVh8i27kXL04k6XTiM6UIbLC34PDQwDR2%2F7%2FJMvZnBl7bRUDYzeKLtoGXRmuSKohJ3tAlwiWVzCDnDa4C655joCG5vW7JfgJko4ippjzK2yF2ghSfwZPDY3i9vh9nbx68tv5RP71B9%2BJ4abbmQI1ydFxF2xyVfbxCUFZvOgp1%2B4DekBE%2BMEE7gYs3ekxU%2FK6zGN9214fyYgX%2BcTO%2B%2FGPlhO7SySxMdyglQAlpQyLyLwSLe%2FGo2key%2FZsVTr5HL0q5QrP2n3FNONqqixKQeBPGZ0%2B%2FY9PmQdgBvmBPDBmvOeDDd54ZLa90s8%2B%2FMEZwm2PaYm%2B5bMAbSuLuw2hKZkuYGY%2FTOJhD0zH3vImvR3j7NkEQgcMa%2BlvyUTnK2pITVhn1bS53GWKeydFa28BCx3GSCsjZnmPlNuMDgaG7Mk2bEvlwnHVDw3VQj%2FoWjyELhYB%2BlkB76jAOo73E31KdYnxjwdbFSsXcAxAyxzHfb9sBvJGef7Vg59qOTxNZA%2BLOHeDsVvHo7lVURNOSbmYSSRTcMBY5NaXt%2Fia37O9ECiRGlm0QCiPkAHwQFBspUjUm8xOAEjS69vOVkUeIQCMoOIo%2ByPqG1dF97b5zNsDRYZCECZazwpaLum4K7HgVxhQXMOmKXaMTLcvvWYX2WxvTMKvK3y19vO8os%2Fv86J16lJ9kk2fbg7sKmYYxdkL8IkAMSe2oD5ZauMeENTGT95MCWA1AELq%2BEJUGJUWJjX7f6IfvPaqWeqo4%2Bg3%2BUiZnoH%2Bt0%2FUqWL3rbLiFG%2BtAFP9CzVcEI9Js1rFGPE8aQjuxMTpf5qAwZQuC3jnF0i%2Fs9LSq8sPjQVi9GZPiTD4K0LB1oaDtPUBTCfI%2BvZQ8TQpgoRR96%2FPo5jiNgvaI3Scqh51%2F0V%2Bq9phLj0gcNrgcmC6QUQe%2FPf2SXJy21x5PlJsZieSL6byaOfGzJFwpj5VEaRi%2BJScPJpSIGLehjXiR1MyJLL3qQaqU81kplbHs4m%2BXbRMMbhS2kz9hlPZwtLaXsfetyc6fpP9Pkx3Gwui8hHJ80D9RkZ4lKli2hhU4C%2FOLC8M3oc5kqsgOmD410fFKGuaGIQ%2F8TXFkpo7kG1Eic1XiJN3RdkqAWUHbUkeY2y6cadqoICIJd2R3yITvT0%2BoWkCx%2BxnM81PpX6meisLE%2FeUiGNVgVUWH2mjTIFgXR2B8kZhHrGqY2i2oABxhNYdksoX8sroWnGIF4x9CZKi2590R1E4KEbLXVkoc73NlvERxxEAuIA8uHm7Z%2FPdjKFGG%2BDlFnFDuXbymqcAPPWc4c6jILf5z3SVO9c1q3xai8NCge8%2BCELDWzwVjA3ZXK4devg6V7%2BVWCxpQ%2FmDF%2Bkf7HsM2NZV8T0cvajA3PVCnBla8KPNxuIXUc%2BsZU8cWFf2JpjWRJpBUlYWKHB%2BAipF4vHZGWWseiOclfAmAvdqx6xoetWepKdsh6CfAhwvXoc3JCdo77K1Z7zXr35w0PwYiDDAxUiG7aosSueqlHaDiwcS3UXmpGd3PGduoBUE7ijCnmRQiouYkVlNm9G%2F2zKrp6d9NZZQ3DBlEoApEhea9WhfVx3Y8t%2FueaNzMpr0R8ULcSBPtv7m3Ang5h2zP5M7CyybD2raQ5ZJHj4FZPKonBUwoiAhjMjHOnE84Ub9jO%2BnCYeUOyxbl%2BXXNPNtIXq6LuQB6FVugub0zHo%2FJxvnJTdvj6skOB5gCEXQ3bgYwAyz3jcz4UdyWFpG0va%2Fm39jenVVqeaPZMGBdR5CHTZsJuey9ccaHhfB5TvoPV%2B03PLbUR%2BIbnLhdyRM0w8wncaJMeAJuqiqtOt2YnRlfkNuUugqVpJ%2BlWmBg8qx6OxRIoIc2GqA%2F6Z95FpF%2FVzDOQmlJaGXoABJ2fyRu%2B4AXM72P0nRm%2B5qISJHVZ%2FGNNXTWLcEMRzVzZ5Js11BVwFVkp8DQNKV6SD6%2Be1aH58lBqecsKjcQpsbCmw0iiX6cszzj5%2BSAkAHNVBRxpU6nmjM2pWFZg4xsAxONO9dqARcq%2FAwhbfTLC5cz7JCHufgh28yGdTKGJM7z0vIyWTuY4%2F7oTNUje6UsFyINVF4pZkEeCdYjVR8FvTtrOBbmnfPr91W0sa2MUYGuH9sKfORVEina0saeuNlcql3sAokDSGGAonZ4kKtDl8ZQqysJctgWnWu2rHdqoGNZ3jXhBQ8CV6yK8tyY%2BT0ZUmZZ781IM18yKNuUtANbgotaxmp6t0XGYhfqJk7166tqtvPN3qtprA%2BBj4%2Bi3k%2F3doI5T%2FLo0EgOb0O68yv%2FH04jzrbNb83oslWryA8iwn8UkIboJRF68IZ5Cwran5sp3t0sjnoTWeNJbmFJL%2Bcv52IHkCo9aHZSNDvt9DIedRiKCW0ggYDYsT%2FExv%2Fi1yOYNCYsw8iqQK8QBGdJMt637ylwJ%2FinOgkeAxWxiRbz4j%2BBqa8hL67TaIdYkXLGvJgCpsTkmTEYoFl7ynlWS%2FspRtovPKk0Egtgl8jIR4PpNcJud6jPCpo7Fw91OyBm3Kc5atMuDFTRxJ4ynHA8%2Bk%2FTVpnJjoFTnHREnHS1SKOl00s6aPF7AdiHycupULE%2FFoTpshcLXSubIM%2BUBRR%2FhgDSVbHk%2Bl3UbGOFLAwn%2Bf3c0bmrN71Yk5rmawd9wpkyPxE5FvrTfs2ULlgm5cIiP6E2oPa%2BscHGJCs8UYyelYq8KFPVuNq5DothYy2Uid%2FfDA3NlgsNxp6fHziLGP3P9d866qr7%2FN0WUDMj3Ogc4Odj6F5DwAFSDNOfourDWnZyy3%2B5NNUDaqTqMAOSRo1WVJ2KtmtDS795n1EZek8lhkn%2BYGRsKRwnhNVAwPFyLaODAwiYp2pxvLaz%2B%2BEjBIoT6ZJM2Hthyz%2BBmO2R9J41dok%2BcMpblz%2FeirQxO%2BQwARF9TVjHaL53r5G50zCaGooJADN1l2rifCHTC8Zr%2BIVjyjS73%2Bv8VVWK9fBtgqCPIcKFYv2q4%2BKqCghxyHc3W3TC7nB71AXMFHqidzmn%2BObCxeX0ExWAy0HCPhlSizgvCezqeOc9vBwTVeyUaEe3QmcyysHzbsEBWhoYFqZtMqcBcaMtxkM8PWSRYYduAx5Pq2SdO3DffeD6BGDdZc%2FgBLcY7OnnTRuMYvDB0GkfxbJT8%2Btkwt87Gy%2FTttb7k%2BaVuVpN65B%2FfvKN%2BoHHck6CvdQi88kAxiGEYTFivgZkYLlWKEkgsGiAQ33t0YfbmPCV1%2BXNzG2v36x0J3jhx38L7CIfWPLKfHT9CQYgSATRb%2BfwMGnZ29boOzfSBZUkbjCVcwQR7l9kNIWXMnr2rjUElh78iEl87is5vaD%2BvTwhnTJtFPYivi9s7XWaQkB%2BlEo1%2BtjtJigq%2FEhJhUnPowxg1E0llv2aKQC1AXwSIFTF9RPzqh0k1hqErNoNIHG4YEe2ICUrcQlrErLT%2FS%2B743ILvJYytKgwrSjLjxyjpcPrJAb"
        headersDinnerSignIn = {
            'Host': 'wx.waimai.meituan.com',
            'Connection': 'keep-alive',
            # 'Content-Length': '5204',
            'content-type': 'application/x-www-form-urlencoded',
            'R2X-Referer': 'https://servicewechat.com/wx2c348cf579062e56/0/page-frame.html',
            'retrofit_exec_time': sjtime,
            'openId': open_id,
            'csecuuid': uuid,
            'csecuserid': user_id,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; V2055A Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.74 Mobile Safari/537.36 MicroMessenger/6.5.7  miniprogram MMP/1.24.0.4.335 group/12.9.404',
            'uuid': uuid,
            'wm-ctype': 'wxapp',
            'Accept-Encoding': 'gzip, deflate'
        }
        resDinnerSignIn = requests.request("POST", urlDinnerSignIn, headers=headersDinnerSignIn,
                                           data=resDataDinnerSignIn)
        resDinnerSignIn = json.loads(resDinnerSignIn.text)
        resCodeDinnerSignIn = resDinnerSignIn.get("code")
        resDataDinnerSignIn = resDinnerSignIn.get("data")
        resMsgDinnerSignIn = resDinnerSignIn.get("msg")
        if resCodeDinnerSignIn == 0:
            sctime = ''
            if 7 <= datetime.datetime.now().hour <= 9:
                sctime = "早餐"
            elif 10 <= datetime.datetime.now().hour <= 14:
                sctime = "午餐"
            elif 16 <= datetime.datetime.now().hour <= 21:
                sctime = "晚餐"
            scPoints = resDataDinnerSignIn.get("get_points")
            msg += sctime + "领取成功:" + str(scPoints) + "米粒"
            self.print_now(sctime + "领取成功:" + str(scPoints) + "米粒")
        elif resCodeDinnerSignIn == 5:
            sctime = ''
            if 7 <= datetime.datetime.now().hour <= 9:
                sctime = "早餐米粒"
            elif 10 <= datetime.datetime.now().hour <= 14:
                sctime = "午餐米粒"
            elif 16 <= datetime.datetime.now().hour <= 21:
                sctime = "晚餐米粒"
            scMsg = "已领取(" + resDinnerSignIn.get("msg") + ")"
            msg += sctime + scMsg
            self.print_now(sctime + scMsg)
        else:
            msg += "领取失败," + resMsgDinnerSignIn
            self.print_now(resMsgDinnerSignIn)
            return [False, msg]
        return [True, msg]

    def main(self):
        msg_all = ""
        for check_item in self.check_items:
            token = check_item["token"]
            uuid = check_item["uuid"]
            user_id = check_item["user_id"]
            open_id = check_item["open_id"]
            # 签到
            resSign = self.sign(token=token, uuid=uuid, user_id=user_id, open_id=open_id)
            if not resSign[0]:
                msg_all += resSign[1] + "\n"
                continue
            msg_all += resSign[1] + "\n"
        return msg_all


if __name__ == "__main__":
    data = get_data()
    _check_items = data.get("MeiTuanML", [])
    # _check_items = [{
    #     "user_id": "",
    #     "open_id": "",
    #     "token": "-",
    #     "uuid": ""
    # }]
    result = MeiTuanML(check_items=_check_items).main()
    send("美团米粒", result)
