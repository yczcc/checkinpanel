#!/usr/bin/python3
# -- coding: utf-8 --
"""
cron "13,23 9 * * *" script-path=xxx.py,tag=匹配cron用
new Env('i茅台');
"""

import base64
import datetime
import hashlib
import json
import math
import random
import time
from os import system, path
from sys import exit, stdout, argv

from notify_mtr import send
from utils import get_data

try:
    import requests
    import pytz
    from Crypto.Cipher import AES
except:
    print(
        "你还没有安装依赖库 正在尝试自动安装 请在安装结束后重新执行此脚本\n若还是提示本条消息 请自行运行如下命令或者在青龙的依赖管理里安装python的下列依赖库")
    system("pip3 install requests")
    system("pip3 install pytz")
    print("安装完成 脚本退出 请重新执行")
    exit(0)


def print_now(content):
    print(content)
    stdout.flush()


class Encrypt:
    def __init__(self, key, iv):
        self.key = key.encode('utf-8')
        self.iv = iv.encode('utf-8')

    # @staticmethod
    def pkcs7padding(self, text):
        """明文使用PKCS7填充 """
        bs = 16
        length = len(text)
        bytes_length = len(text.encode('utf-8'))
        padding_size = length if (bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        padding_text = chr(padding) * padding
        self.coding = chr(padding)
        return text + padding_text

    def aes_encrypt(self, content):
        """ AES加密 """
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        # 处理明文
        content_padding = self.pkcs7padding(content)
        # 加密
        encrypt_bytes = cipher.encrypt(content_padding.encode('utf-8'))
        # 重新编码
        result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
        return result

    def aes_decrypt(self, content):
        """AES解密 """
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        content = base64.b64decode(content)
        text = cipher.decrypt(content).decode('utf-8')
        return text.rstrip(self.coding)


# 获取i茅台的最新版本号
def getMtVersion():
    # mt_version = "".join(re.findall('latest__version">(.*?)</p>',
    #                                 requests.get('https://apps.apple.com/cn/app/i%E8%8C%85%E5%8F%B0/id1600482450').text,
    #                                 re.S)).split(" ")[1]
    mt_version = json.loads(
        requests.get("https://itunes.apple.com/cn/lookup?id=1600482450").text)["results"][0]["version"]
    return mt_version


# 获取当前北京时间秒级时间戳
def getDayTime():
    # 创建一个东八区（北京时间）的时区对象
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # 获取当前北京时间的日期和时间对象
    beijing_dt = datetime.datetime.now(beijing_tz)

    # 设置时间为0点
    beijing_dt = beijing_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    # 获取时间戳（以秒为单位）
    timestamp = int(beijing_dt.timestamp()) * 1000
    return timestamp


# 获取位置最近的门店ID
def distanceShop(city,
                 item_code,
                 p_c_map,
                 province,
                 shops,
                 source_data,
                 lat: str = '28.499562',
                 lng: str = '102.182324'):
    # shop_ids = p_c_map[province][city]
    temp_list = []
    for shop in shops:
        shopId = shop['shopId']
        items = shop['items']
        item_ids = [i['itemId'] for i in items]
        # if shopId not in shop_ids:
        #     continue
        if str(item_code) not in item_ids:
            continue
        shop_info = source_data.get(shopId)
        # d = geodesic((lat, lng), (shop_info['lat'], shop_info['lng'])).km
        d = math.sqrt((float(lat) - shop_info['lat']) ** 2 + (float(lng) - shop_info['lng']) ** 2)
        # print(f"距离：{d}")
        temp_list.append((d, shopId))

    # sorted(a,key=lambda x:x[0])
    temp_list = sorted(temp_list, key=lambda x: x[0])
    # logging.info(f"所有门店距离:{temp_list}")
    if len(temp_list) > 0:
        return temp_list[0][1]
    else:
        return '0'


# 获取出货量最大的门店ID
def maxShop(city, item_code, p_c_map, province, shops):
    max_count = 0
    max_shop_id = '0'
    shop_ids = p_c_map[province][city]
    for shop in shops:
        shopId = shop['shopId']
        items = shop['items']

        if shopId not in shop_ids:
            continue
        for item in items:
            if item['itemId'] != str(item_code):
                continue
            if item['inventory'] > max_count:
                max_count = item['inventory']
                max_shop_id = shopId
    print_now(f'item code {item_code}, max shop id : {max_shop_id}, max count : {max_count}')
    return max_shop_id


# 根据地址描述获取地理编码(坐标)
def getGeoCode(address: str):
    # https://www.piliang.tech/geocoding-amap
    resp = requests.get(f"https://www.piliang.tech/api/amap/geocode?address={address}")
    geocodes: list = resp.json()['geocodes']
    return geocodes


class IMaoTai:
    def __init__(self, check_items):
        self.check_items = check_items
        # 设备ID固定一个值就好
        # self.DEVICE_ID = str(uuid.uuid4()).upper()
        self.DEVICE_ID = ''
        self.MOBILE = ''
        self.TOKEN = ''
        self.USER_ID = 0
        self.AES_KEY = 'qbhajinldepmucsonaaaccgypwuvcjaa'
        self.AES_IV = '2018534749963515'
        self.SALT = '2af72f100c356273d46284f6fd1dfc08'
        self.ENCRYPT = Encrypt(key=self.AES_KEY, iv=self.AES_IV)
        # 可预约商品列表
        self.ITEM_MAP = {
            "10941": "53%vol 500ml贵州茅台酒（甲辰龙年）",
            "10942": "53%vol 375ml×2贵州茅台酒（甲辰龙年）",
            "10056": "53%vol 500ml茅台1935",
            "2478": "53%vol 500ml贵州茅台酒（珍品）"
        }
        # 需要预约的商品(默认只预约2个龙茅)
        ########################
        self.ITEM_CODES = ['10941', '10942']
        # 预约规则配置,二选一
        ########################
        # 预约本市出货量最大的门店
        self.MAX_ENABLED = True
        # 预约你的位置附近门店
        self.DISTANCE_ENABLED = False
        ########################
        self.MT_VERSION = getMtVersion()
        self.HEADER_CONTEXT = {
            'MT-Lat': '28.499562',
            'MT-Lng': '102.182324',
            'MT-User-Tag': '0',
            'MT-Network-Type': 'WIFI',
            'MT-Token': '1',
            'MT-Team-ID': '',
            'MT-Info': '028e7f96f6369cafe1d105579c5b9377',
            'MT-Device-ID': self.DEVICE_ID,
            'MT-Bundle-ID': 'com.moutai.mall',
            'MT-K': '1675213490331',
            'MT-Request-ID': '167560018873318465',
            'MT-APP-Version': self.MT_VERSION,
            'MT-R': 'clips_OlU6TmFRag5rCXwbNAQ/Tz1SKlN8THcecBp/HGhHdw==',
            # 'Content-Length': '93',
            'Accept': '*/*',
            'Accept-Language': 'en-CN;q=1, zh-Hans-CN;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Host': 'app.moutai519.com.cn',
            'User-Agent': 'iOS;16.6;Apple;iPhone XR',
            'userId': '2'
        }
        self.HEADERS = {}

    # 初始化请求头
    def initHeaders(self, user_id: str = '1', token: str = '2', lat: str = '28.499562', lng: str = '102.182324'):
        dict.update(self.HEADER_CONTEXT, {"MT-Device-ID": self.DEVICE_ID})
        for k in dict.keys(self.HEADER_CONTEXT):
            dict.update(self.HEADERS, {k: self.HEADER_CONTEXT[k]})
        dict.update(self.HEADERS, {"userId": user_id})
        dict.update(self.HEADERS, {"MT-Token": token})
        dict.update(self.HEADERS, {"MT-Lat": lat})
        dict.update(self.HEADERS, {"MT-Lng": lng})
        dict.update(self.HEADERS, {"MT-APP-Version": self.MT_VERSION})

    # 请求参数签名
    def signature(self, data: dict, current_time: str):
        keys = sorted(data.keys())
        temp_v = ''
        for item in keys:
            temp_v += data[item]
        text = self.SALT + temp_v + current_time
        hl = hashlib.md5()
        hl.update(text.encode(encoding='utf8'))
        md5 = hl.hexdigest()
        return md5

    # 获取手机号登录验证码
    def get_vcode(self, mobile: str, current_time: str):
        timestamp_ms = int(time.time() * 1000)
        params = {'mobile': mobile}
        md5 = self.signature(params, current_time)
        dict.update(params, {'md5': md5, "timestamp": current_time, 'MT-APP-Version': self.MT_VERSION})
        dict.update(self.HEADERS, {"MT-K": f'{timestamp_ms}'})
        dict.update(self.HEADERS, {"MT-Request-ID": f'{timestamp_ms}{random.randint(10000, 99999)}'})
        responses = requests.post("https://app.moutai519.com.cn/xhr/front/user/register/vcode", json=params,
                                  headers=self.HEADERS)
        print_now(
            f'get v_code : params : {params}, response code : {responses.status_code}, response body : {responses.text}')

    # 手机号登录
    def login(self, mobile: str, v_code: str):
        timestamp_ms = int(time.time() * 1000)
        current_time = str(timestamp_ms)
        params = {'mobile': mobile, 'vCode': v_code, 'ydToken': '', 'ydLogId': ''}
        md5 = self.signature(params, current_time)
        dict.update(params, {'md5': md5, "timestamp": current_time, 'MT-APP-Version': self.MT_VERSION})
        dict.update(self.HEADERS, {"MT-K": f'{timestamp_ms}'})
        dict.update(self.HEADERS, {"MT-Request-ID": f'{timestamp_ms}{random.randint(10000, 99999)}'})
        responses = requests.post("https://app.moutai519.com.cn/xhr/front/user/register/login", json=params,
                                  headers=self.HEADERS)
        if responses.status_code != 200:
            print_now(
                f'login : params : {params}, response code : {responses.status_code}, response body : {responses.text}')
        dict.update(self.HEADERS, {'MT-Token': responses.json()['data']['token']})
        dict.update(self.HEADERS, {'userId': responses.json()['data']['userId']})
        return responses.json()['data']['token'], responses.json()['data']['userId']

    # 获取当前会话ID
    def get_current_session_id(self):
        day_time = getDayTime()
        responses = requests.get(
            f"https://static.moutai519.com.cn/mt-backend/xhr/front/mall/index/session/get/{day_time}")
        if responses.status_code != 200:
            print_now(
                f'get_current_session_id : params : {day_time}, response code : {responses.status_code}, response body : {responses.text}')
        current_session_id = responses.json()['data']['sessionId']
        dict.update(self.HEADERS, {'current_session_id': str(current_session_id)})

    # 按照门店选择策略获取当前位置预约的门店ID
    def get_location_count(self, province: str,
                           city: str,
                           item_code: str,
                           p_c_map: dict,
                           source_data: dict,
                           lat: str = '28.499562',
                           lng: str = '102.182324'):
        day_time = getDayTime()
        session_id = self.HEADERS['current_session_id']
        responses = requests.get(
            f"https://static.moutai519.com.cn/mt-backend/xhr/front/mall/shop/list/slim/v3/{session_id}/{province}/{item_code}/{day_time}")
        if responses.status_code != 200:
            print_now(
                f'get_location_count : params : {day_time}, response code : {responses.status_code}, response body : {responses.text}')
        shops = responses.json()['data']['shops']

        if self.MAX_ENABLED:
            return maxShop(city, item_code, p_c_map, province, shops)
        if self.DISTANCE_ENABLED:
            return distanceShop(city, item_code, p_c_map, province, shops, source_data, lat, lng)

    def act_params(self, shop_id: str, item_id: str):
        # {
        #     "actParam": "a/v0XjWK/a/a+ZyaSlKKZViJHuh8tLw==",
        #     "itemInfoList": [
        #         {
        #             "count": 1,
        #             "itemId": "2478"
        #         }
        #     ],
        #     "shopId": "151510100019",
        #     "sessionId": 508
        # }
        session_id = self.HEADERS['current_session_id']
        userId = self.HEADERS['userId']
        params = {"itemInfoList": [{"count": 1, "itemId": item_id}],
                  "sessionId": int(session_id),
                  "userId": userId,
                  "shopId": shop_id
                  }
        s = json.dumps(params)
        act = self.ENCRYPT.aes_encrypt(s)
        params.update({"actParam": act})
        return params

    # 申购预约
    def reservation(self, params: dict, mobile: str) -> dict:
        timestamp_ms = int(time.time() * 1000)
        params.pop('userId')
        dict.update(self.HEADERS, {"MT-K": f'{timestamp_ms}'})
        dict.update(self.HEADERS, {"MT-Request-ID": f'{timestamp_ms}{random.randint(10000, 99999)}'})
        responses = requests.post(
            "https://app.moutai519.com.cn/xhr/front/mall/reservation/add",
            json=params,
            headers=self.HEADERS)
        if responses.status_code == 401:
            msg = f'[{mobile}],登录token失效，需要重新登录'
            print_now(msg)
            return {"name": "申购结果", "value": msg}
        if '您的实名信息未完善或未通过认证' in responses.text:
            msg = f'[{mobile}],{responses.text}'
        else:
            msg = f'预约成功: mobile:{mobile} :  response code: {responses.status_code}, response body: {responses.text}'
        print_now(msg)
        return {"name": "申购结果", "value": msg}

    # 获取门店数据
    def get_shop_data(self, lat: str = '28.499562', lng: str = '102.182324'):
        timestamp_ms = int(time.time() * 1000)
        p_c_map = {}
        url = 'https://static.moutai519.com.cn/mt-backend/xhr/front/mall/resource/get'
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_1 like Mac OS X)',
            'Referer': 'https://h5.moutai519.com.cn/gux/game/main?appConfig=2_1_2',
            'Client-User-Agent': 'iOS;16.0.1;Apple;iPhone 14 ProMax',
            'MT-R': 'clips_OlU6TmFRag5rCXwbNAQ/Tz1SKlN8THcecBp/HGhHdw==',
            'Origin': 'https://h5.moutai519.com.cn',
            'MT-APP-Version': self.MT_VERSION,
            'MT-K': f'{timestamp_ms}',
            'MT-Request-ID': f'{timestamp_ms}{random.randint(10000, 99999)}',
            'Accept-Language': 'zh-CN,zh-Hans;q=1',
            'MT-Device-ID': self.DEVICE_ID,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'MT-Lng': f'{lng}',
            'MT-Lat': f'{lat}'
        }
        res_resource = requests.get(url, headers=headers)
        if 200 != res_resource.status_code:
            return None
        mt_shops_pc = res_resource.json().get('data', {}).get('mtshops_pc', {})
        mt_shops_pc_version = mt_shops_pc.get('version')
        mt_shops_pc_filename = 'mtshops_pc_' + str(mt_shops_pc_version) + '.json'
        if path.exists(mt_shops_pc_filename):
            with open(mt_shops_pc_filename, 'r') as f:
                mt_shops_pc_file = f.read()
                mt_shops_pc_data = json.loads(mt_shops_pc_file)
        else:
            mt_shops_pc_url = mt_shops_pc.get('url')
            res_mt_shops_pc = requests.get(mt_shops_pc_url)
            mt_shops_pc_data = res_mt_shops_pc.json()
            with open(mt_shops_pc_filename, 'w') as f:
                f.write(json.dumps(mt_shops_pc_data, ensure_ascii=False))

        for k, v in dict(mt_shops_pc_data).items():
            provinceName = v.get('provinceName')
            cityName = v.get('cityName')
            if not p_c_map.get(provinceName):
                p_c_map[provinceName] = {}
            if not p_c_map[provinceName].get(cityName, None):
                p_c_map[provinceName][cityName] = [k]
            else:
                p_c_map[provinceName][cityName].append(k)

        return p_c_map, dict(mt_shops_pc_data)

    # 获取用户耐力值奖励
    def getUserEnergyAward(self, mobile: str) -> dict:
        """
        领取耐力
        """
        cookies = {
            'MT-Device-ID-Wap': self.HEADERS['MT-Device-ID'],
            'MT-Token-Wap': self.HEADERS['MT-Token'],
            'YX_SUPPORT_WEBP': '1',
        }
        timestamp_ms = int(time.time() * 1000)
        dict.update(self.HEADERS, {"MT-K": f'{timestamp_ms}'})
        dict.update(self.HEADERS, {"MT-Request-ID": f'{timestamp_ms}{random.randint(10000, 99999)}'})
        response = requests.post('https://h5.moutai519.com.cn/game/isolationPage/getUserEnergyAward', cookies=cookies,
                                 headers=self.HEADERS, json={})
        # response.json().get('message') if '无法领取奖励' in response.text else "领取奖励成功"
        msg = f'领取耐力 : mobile:{mobile} :  response code : {response.status_code}, response body : {response.text}'
        return {"name": "小茅运", "value": msg}

    # 获取预约申购详情
    def getReservationDetail(self, reservationId: int) -> dict:
        resMsg = {"name": " * 申购详情", "value": ''}
        resMsgValue = '\n\t'
        timestamp_ms = int(time.time() * 1000)
        dict.update(self.HEADERS, {"MT-K": f'{timestamp_ms}'})
        dict.update(self.HEADERS, {"MT-Request-ID": f'{timestamp_ms}{random.randint(10000, 99999)}'})
        try:
            resQueryList = requests.get(
                'https://app.moutai519.com.cn/xhr/front/mall/reservation/detail/query?reservationId=' + str(
                    reservationId),
                headers=self.HEADERS)
            if 200 != resQueryList.status_code:
                msg = '请求申购详情失败(status_code=' + str(resQueryList.status_code) + ')'
                print_now(msg)
                resMsgValue += msg
                resMsg['value'] = resMsgValue
                return resMsg
            resQueryJson = resQueryList.json()
            resQueryCode = resQueryJson['code']
            if 2000 != resQueryCode:
                msg = '解析申购详情失败(code=' + str(resQueryCode) + ')'
                print_now(msg)
                resMsgValue += msg
                resMsg['value'] = resMsgValue
                return resMsg
            resQueryData = resQueryJson['data']
            msg = '状态: '
            status = resQueryData['status']
            if 0 == status:
                msg += '结果待公布'
            elif 1 == status:
                msg += '结果已公布'
            else:
                msg += '未知'
            msg += '\n\t'

            msg += '商品: '
            itemVOList = resQueryData['itemVOList']
            for itemVO in itemVOList:
                title = itemVO.get('title')
                price = itemVO.get('price')
                count = itemVO.get('count')
                msg += title + ', 价格:' + str(price) + ', 数量:' + str(count)
                msg += '\n\t'
            msg += '店铺: '
            shopVO = resQueryData['shopVO']
            msg += shopVO['name'] + ', 地址:' + shopVO['fullAddress']
            msg += '\n\t'

            resMsgValue += msg
            resMsg['value'] = resMsgValue
        except:
            msg = "请求失败 最大可能是token失效了 也可能是网络问题"
            print_now(msg)
            resMsgValue += msg
            resMsg['value'] = resMsgValue
        return resMsg

    # 获取预约申请信息列表
    def getReservationList(self) -> dict:
        resMsg = {"name": " * 申购结果", "value": ''}
        resMsgValue = '\n\t'
        timestamp_ms = int(time.time() * 1000)
        dict.update(self.HEADERS, {"MT-K": f'{timestamp_ms}'})
        dict.update(self.HEADERS, {"MT-Request-ID": f'{timestamp_ms}{random.randint(10000, 99999)}'})
        try:
            resQueryList = requests.get('https://app.moutai519.com.cn/xhr/front/mall/reservation/list/pageOne/queryV2',
                                        headers=self.HEADERS)
            if 200 != resQueryList.status_code:
                msg = '请求申购列表失败(status_code=' + str(resQueryList.status_code) + ')'
                print_now(msg)
                resMsgValue += msg
                resMsg['value'] = resMsgValue
                return resMsg
            resQueryCode = resQueryList.json()['code']
            if 2000 != resQueryCode:
                msg = '解析申购列表失败(code=' + str(resQueryCode) + ')'
                print_now(msg)
                resMsgValue += msg
                resMsg['value'] = resMsgValue
                return resMsg
            reservationItemVOS = resQueryList.json()['data']['reservationItemVOS']
            idx = 1
            # 当天
            cur_day_time_ms = int(time.mktime(datetime.date.today().timetuple()) * 1000)
            for reservationItem in reservationItemVOS:
                reserveStartTime = reservationItem.get('reserveStartTime')
                if reserveStartTime < cur_day_time_ms:
                    continue
                reservationId = reservationItem.get('reservationId')
                resReservationDetail = self.getReservationDetail(reservationId)
                resMsgValue += str(idx) + '-' + resReservationDetail['name']
                resMsgValue += resReservationDetail['value'] + '\n\t'
                idx += 1
            if 1 == idx:
                resMsgValue = '今日还未申购！！！'
            resMsg['value'] = resMsgValue
        except Exception as e:
            print_now(e)
            msg = "请求失败 最大可能是token失效了 也可能是网络问题"
            print_now(msg)
            resMsgValue += msg
            resMsg['value'] = resMsgValue
        return resMsg

    def main(self, param_type: int):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = "申购预约任务\n" + now + '\n'

        if 1 == param_type:
            time_now = datetime.datetime.now().time()
            if datetime.time(9, 00) > time_now or time_now > datetime.time(10, 00):
                msg += '不在申购时间段内'
                return msg

            # 获取当日session id
            self.get_current_session_id()

            for check_user in self.check_items:
                self.MOBILE = check_user.get('mobile')
                self.TOKEN = check_user.get('token')
                self.USER_ID = check_user.get('userId')
                self.DEVICE_ID = check_user.get('deviceId')
                province = check_user.get('province')
                city = check_user.get('city')
                lat = check_user.get('lat')
                lng = check_user.get('lng')

                msg_user = [
                    {
                        "name": " * 手机号",
                        "value": f"{self.MOBILE}",
                    },
                    {
                        "name": " * 省份城市",
                        "value": f"{province}{city}",
                    },
                ]

                p_c_map, source_data = self.get_shop_data(lat=lat, lng=lng)
                self.initHeaders(user_id=str(self.USER_ID), token=self.TOKEN, lat=lat, lng=lng)
                # 根据配置中，要预约的商品ID，城市 进行自动预约
                try:
                    for item in self.ITEM_CODES:
                        max_shop_id = self.get_location_count(province=province, city=city, item_code=item,
                                                              p_c_map=p_c_map,
                                                              source_data=source_data, lat=lat, lng=lng)
                        print_now(f'max shop id : {max_shop_id}')
                        if max_shop_id == '0':
                            continue
                        shop_info = source_data.get(str(max_shop_id))
                        title = self.ITEM_MAP.get(item)
                        reservation_info = f'商品：{title}\n门店：{shop_info["name"]}'
                        print_now(reservation_info)
                        msg_user.append({
                            "name": "申购信息",
                            "value": reservation_info,
                        })
                        reservation_params = self.act_params(max_shop_id, item)
                        resReservation = self.reservation(reservation_params, self.MOBILE)
                        msg_user.append(resReservation)
                        resAward = self.getUserEnergyAward(self.MOBILE)
                        msg_user.append(resAward)
                except BaseException as e:
                    print_now(e)
                    msg_user.append(
                        {
                            "name": "申购结果",
                            "value": self.MOBILE + '申购预约失败\n' + e,
                        }
                    )
                msg_user = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg_user])
                msg += msg_user + '\n\n'
        elif 2 == param_type:
            # 获取当日session id
            self.get_current_session_id()

            for check_user in self.check_items:
                self.MOBILE = check_user.get('mobile')
                self.TOKEN = check_user.get('token')
                self.USER_ID = check_user.get('userId')
                self.DEVICE_ID = check_user.get('deviceId')
                province = check_user.get('province')
                city = check_user.get('city')
                lat = check_user.get('lat')
                lng = check_user.get('lng')

                msg_user = [
                    {
                        "name": " * 手机号",
                        "value": f"{self.MOBILE}",
                    },
                    {
                        "name": " * 省份城市",
                        "value": f"{province}{city}",
                    },
                ]

                self.initHeaders(user_id=str(self.USER_ID), token=self.TOKEN, lat=lat, lng=lng)
                resReservation = self.getReservationList()
                msg_user.append(resReservation)
                msg_user = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg_user])
                msg += msg_user + '\n\n'
        else:
            msg += "运行参数错误,param_type=" + str(param_type)
        return msg


if __name__ == '__main__':
    if len(argv) < 2:
        param = 1
    else:
        param = int(argv[1])
    data = get_data()
    _check_items = data.get("IMAOTAI", [])
    if len(_check_items) < 1:
        send("i茅台", "IMAOTAI配置错误")
        exit(0)
    # _check_items = [{
    #     'mobile': '1',
    #     'token': '1.1.1',
    #     'userId': 1,
    #     'deviceId': '1',
    #     'province': '天津市',
    #     'city': '天津市',
    #     'lat': '39.086789',
    #     'lng': '117.313567',
    # }]
    result = IMaoTai(check_items=_check_items).main(param)
    send("i茅台", result)
    # result = IMaoTai(check_items=_check_items).main(2)
    # print_now(result)
    exit(0)
