# -*- coding: utf-8 -*-
"""
cron: 23 14 * * *
new Env('IKuuu机场');
"""

import re
import requests

from notify_mtr import send
from utils import get_data

class IKuuu:
    def __init__(self, check_items):
        self.check_items = check_items

    @staticmethod
    def sign(email, passwd):
        msg = ""
        try:
            body = {"email": email, "passwd": passwd}
            headers = {
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
            res = requests.get('https://ikuuu.club/', headers=headers)
            url = re.findall('target="_blank">(.*?)</a>', res.text, re.S)
            for i in range(len(url)):
                ikuuu_url = url[i]
                resp = requests.session()
                res_login = resp.post(f'{ikuuu_url}auth/login', headers=headers, data=body).json()
                if 'ret' not in res_login:
                    msg += f"登录地址: {ikuuu_url} 解析响应失败\n" + res_login['msg'] + "\n"
                    continue
                if 1 != res_login['ret']:
                    msg += f"登录地址: {ikuuu_url} 登录失败\n" + res_login['msg'] + "\n"
                    continue

                res_checkin = resp.post(f'{ikuuu_url}user/checkin').json()
                if 'ret' not in res_checkin:
                    msg += f"帐号信息: {email}\n签到地址: {ikuuu_url} 解析响应失败\n" + res_checkin['msg'] + "\n"
                    continue
                if 1 == res_checkin['ret']:
                    msg += f"帐号信息: {email}\n签到状态: 签到成功," + res_checkin['msg'] + "\n"
                    break
                elif 0 == res_checkin['ret']:
                    msg += f"帐号信息: {email}\n签到状态: 已签到," + res_checkin['msg'] + "\n"
                    break
                else:
                    msg += f"帐号信息: {email}\n签到地址: {ikuuu_url} 签到失败\n" + res_checkin['msg'] + "\n"
                    continue
        except Exception as e:
            print('请检查帐号配置是否错误')
            msg += f"帐号信息: {email}\n请检查帐号配置是否错误\n"
        return msg

    def main(self):
        msg_all = ""
        for check_item in self.check_items:
            email = check_item.get("email")
            passwd = check_item.get("passwd")
            msg = self.sign(email, passwd)
            msg_all += msg + "\n\n"
        return msg_all

if __name__ == "__main__":
    data = get_data()
    _check_items = data.get("IKUUU", [])
    res = IKuuu(check_items=_check_items).main()
    send("IKuuu机场", res)
