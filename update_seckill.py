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

NETWORK_TIME_URL = "http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp"
BASE_URL = "https://promotion.waimai.meituan.com/lottery/rights/limitcouponcomponent/fetchcoupon?couponReferId=4D21F6F549964FB2A7BA8FB6B3CA28CF&componentId=17225038407340.5619507582448298&geoType=2&gdPageId=569389&pageId=579967&version=1&instanceId=17225038407340.5619507582448298&clientTime=1723031635044&ctype=iphone&utmMedium=iphone&gSource=&dpSource=&utmCampaign=AwaimaiBwaimaiGhomepageH0&utmSource=2000&yodaReady=h5&csecplatform=4&csecversion=2.4.0"
PROXY_URL = ""  # 替换为实际的代理IP获取API
DEFAULT_HEADERS: Dict[str, str] = {
    "host": "promotion.waimai.meituan.com",
    "content-type": "application/json",
    "x-titans-user": "",
    "accept": "application/json, text/plain, */*",
    "sec-fetch-site": "same-site",
    "dj-token": "BUtNUwMAAABuBktNUwMaOQIAAAABO5rMWgAAACxUk3kku9S+/FhNj6KAztMR9mlxIrC/udidqTpxbVgrQKyl7zdA3lhQZFaStCIsUnufjX8Z5PNzxhhI04A3HgbglGIQxKdAqAdptaKNuxCiQdU66E0y4isjTQIAAABOkMzXIFagiklsGUBtTU/v1lBVFCuFIhJALoyznlBuBjeIx4AHPNv9VL3sInQ3LheLNtxhk8LSA2NwOcTdJf2noP4yBGzy+3BZTLqGw4+Q",
    "accept-language": "zh-CN,zh-Hans;q=0.9",
    "sec-fetch-mode": "cors",
    "accept-encoding": "gzip, deflate, br",
    "origin": "https://market.waimai.meituan.com",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 TitansX/20.0.1.old KNB/1.0 iOS/17.4.1 meituangroup/com.meituan.imeituan/12.23.407 meituangroup/12.23.407 App/10110/12.23.407 iPhone/iPhone12 WKWebView",
    "referer": "https://market.waimai.meituan.com/",
    "content-length": "1589",
    "mtgsig": '{"a0":"3.0","a1":"7db5788e-97df-40d7-a19c-1cb62ef9f257","a3":24,"a4":1723031635,"a5":"Wce20YcosXsNu0mTl+K1OhkSX5GppDSH5kpir3Wr2J2jFaDEzzFzNCJCw52RcqWRnnPL1hidS/HLC4MSVbufI2+tFl8sa2DGA3iqpLqjYmoIrkGNUPwAssyXhGDP6EtulTUswcPCAAF1JvUsMSfyWGSDGxL7bpNkup6MNsxyjQHrHJmpiTc41aHGRiWEYISCT3/JKSIthbcBNsPpmw1K8Zdacp8+B6kxiMaBqfefgLVVECN1H5kyHWLCNrp6lgrqCFEwxJ1xTcYIArlemOLfMB7yLjQ0qAqxuYtyHMoi1IX+WzLFkDM/Gv51Rp35hGrapvV8Hj49nW2v/eDH2vv5k/IgIAKRjEQOQ3kXHRg2HUf0qvZQLvBVi3NgQ8vnDsCWW9rIXjk3X4jktg==","a6":0,"a7":"EKCzRS4HIsWXc7NmgtOFeRIkzuuUaUn04ts8o+jTCK+t3cnUqUrlnen/7kEQUVP+R0jzrmyyzcLA9FoVocWknKYs6NdIz6f8uehpcfy6oRw=","a8":"664d21ec8cb8090c0c2c80f314d3bbb59217f6083b903830440c978e","a9":"33a6ca7aW6+v1Z0zloZOS00yU+LhoXdI86EoyoOJAbLIvHQ1A9ad8LiLCfsY/6/vzAdcci7DZ3O27eXzg5QOvG96bh7nUTDBuZ3A+MeJR57KOmK7Ww5MulXuPuBNVRgh9nDZi0tnbrb14ldpzaOnsQDuBI6x9dsHYgorkfYGDWyBEjOrPYK7+lzP/vh4HKaddj/mAA/J3WYvfxP7bsarBE2xwsddKU8eO95iMSQfU1Qf0rJdw/pZhSpokDRdZOwrrB3v4z+fcDtc7pTUuLrI9KnmZtOpvFH50ru3Y/Up6sp39TCjGmHhAtzF4JqsAfGVjbpMYQuzFERC+JM6S+GRjUKjilAsnrVt7HglB1l1UM9WSL1dh73Ukf0qJFp5j0PqzmrDbf0OaswyS30K+mQmUkSfi8PNMz4mrKHplOR21bePJl3HaB/6BC829LYxxHZn6qNLr0iSSDxB9RZrpXQ746xVUKppyehbVzHz/Yl5fymDEqMJhm7I371vYam0EdYPsyfB36Drh/mEotKlkFgEc9gE4+HdBYVWEDDllRWflKhWfdEuUdc9vv0UsVESowiSERop5Yh2wzuFHLVZ6zj6pVUNfybn6JK+ENbZwb+23AbxtcONFt83YILnqzbSfr1bry7SEZo6qklFIXzqGCop/dSmQ/MVyw==","a10":"5,78,1.1.6","x0":2,"a2":"7a80a34d625ad118af38aae7bd3a17a8"}',
    "sec-fetch-dest": "empty",
}
BASE_DATA: Dict[str, int] = {
    "cType": "iphone",
    "fpPlatform": 5,
    "wxOpenId": "",
    "appVersion": "8.32.0",
    "mtFingerprint": "dfp_6.5.16_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",
}


class Seckkiller:

    def __init__(
        self,
        cookie_id: str,
        start_time: datetime.time,
        account_name: Optional[str] = None,
        max_attempts: int = 1,
        thread_count: int = 1,
        key_value: Optional[Dict[str, str]] = None,
        use_encryption: bool = False,
        encryption_params: Optional[Dict[str, str]] = None,
    ):
        self.cookie_id: str = cookie_id
        self._headers: Dict[str, str] = {**DEFAULT_HEADERS, "cookie": cookie_id}
        self._data: Dict[str, int] = BASE_DATA
        self._base_url: str = BASE_URL
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
                    BASE_URL = f"https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm?type__1286={type_1286}"
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
                    response_data = response.json()
                except json.JSONDecodeError as json_err:
                    logger.error(f"Failed to decode JSON response: {json_err}")
                    response_data = None

                if response_data:
                    logger.debug(f"[{self.account_name}] Response: {response_data}")
                    if self.key_value in response_data.get("msg", "").lower():
                        logger.info(
                            f"[{self.account_name}] Successfully completed the request."
                        )
                        self.stop_flag.set()
                        break
                    else:
                        logger.warning(
                            f"[{self.account_name}] Unexpected response: {response_data}"
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
        try:
            response = requests.get(
                NETWORK_TIME_URL,
                impersonate="chrome100",
            )
            res = response.json()
            now_time = int(res["data"]["t"]) / 1000.0
            return datetime.fromtimestamp(now_time).time()
        except requests.errors.RequestsError as e:
            logger.error(f"Request failed: {e}")
            return datetime.now().time()

    @staticmethod
    def get_proxy_ips() -> List[Dict[str, str]]:
        try:
            response = requests.get(
                PROXY_URL,
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
                self.proxy_list = Seckkiller.get_proxy_ips()
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
                "round": self.config.get("round", ""),  # 获取round的值
                "secretword": self.config.get("secretword", ""),
            }

        seckkiller = Seckkiller(
            cookie_id,
            self.start_time,
            account_name,
            max_attempts=self.config.get("max_attempts", ""),
            thread_count=self.config.get("thread_count", ""),
            key_value=self.config.get("key_value", ""),
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
    start_time = "17:59:59.950"  # 设置开始时间
    main(start_time)
