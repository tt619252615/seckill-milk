"""
description: This is file for encrytion post data or get parameter
author: chengzhi
date: 2024
"""

from abc import ABC, abstractmethod
import requests
import json
import hashlib
import execjs
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from loguru import logger
from urllib.parse import urlparse, parse_qs
import hashlib
import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib.parse


class Encryptor:
    """
    description: Encryptor class for encrypt

    agrs:
        flag: flag for encryptor.
    methods:
        encrypt: encrypt the data with the specified method and return the encrypted string and related data
    """

    def __init__(self, flag: Optional[str] = None):
        """
        description: Initialize the Encryptor class.
        Flage means to choose the encryption method.
        encryption_js is a function that loads the encryption js file and returns the execjs object.

        agrs:
            flag: flag for encryptor.
        """
        self.flag = flag
        self.encryption_js = self.load_encryption_js

    def load_encryption_js(self):
        with open("./js/mixue.js", "r", encoding="utf-8") as js_file:
            return execjs.compile(js_file.read())

    def encrypt(
        self, method: str, params: Dict[str, Any], current_time: datetime
    ) -> Tuple[str, Dict[str, Any]]:
        encrypt_method = getattr(self, f"encrypt_{method}", None)
        if not encrypt_method:
            raise ValueError(f"Unknown encryption method: {method}")
        return encrypt_method(params, current_time)

    def encrypt_mixue(
        self, params: Dict[str, Any], current_time: datetime
    ) -> Tuple[str, Dict[str, Any]]:
        marketingId = params.get("marketingId", "")
        round = params.get("round", "")
        secretword = params.get("secretword", "")
        timestamp = int(current_time.timestamp() * 1000)
        param = f"marketingId={marketingId}&round={round}&s=2&secretword={secretword}&stamp={timestamp}c274bac6493544b89d9c4f9d8d542b84"
        sign = Encryptor.foundation_md5(param)
        mixue_data = {
            "marketingId": marketingId,
            "round": round,
            "secretword": secretword,
            "sign": sign,
            "s": 2,
            "stamp": timestamp,
        }

        encrypted_str = f'https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm{{"marketingId":"{marketingId}","round":"{round}","secretword":"{secretword}","sign":"{sign}","s":2,"stamp":{timestamp}}}'
        encrypted_str = self.encryption_js.call("get_sig", encrypted_str)

        return encrypted_str, mixue_data

    @staticmethod
    def encrypt_kudi(current_time: datetime) -> Tuple[str, Dict[str, Any]]:
        """
        description: kudi encryption method.
        """
        kudi_params = f"path/cotti-capi/universal/coupon/receiveLaunchRewardH5timestamp{current_time}versionv1Bu0Zsh4B0SnKBRfds0XWCSn51WJfn5yN"
        sign = Encryptor.foundation_md5(kudi_params).upper()
        return sign

    @staticmethod
    def foundation_md5(params: Dict[str, Any]) -> str:
        """
        description: foundation md5 encryption method.
        """
        md5 = hashlib.md5()
        md5.update(params.encode("utf-8"))
        return md5.hexdigest()


class RequestStrategy(ABC):
    @abstractmethod
    def prepare_request(
        self, current_time: datetime, data: Dict, headers: Dict, base_url: str
    ) -> tuple:
        pass

    @abstractmethod
    def process_response(self, response: requests.Response) -> Dict:
        pass


class DefaultRequestStrategy(RequestStrategy):
    def prepare_request(
        self, current_time: datetime, data: Dict, headers: Dict, base_url: str
    ) -> tuple:
        process_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        return base_url, process_data, headers

    def process_response(self, response: requests.Response) -> Dict:
        return response.json()


class QCSRequestStrategy(RequestStrategy):
    def prepare_request(
        self, current_time: datetime, data: Dict, headers: Dict, base_url: str
    ) -> tuple:
        process_data = json.dumps(data)
        return base_url, data, headers

    def process_response(self, response: requests.Response) -> Dict:
        return response.json()


class BwRequestStrategy(RequestStrategy):
    def __init__(self, bw_keywords: str) -> None:
        self._current_kw_index = 0
        self._key_words = bw_keywords

    def _get_current_keyword(self, keywords_str: str) -> str:
        keywords_list = [kw.strip() for kw in keywords_str.split(",")]
        if self._current_kw_index >= len(keywords_list):
            self._current_kw_index = 0
        kw = keywords_list[self._current_kw_index]
        self._current_kw_index += 1
        return kw

    def _build_signature(self, activity_id: str, user_id: str, timestamp: str) -> str:
        key = activity_id[::-1]
        signature_str = f"activityId={activity_id}&sellerId=49006&timestamp={timestamp}&userId={user_id}&key={key}"
        return Encryptor.foundation_md5(signature_str).upper()

    def _encrypt_request_data(self, request_data: Dict, key: str, iv: str) -> str:
        json_data = json.dumps(request_data, ensure_ascii=False, separators=(",", ":"))
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
        padded_data = pad(json_data.encode("utf-8"), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        return b64encode(encrypted_data).decode("utf-8")

    def _get_encryption_params(self, process_data: Dict) -> str:
        url = "http://192.168.31.186:3001/api/encrypt"
        payload = json.dumps(process_data)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=payload)
        params = response.json().get("data", {}).get("encrypted")
        if not params:
            raise ValueError("Encryption failed - no result returned")
        return params

    def prepare_request(
        self, current_time: datetime, data: Dict, headers: Dict, base_url: str
    ) -> tuple:
        kw = self._get_current_keyword(self._key_words)
        activity_id = data.get("activityId")
        signature = self._build_signature(activity_id, data.get("userId"), current_time)

        request_data = {
            "activityId": activity_id,
            "keyWords": kw,
            "qzGtd": "",
            "gdtVid": "",
            "appid": "wxafec6f8422cb357b",
            "timestamp": current_time,
            "signature": signature,
        }
        encrypted_data = self._encrypt_request_data(
            request_data, data.get("key"), data.get("iv")
        )

        process_data = {
            **request_data,
            "data": encrypted_data,
            "version": data.get("version"),
        }
        params = self._get_encryption_params(process_data)

        process_url = f"{base_url}?type__1475={params}"
        process_data = json.dumps(
            process_data, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return process_url, process_data, headers

    def process_response(self, response: requests.Response) -> Dict:
        return response.json()

    def process_keywords(self, keywords):
        # 如果输入是字符串，先按逗号分割成列表
        if isinstance(keywords, str):
            keywords_list = [kw.strip() for kw in keywords.split(",")]
        # 如果输入是列表，直接使用
        elif isinstance(keywords, list):
            keywords_list = keywords
        else:
            raise ValueError("关键词格式不正确")

        # 返回处理后的关键词字符串
        return ",".join(keywords_list)


class TestIpRequestStrategy(RequestStrategy):
    def prepare_request(
        self, current_time: datetime, data: Dict, headers: Dict, base_url: str
    ) -> tuple:
        process_data = json.dumps(data)
        base_url = "http://httpbin.org/ip"
        return base_url, data, headers

    def process_response(self, response: requests.Response) -> Dict:
        return response.json()


class MixueEncryptionStrategy(RequestStrategy):
    def __init__(self, encryption_params: Dict[str, str]):
        self.encryption_params = encryption_params or {}
        with open("./js/mixue.js", "r", encoding="utf-8") as js_file:
            self.encryption_js = execjs.compile(js_file.read())

    def prepare_request(
        self, current_time: datetime, data: Dict, headers: Dict, base_url: str
    ) -> tuple:
        marketingId = self.encryption_params.get("marketingId", "")
        round = self.encryption_params.get("round", "")
        secretword = self.encryption_params.get("secretword", "")
        timestamp = int(current_time.timestamp() * 1000)

        param = f"marketingId={marketingId}&round={round}&s=2&secretword={secretword}&stamp={timestamp}c274bac6493544b89d9c4f9d8d542b84"
        m = hashlib.md5(param.encode("utf8"))
        sign = m.hexdigest()

        mixue_data = {
            "marketingId": marketingId,
            "round": round,
            "secretword": secretword,
            "sign": sign,
            "s": 2,
            "stamp": timestamp,
        }

        encrypted_str = f'https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm{{"marketingId":"{marketingId}","round":"{round}","secretword":"{secretword}","sign":"{sign}","s":2,"stamp":{timestamp}}}'
        encrypted_str = self.encryption_js.call("get_sig", encrypted_str)

        new_url = f"{base_url}?type__1286={encrypted_str}"
        return new_url, mixue_data, headers

    def process_response(self, response: requests.Response) -> Dict:
        return response.json()


class JDRequestStrategy(RequestStrategy):
    def prepare_request(
        self, current_time: datetime, data: Dict, headers: Dict, base_url: str
    ) -> tuple:
        return base_url, data, headers

    def process_response(self, response: requests.Response) -> Dict:
        res = response.json()
        if "data" in res:
            return res["data"]
        else:
            return res


class KuDiEncryptionStrategy(RequestStrategy):
    def __init__(self, encryption_params: Dict):
        self.encryption_params = encryption_params or {}

    def prepare_request(
        self, current_time: datetime, data: Dict, headers: Dict, base_url: str
    ) -> Tuple[str, Dict, Dict]:
        timestamp = int(current_time.timestamp() * 1000)
        encrypted_sign = Encryptor.encrypt_kudi(timestamp)
        headers["sign"] = encrypted_sign
        headers["timestamp"] = str(timestamp)
        data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        # print(data)
        return base_url, data, headers

    def process_response(self, response: requests.Response) -> Dict:
        res = response.json()
        return res["data"]


class MTEncryptionStrategy(RequestStrategy):
    def __init__(self, encryption_params: Dict):
        self.encryption_params = encryption_params or {}
        self.flage = ""

    def prepare_request(
        self, current_time: datetime, data: Dict, headers: Dict, base_url: str
    ) -> Tuple[str, Dict, Dict]:
        data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        return base_url, data, headers

    def process_response(self, response: requests.Response) -> Dict:
        res = response.json()["data"]["coupon"]
        return res

    def _get_couponId(self, basurl):
        return basurl.split("couponReferIds=")[1].split("&")[0]

    @staticmethod
    def get_coupon_info(headers: Dict, basurl: str):
        # couponId = basurl.split("couponReferIds=")[1].split("&")[0]
        # print(couponId)
        parsed_url = urlparse(basurl)
        query_params = parse_qs(parsed_url.query)
        couponId = query_params.get("couponReferId")[0]
        cookie = headers["cookie"]
        URL1 = "https://promotion.waimai.meituan.com/lottery/limitcouponcomponent/info?couponReferIds={}&actualLng=118.33515&actualLat=35.04518&geoType=2".format(
            couponId
        )
        headers_temp = {
            "dj-token": "",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; MI 6 Build/TQ2A.230405.003.E1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615.136 Mobile Safari/537.36 TitansX/12.9.1 KNB/1.2.0 android/13 mt/com.sankuai.meituan/12.9.404 App/10120/12.9.404 MeituanGroup/12.9.404",
            "Content-Type": "application/json",
            "X-Requested-With": "com.sankuai.meituan",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "mtgsig": "",
            "Sec-Fetch-Dest": "empty",
            "Cookie": cookie,
        }
        # logger.info(f"URL1: {headers}")
        response = requests.get(url=URL1, headers=headers_temp)
        # self.flage = response.json().get("msg", {})
        # print(self.flage)
        if response.status_code == 200:
            return response.json()
        else:
            return None


class RequestStrategyManager:
    def __init__(self):
        self.strategies = {
            None: DefaultRequestStrategy(),
            "QCS": QCSRequestStrategy(),
            "BW": BwRequestStrategy({}),
            "IP": TestIpRequestStrategy(),
            "mixue": MixueEncryptionStrategy({}),  # 初始化时传入空字典，后续可以更新
            "KuDi": KuDiEncryptionStrategy({}),
            "MT": MTEncryptionStrategy({}),
            "JD": JDRequestStrategy(),
        }

    def get_strategy(self, strategy_flag: Optional[str]) -> RequestStrategy:
        return self.strategies.get(strategy_flag, self.strategies[None])

    def update_strategy_params(self, strategy_flag: str, params: Optional[Dict] = None):
        if strategy_flag in self.strategies:
            strategy_class = type(self.strategies[strategy_flag])
            if params is not None:
                self.strategies[strategy_flag] = strategy_class(params)
            else:
                self.strategies[strategy_flag] = strategy_class()
