# -*- coding: utf-8 -*-
"""
cron: 10 19 * * *
new Env('苹果团');
"""

import re

import requests
import urllib3
from bs4 import BeautifulSoup

from notify_mtr import send
from utils import get_data

urllib3.disable_warnings()


class AppleTuan:
    def __init__(self, check_items):
        self.check_items = check_items
        self.url = "https://appletuan.com"

    def sign(self, session):
        msg = ""
        response = session.get(url=self.url + "/checkins", verify=False)

        soup = BeautifulSoup(response.text, "html.parser")
        chechin_info = soup.find_all("div", "py-3 bg-tertiary-200 rounded text-center mt-3")
        if (len(chechin_info) > 0):
            if chechin_info[0].span.text == "今日已签到":
                acc_info = soup.find_all("div", "w-3/12")
                idx = 0
                msg += "当前资产："
                for child in acc_info[0].children:
                    text = child.text.strip()
                    if len(text) < 1:
                        idx += 1
                        continue
                    text = text.replace('\n', '').replace('\r', '')
                    if len(text) < 1:
                        idx += 1
                        continue
                    msg += "\n  " + text+ "：" + acc_info[1].contents[idx].text
                    idx += 1
                return "今日已签到\n" + msg

        # <a class="btn btn-blue btn-big block text-center" rel="nofollow" data-method="post" href="/checkins/start">签到</a>
        pattern = (r"<a class=\"btn btn-blue btn-big block text-center\" rel=\"nofollow\" data-method=\"post\" href=\"(.*?)\">签到</a>")
        urls = re.findall(pattern=pattern, string=response.text)
        url = urls[0] if urls else None
        if url is None:
            print(response)
            print(response.text)
            return "cookie 可能过期，获取签到url失败！"
        checkin_url = "https://appletuan.com" + url
        print(checkin_url)

        # <meta name="csrf-param" content="authenticity_token" />
        # <meta name="csrf-token" content="QckUneXCOcqWFhwxoq4ig8Btf2sQEj0cVOylL2tO3tqgsDi8iQq034Vajw4wdomaoZWJKRhP9UvyCr9OkJV3sQ" />
        pattern = (r"<meta name=\"csrf-param\" content=\"(.*?)\" />")
        params = re.findall(pattern=pattern, string=response.text)
        param = params[0] if params else None
        if param is None:
            print(response)
            print(response.text)
            return "cookie 可能过期，无法获取签到请求参数token名称"
        token_param_name = param
        print(token_param_name)

        pattern = (r"<meta name=\"csrf-token\" content=\"(.*?)\" />")
        params = re.findall(pattern=pattern, string=response.text)
        param = params[0] if params else None
        if param is None:
            print(response)
            print(response.text)
            return "cookie 可能过期，无法获取签到请求参数token值"
        token_param_value = param
        print(token_param_value)

        checkin_data = "_method=post&" + token_param_name + "=" + token_param_value
        print(checkin_data)

        session.headers.setdefault("content-type", "application/x-www-form-urlencoded")
        print(session.headers)

        response = session.post(url=checkin_url, data=checkin_data, verify=False)

        soup = BeautifulSoup(response.text, "html.parser")
        acc_info = soup.find_all("div", "w-3/12")
        if (len(acc_info) < 1):
            print(response)
            print(response.text)
            return "签到失败\n" + str(response.status_code)
        idx = 0
        msg += "当前资产："
        for child in acc_info[0].children:
            text = child.text.strip()
            if len(text) < 1:
                idx += 1
                continue
            text = text.replace('\n', '').replace('\r', '')
            if len(text) < 1:
                idx += 1
                continue
            msg += "\n  " + text + "：" + acc_info[1].contents[idx].text
            idx += 1
        return "签到成功\n" + msg

    def main(self):
        msg_all = ""
        for check_item in self.check_items:
            cookie = {
                "_session_id": check_item["_session_id"]
            }
            session = requests.session()
            requests.utils.add_dict_to_cookiejar(session.cookies, cookie)
            session.headers.update(
                {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
                    "referer": self.url,
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
                }
            )
            msg = self.sign(session=session)
            msg_all += msg + "\n\n"
        return msg_all


if __name__ == "__main__":
    data = get_data()
    _check_items = data.get("AppleTuan", [])
    res = AppleTuan(check_items=_check_items).main()
    send("苹果团", res)
