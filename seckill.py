import threading
import time
from datetime import datetime, date
from typing import Dict, Optional, List
import requests
import json
import yaml
import multiprocessing
from loguru import logger
import random
import hashlib

NETWORK_TIME_URL = "http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp"
BASE_URL = "https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm"
PROXY_URL = ""  # 替换为实际的代理IP获取API
DEFAULT_HEADERS: Dict[str, str] = {
    "host": "mxsa.mxbc.net",
    "content-length": "140",
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13)XWEB/9193",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://mxsa-h5.mxbc.net",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://mxsa-h5.mxbc.net/",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
}
BASE_DATA: Dict[str, int] = {
    "marketingId": "1816854086004391938",
    "round": "13:00",
    "secretword": "1",
    "sign": "f185a655dba3ce0d570f3fe83ee1b4b7",
    "s": 2,
    "stamp": 1722319027399,
}


class Seckkiller:

    def __init__(
        self,
        cookie_id: str,
        start_time: datetime.time,
        account_name: Optional[str] = None,
        max_attempts: int = 1,
        thread_count: int = 1,
        use_encryption: bool = False,
        encryption_params: Optional[Dict[str, str]] = None,
    ):
        self.cookie_id: str = cookie_id
        self._headers: Dict[str, str] = {**DEFAULT_HEADERS, "Access-Token": cookie_id}
        self._data: Dict[str, int] = BASE_DATA
        self.max_attempts: int = max_attempts
        self.attempts: int = 0
        self.account_name: Optional[str] = account_name
        self.stop_flag: threading.Event = threading.Event()
        self.thread_count: int = thread_count
        self.start_time: datetime.time = start_time
        self.proxy_list: List[Dict[str, str]] = []
        self.use_encryption: bool = use_encryption
        self.encryption_params: Optional[Dict[str, str]] = encryption_params

    def encrypt_data(self, current_time: datetime) -> None:
        if not self.use_encryption or not self.encryption_params:
            return

        marketingId = self.encryption_params.get("marketingId", "")
        round = self.encryption_params.get("round", "")
        secretword = self.encryption_params.get("secretword", "")
        timestamp = int(current_time.timestamp() * 1000)

        param = f"marketingId={marketingId}&round={round}&s=2&secretword={secretword}&stamp={timestamp}c274bac6493544b89d9c4f9d8d542b84"
        logger.debug(f"[{self.account_name}] Encryption param: {param}")
        m = hashlib.md5(param.encode("utf8"))
        sign = m.hexdigest()

        self._data.update(
            {
                "marketingId": marketingId,
                "round": round,  #   # 毫秒级时间戳
                "sign": sign,
                "secretword": secretword,
                "stamp": timestamp,
            }
        )

    def post_seckill_url(self) -> None:
        try:
            proxy = random.choice(self.proxy_list) if self.proxy_list else None
            proxies = (
                {
                    "http": f"http://{proxy['ip']}:{proxy['port']}",
                }
                if proxy
                else None
            )
            logger.debug(f"[{self.account_name}]Using proxy: {proxies}")
            current_time = datetime.now()
            if self.use_encryption:
                self.encrypt_data(current_time)
            response = requests.post(
                BASE_URL,
                headers=self._headers,
                data=json.dumps(self._data),
                proxies=proxies,
            )
            print(response.text)
            response_data = response.json()
            logger.debug(f"[{self.account_name}]Response: {response_data}")
            logger.debug(
                f"[{self.account_name}]Response: {response_data.get('msg', 'No message')}"
            )
            if "success" in response_data.get("msg", "").lower():
                self.stop_flag.set()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
        self.attempts += 1
        if self.attempts >= self.max_attempts:
            self.stop_flag.set()

    def start_seckill(self) -> None:
        self.wait_for_start_time()
        while not self.stop_flag.is_set():
            self.post_seckill_url()
            time.sleep(0.1)  # 避免请求过于频繁

    @staticmethod
    def get_network_time() -> datetime.time:
        try:
            response = requests.get(NETWORK_TIME_URL)
            res = response.json()
            now_time = int(res["data"]["t"]) / 1000.0
            return datetime.fromtimestamp(now_time).time()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return datetime.now().time()

    @staticmethod
    def get_proxy_ips() -> List[Dict[str, str]]:
        try:
            response = requests.get(PROXY_URL)
            data = response.json()
            if data["success"] and data["code"] == 0:
                return data["data"]
            else:
                logger.error(f"Failed to get proxy IP9s: {data['msg']}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get proxy IPs: {e}")
            return []

    def wait_for_start_time(self) -> None:
        while True:
            current_time = self.get_network_time()
            if current_time >= self.start_time:
                logger.info(f"[{self.account_name}] Starting seckill...")
                break
            # 在等待期间获取代理IP
            if not self.proxy_list:
                self.proxy_list = self.get_proxy_ips()
                if self.proxy_list:
                    logger.info(
                        f"[{self.account_name}] Got {len(self.proxy_list)} proxy IPs"
                    )
            time.sleep(0.01)  # 小的睡眠时间以避免过度消耗CPU

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


class SeckillManager:
    def __init__(self, config_file: str, start_time: str):
        self.config_file: str = config_file
        self.start_time: datetime.time = datetime.strptime(
            start_time, "%H:%M:%S.%f"
        ).time()
        self.config: Dict = self.load_config()
        self.account_cookie_map: Dict[str, str] = self.config.get("Cookies", {})

    def load_config(self) -> Dict:
        with open(self.config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def worker(self, account_name: str, cookie_id: str) -> None:
        use_encryption = self.config.get("use_encryption", False)
        encryption_params = None
        if use_encryption:
            encryption_params = {
                "marketingId": self.config.get("marketingId", ""),
                "round": self.config.get("round", ""),  # 使用cookie作为token
                "secretword": self.config.get("secretword", ""),
            }

        seckkiller = Seckkiller(
            cookie_id,
            self.start_time,
            account_name,
            use_encryption=use_encryption,
            encryption_params=encryption_params,
        )
        seckkiller.run()

    def print_remaining_time(self) -> None:
        while True:
            current_time = Seckkiller.get_network_time()
            remaining_seconds = (
                datetime.combine(date.today(), self.start_time)
                - datetime.combine(date.today(), current_time)
            ).total_seconds()
            if remaining_seconds <= 0:
                logger.info("Time is up! All processes should start seckill...")
                break
            logger.info(f"Remaining time: {remaining_seconds:.2f} seconds")
            time.sleep(0.5)

    def run(self) -> None:
        timer_process = multiprocessing.Process(target=self.print_remaining_time)
        timer_process.start()

        processes: List[multiprocessing.Process] = []
        for account_name, cookie_id in self.account_cookie_map.items():
            p = multiprocessing.Process(
                target=self.worker, args=(account_name, cookie_id)
            )
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        timer_process.terminate()
        timer_process.join()


def main(start_time: str, config_file: str = "cookie.yaml") -> None:
    manager = SeckillManager(config_file, start_time)
    manager.run()


if __name__ == "__main__":
    start_time = "20:53:00.000"  # 设置开始时间
    main(start_time)
