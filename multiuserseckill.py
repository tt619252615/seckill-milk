import threading
import time
from datetime import datetime, date
from typing import Dict, Optional, List
from curl_cffi import requests
import json
import yaml
import multiprocessing
from loguru import logger
import random
import execjs
import hashlib


class Seckkiller:

    def __init__(
        self,
        cookie_id: str,
        cooke_name: str,
        headers: Dict[str, str],
        data: Dict[str, int],
        base_url: str,
        proxy_url: str,
        start_time: datetime.time,
        account_name: Optional[str] = None,
        max_attempts: int = 1,
        thread_count: int = 1,
        key_value: Optional[Dict[str, str]] = None,
        use_encryption: bool = False,
        encryption_params: Optional[Dict[str, str]] = None,
        proxy_flag: bool = False,
    ):
        self.cookie_id: str = cookie_id
        self.cooke_name: str = cooke_name
        self._headers: Dict[str, str] = {**headers, self.cooke_name: cookie_id}
        self._data: Dict[str, int] = data
        self._base_url: str = base_url
        self._proxy_url: str = proxy_url
        self.max_attempts: int = max_attempts
        self.attempts: int = 0
        self.key_value: Optional[Dict[str, str]] = key_value
        self.account_name: Optional[str] = account_name
        self.stop_flag: threading.Event = threading.Event()
        self.thread_count: int = thread_count
        self.start_time: datetime.time = start_time
        self.proxy_list: List[Dict[str, str]] = []
        self.use_encryption: bool = use_encryption
        self.encryption_params: Optional[Dict[str, str]] = encryption_params
        self.proxy_flag: bool = proxy_flag
        if self.use_encryption:
            with open("./js/mixue.js", "r", encoding="utf-8") as js_file:
                self.encryption_js = execjs.compile(js_file.read())

    def encrypt_data(self, current_time: datetime) -> None:
        if not self.use_encryption or not self.encryption_params:
            return

        marketingId = self.encryption_params.get("marketingId", "")
        round = self.encryption_params.get("round", "")
        secretword = self.encryption_params.get("secretword", "")
        timestamp = int(current_time.timestamp() * 1000)
        param = f"marketingId={marketingId}&round={round}&s=2&secretword={secretword}&stamp={timestamp}c274bac6493544b89d9c4f9d8d542b84"
        m = hashlib.md5(param.encode("utf8"))
        sign = m.hexdigest()
        mixue_data = {
            "marketingId": "1816854086004391938",
            "round": "13:00",
            "secretword": "1",
            "sign": "f185a655dba3ce0d570f3fe83ee1b4b7",
            "s": 2,
            "stamp": 1722319027399,
        }
        mixue_data.update(
            {
                "marketingId": marketingId,
                "round": round,
                "secretword": secretword,
                "sign": sign,
                "stamp": timestamp,
            }
        )
        encrypted_str = f'https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm{{"marketingId":"{marketingId}","round":"{round}","secretword":"{secretword}","sign":"{sign}","s":2,"stamp":{timestamp}}}'
        encrypted_str = self.encryption_js.call("get_sig", encrypted_str)
        return encrypted_str, mixue_data

    def post_seckill_url(self) -> None:
        while self.attempts < self.max_attempts and not self.stop_flag.is_set():
            proxy = random.choice(self.proxy_list) if self.proxy_list else None
            proxies = (
                f"http://{proxy['ip']}:{proxy['port']}"
                if proxy and self.use_encryption
                else (
                    {
                        "http": f"http://{proxy['ip']}:{proxy['port']}",
                        "https": f"http://{proxy['ip']}:{proxy['port']}",
                    }
                    if proxy
                    else None
                )
            )

            logger.debug(f"[{self.account_name}] Using proxy: {proxies}")
            try:
                if self.use_encryption:
                    type_1286, self._data = self.encrypt_data(datetime.now())
                    self._base_url = f"https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm?type__1286={type_1286}"
                # logger.debug(f"[{self.account_name}] Request: {self._data}")
                # logger.debug(f"[{self.account_name}] URL: {self._base_url}")
                # logger.debug(f"[{self.account_name}] Headers: {self._headers}")
                # logger.debug(f"[{self.account_name}] Proxies: {proxies}")
                response = requests.post(
                    self._base_url,
                    headers=self._headers,
                    data=json.dumps(
                        self._data, separators=(",", ":"), ensure_ascii=False
                    ),
                    impersonate="chrome100",
                    proxy=proxies,
                    timeout=1,
                )
                try:
                    # print(response.text)
                    response_data = response.json()
                    message = response_data.get("msg", "")
                except json.JSONDecodeError as json_err:
                    logger.error(f"Failed to decode JSON response: {json_err}")
                    response_data = None

                if response_data:
                    logger.debug(f"[{self.account_name}] Response: {message}")
                    if self.key_value in response_data.get("msg", "").lower():
                        logger.info(
                            f"[{self.account_name}] Successfully completed the request."
                        )
                        self.stop_flag.set()
                        break
                    else:
                        logger.warning(
                            f"[{self.account_name}] Unexpected response: {message}"
                        )

            except Exception as e:
                logger.error(f"Request failed: {e}")

            self.attempts += 1
            logger.info(
                f"Attempt {self.attempts}/{self.max_attempts} failed. Retrying..."
            )

        if not self.stop_flag.is_set():
            logger.error(
                f"Reached maximum attempts ({self.max_attempts}). Stopping requests."
            )
            self.stop_flag.set()

    def start_seckill(self) -> None:
        self.wait_for_start_time()
        while not self.stop_flag.is_set():
            self.post_seckill_url()
            time.sleep(0.1)  # 避免请求过于频繁

    @staticmethod
    def get_network_time() -> datetime.time:
        NetworkTimeUrl = (
            "http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp"
        )
        try:
            response = requests.get(
                NetworkTimeUrl,
                impersonate="chrome100",
            )
            res = response.json()
            now_time = int(res["data"]["t"]) / 1000.0
            return datetime.fromtimestamp(now_time).time()
        except requests.errors.RequestsError as e:
            logger.error(f"Request failed: {e}")
            return datetime.now().time()

    def get_proxy_ips(self) -> List[Dict[str, str]]:
        if self.proxy_flag == False:
            logger.info(f"[{self.account_name}] Using proxy IP9s")
            return []
        else:
            try:
                response = requests.get(
                    self._proxy_url,
                    impersonate="chrome100",
                )
                data = response.json()
                if data["success"] and data["code"] == 0:
                    return data["data"]
                else:
                    logger.error(f"Failed to get proxy IP9s: {data['msg']}")
                    return []
            except requests.errors.RequestsError as e:
                logger.error(f"Failed to get proxy IPs: {e}")
                return []

    def wait_for_start_time(self) -> None:
        proxy_fetch_interval = 5  # 设置获取代理 IP 的间隔时间（秒）
        last_proxy_fetch_time = 0
        proxy_fetch_failed = False  # 新增标志，用于记录代理获取是否失败

        while True:
            current_time = Seckkiller.get_network_time()
            if current_time >= self.start_time:
                logger.info(f"[{self.account_name}] Starting seckill...")
                break

            # 检查是否需要获取代理 IP
            current_timestamp = time.time()
            if (
                not self.proxy_list
                and not proxy_fetch_failed  # 只有在之前没有失败时才尝试获取
                and current_timestamp - last_proxy_fetch_time > proxy_fetch_interval
            ):
                self.proxy_list = self.get_proxy_ips()
                last_proxy_fetch_time = current_timestamp
                if self.proxy_list:
                    logger.info(
                        f"[{self.account_name}] Got {len(self.proxy_list)} proxy IPs"
                    )
                else:
                    logger.info(
                        f"[{self.account_name}] No proxy IPs available, will use local IP"
                    )
                    proxy_fetch_failed = True  # 标记获取失败，后续不再尝试

            time.sleep(0.01)

    def run(self) -> None:
        logger.info(f"[{self.account_name}] Waiting for start time: {self.start_time}")
        seckill_threads: List[threading.Thread] = []
        for _ in range(self.thread_count):
            t = threading.Thread(target=self.start_seckill)
            t.start()
            seckill_threads.append(t)

        for t in seckill_threads:
            t.join()

        logger.info(f"[{self.account_name}] Seckill finished")