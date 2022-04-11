#!/usr/bin/env python3
"""
:author @yczcc from github
cron: 0 0 */7 * *
new Env('随机定时');
"""

from abc import ABC
from random import randrange
from typing import Dict, List

import requests

from notify_mtr import send
from utils import get_data
from utils_env import get_env_int

import time
import traceback

class ClientApi(ABC):
    def __init__(self):
        self.cid = ""
        self.sct = ""
        self.url = "http://localhost:5700/"
        self.twice = False
        self.token = ""
        self.cron: List[Dict] = []

    def init_cron(self):
        raise NotImplementedError

    def shuffle_cron(self):
        raise NotImplementedError

    def run(self):
        self.init_cron()
        return self.shuffle_cron()

    @staticmethod
    def get_ran_min() -> str:
        return str(randrange(0, 60))

    def get_ran_hour(self, is_api: bool = False) -> str:
        if is_api:
            return str(randrange(7, 9))
        if self.twice:
            start = randrange(0, 12)
            return f"{start},{start + randrange(6, 12)}"
        return str(randrange(0, 24))

    def random_time(self, origin_time: str, command: str):
        if command.find("rssbot") != -1 or command.find("hax") != -1:
            return ClientApi.get_ran_min() + " " + " ".join(origin_time.split(" ")[1:])
        if command.find("api") != -1:
            return ClientApi.get_ran_min() + " " + \
                   self.get_ran_hour(True) + " " + \
                   " ".join(origin_time.split(" ")[2:])
        return ClientApi.get_ran_min() + " " + \
               self.get_ran_hour() + " " + \
               " ".join(origin_time.split(" ")[2:])


class QLClient(ClientApi):
    def __init__(self, client_info: Dict):
        super().__init__()
        if not client_info or not (cid := client_info.get("client_id")) or not (
                sct := client_info.get("client_secret")):
            raise ValueError("无法获取client相关参数")
        else:
            self.cid = cid
            self.sct = sct
        self.url = client_info.get("url", "http://localhost:5700").rstrip("/") + "/"
        self.twice = client_info.get("twice", False)
        self.repo = client_info.get("repo", "")
        if len(self.repo) < 1:
            raise ValueError("必须指定repo")
        self.exclude = client_info.get("exclude", "")
        self.token = requests.get(url=self.url + "open/auth/token",
                                  params={"client_id": self.cid, "client_secret": self.sct}).json()["data"]["token"]
        if not self.token:
            raise ValueError("无法获取token")

    def init_cron(self):
        time_now = int(round(time.time() * 1000))
        has_exclude = False
        if len(self.exclude) > 0:
            has_exclude = True
        self.cron: List[Dict] = list(
            filter(lambda x: not x.get("isDisabled", 1)
                             and x.get("command", "").find(self.repo) != -1
                             and ((has_exclude and x.get("command", "").find(self.exclude) == -1) or (not has_exclude)),
                   requests.get(url=self.url + "open/crons?searchValue=" + self.repo + "&t=" + str(time_now),
                                headers={"Authorization": f"Bearer {self.token}"}).json()["data"]))

    def shuffle_cron(self):
        total = 0
        success = 0
        for c in self.cron:
            total += 1
            if 'schedule' in c:
                data = {
                    "id": c["id"],
                    "name": c["name"],
                    "command": c["command"],
                    "schedule": self.random_time(c["schedule"], c["command"]),
                }
                if 'labels' in c and c["labels"] and len(c["labels"]) > 0 and len(c["labels"][0]) > 0:
                    data["labels"] = c["labels"]
                else:
                    data["labels"] = []
                res = requests.put(url=self.url + "open/crons",
                                   data=data,
                                   headers={"Authorization": f"Bearer {self.token}"}).json()
                if 'code' in res and 200 == res['code']:
                    success += 1
                else:
                    print(c)
                    print(data)
                    print(res)
            else:
                print(c)
        return [total, success]


def get_client():
    env_type = get_env_int()
    if env_type == 5 or env_type == 6:
        check_data = get_data()
        return QLClient(check_data.get("RANDOM", [[]])[0])


msg = "null"
try:
    res = get_client().run()
    msg = "处于启动状态的任务定时修改完成！总计：" + str(res[0]) + "个， 成功：" + str(res[1]) + "个。"
except ValueError as e:
    msg = "配置错误：" + str(e) + "，请检查你的配置文件！"
    traceback.print_exc()
except KeyError:
    msg = "配置错误，请检查你的配置文件！"
    traceback.print_exc()
except AttributeError:
    msg = "你的系统不支持运行随机定时！"
    traceback.print_exc()
# print(msg)
send("随机定时", msg)
