import threading
import time
from datetime import datetime, date
from typing import Dict, Optional, List
import requests
import json
import yaml
import multiprocessing
from loguru import logger

NETWORK_TIME_URL = "http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp"
BASE_URL = (
    "https://h5.gumingnc.com/newton-buyer/newton/buyer/ump/milk/tea/activity/fcfs"
)
DEFAULT_HEADERS: Dict[str, str] = {
    "host": "h5.gumingnc.com",
    "content-length": "109",
    "t-token": "tWPHd1721229807WtnhbUCAXp3",
    "cache-control": "max-age=0",
    "authorization": "",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b11)XWEB/9185",
    "content-type": "application/json",
    "accept": "*/*",
    "origin": "https://h5.gumingnc.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://h5.gumingnc.com/",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
}
BASE_DATA: Dict[str, int] = {
    "channelCode": 20,
    "activityId": 14,
    "brandId": 1,
    "keyWordAnswer": "乌龙青",
    "consumptionInventoryId": 332319846,
}


class Seckkiller:
    def __init__(
        self,
        cookie_id: str,
        start_time: datetime.time,
        account_name: Optional[str] = None,
        max_attempts: int = 10,
        thread_count: int = 1,
    ):
        self.cookie_id: str = cookie_id
        self._headers: Dict[str, str] = {**DEFAULT_HEADERS, "cookie": cookie_id}
        self._data: Dict[str, int] = BASE_DATA
        self.max_attempts: int = max_attempts
        self.attempts: int = 0
        self.account_name: Optional[str] = account_name
        self.stop_flag: threading.Event = threading.Event()
        self.thread_count: int = thread_count
        self.start_time: datetime.time = start_time

    def post_seckill_url(self) -> None:
        try:
            response = requests.post(
                BASE_URL,
                headers=self._headers,
                data=json.dumps(self._data),
            )
            response_data = response.json()
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

    def wait_for_start_time(self) -> None:
        while True:
            current_time = self.get_network_time()
            if current_time >= self.start_time:
                logger.info(f"[{self.account_name}] Starting seckill...")
                break
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
        self.account_cookie_map: Dict[str, str] = self.load_config()

    def load_config(self) -> Dict[str, str]:
        with open(self.config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)["Cookies"]

    def worker(self, account_name: str, cookie_id: str) -> None:
        seckkiller = Seckkiller(cookie_id, self.start_time, account_name)
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
    start_time = "23:14:59.850"  # 设置开始时间
    main(start_time)
