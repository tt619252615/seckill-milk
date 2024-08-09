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
BASE_URL = "https://promotion.waimai.meituan.com/lottery/rights/limitcouponcomponent/fetchcoupon?couponReferId=1C5C5E27A51F4F6AA8F313A6592733C1&componentId=17230121018850.8127990801029694&geoType=2&gdPageId=569460&pageId=580258&version=1&instanceId=17230121018850.8127990801029694&clientTime=1723171248661&ctype=mtiphone&utmMedium=iphone&gSource=&dpSource=&utmCampaign=AgroupBgroupG&utmSource=AppStore&yodaReady=h5&csecplatform=4&csecversion=2.4.0"
PROXY_URL = ""  # 替换为实际的代理IP获取API
DEFAULT_HEADERS: Dict[str, str] = {
    "host": "promotion.waimai.meituan.com",
    "content-type": "application/json",
    "x-titans-user": "",
    "accept": "application/json, text/plain, */*",
    "sec-fetch-site": "same-site",
    "dj-token": "BUtNUwMAAABuBktNUwMaOQIAAAABO5rMWgAAACxUk3kku9S+/FhNj6KAztMR9mlxIrC/udidqTpxbVgrQKyl7zdA3lhQZFaStCIsUnufjX8Z5PNzxhhI04A3HgbglGIQxKdAqAdptaKNuxCiQdU66E0y4isjTQIAAABOpo80ZvkRnLNsLKnP3w3IhtLtR1cYbbRq4MzUMoBNHPoHoXIhYxM4tDa0IDXQK0i1tX1TCRjImd6so8b6ngGD8MJoGg1Kdq6VYhZj9XNu",
    "accept-language": "zh-CN,zh-Hans;q=0.9",
    "sec-fetch-mode": "cors",
    "accept-encoding": "gzip, deflate, br",
    "origin": "https://market.waimai.meituan.com",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 TitansX/20.0.1.old KNB/1.0 iOS/17.4.1 meituangroup/com.meituan.imeituan/12.23.407 meituangroup/12.23.407 App/10110/12.23.407 iPhone/iPhone12 WKWebView",
    "referer": "https://market.waimai.meituan.com/",
    "content-length": "1589",
    "mtgsig": '{"a0":"3.0","a1":"6f50fb51-23ee-4173-ab33-6ee69ed0ef29","a3":24,"a4":1723171248,"a5":"QCHqdfMKAc6deciLuB9wXRnqVqfxT4kCNjF2qmofB8ql9Bak6pbftKAzds6OIoueNM3+RIXxyDvzD+FGqDjfFZSr0H3VSwmRFFuZCuWsFEgRKFvGZb9iUl8J0bNzevchMdfRADNlHi9J2SbtB1T0g+RG9pXdtFHe1TKVAgM301D8N5d0XIwrFZidgdQQ0I2k186Bq20JhOOz4zVK2jXFLjfdwmE0m77dPYZBwDsYctUeS30jJkTTh2ai+EiDas2v415+pQBRCG7Rmal2HUG2eUSuVyqcOkuVcosKGT84yTTAaIMd2pf52WCWxIEkVOHoOuCbMQm4w8hziFb8BZeYLSSCLhcs6NpNYWkDgfjG/Rwgutkt1eAaTJqtW3ortKih5/a+hC1Xrg==","a6":0,"a7":"EKCzRS4HIsWXc7NmgtOFeRIkzuuUaUn04ts8o+jTCK+t3cnUqUrlnen/7kEQUVP+Z/3ZflTqAQDOOAxGLDU9gXldWIDHWc1iyt3Augwr9BA=","a8":"664d21ec8cb8090c0c2c80f314d3bbb59217f6083b903830440c978e","a9":"dbee2d06ESa/FJm64TD25ijTK/nFXdyKb8+IGK9ttWX2K0sUoN/37ZXNsWkcXWij1hzNVkB7mqQkQ7HCymSUkYR0v9jiP6F6wlm5jiZ2rrudSIbVc0bjV8oF4faiqvTr7uMD9ql3hnHEjZNK+wx7yxYgGNNTPQLBOpvTXaFxeDWCfN8MRTYY02ZUSGOgSH8oRr76CLF2FGHdFQYZybDYYq8crqn0T3BZhTZEEazZ6NnzVEp+piJSyhmkKbg7K8kk5Ym1MKXyVv64D9y+6iQ1PApW/87Bs2rr/ivqSe1AGnWxw+OvMrwi6/WOUs6mhHQH2rDspUyHUECRhUyq8xuCckJjz+pYiRdUev9PCPdzAE8jPmcKV7y73JD9yG5uuffWy1JHWUMWoivNrJ/0rlO0MbMv4Sy9FOYfSXj3x2Le0AmGSIlZqWZb3bRWt2+VbtmOp6BaoYlsW5Me4QoujAnrFP2fiZCoBbJ4+MwWeUdXasdCQTzjXdcC5FrzMGTDY7Xs2663qdyyGjRpxMuDEOeYH/Z7U4boS90Qf44tI2/5HSdTNCunTk/Aje7nHxKLrRTb/TtqLqtPdoVZsqi95B1ncMPd6FaUB8VpZKdHVauaVXl+YGri639LTMkuft/eijO++VT8K09lCOKJ7mZmcXkjP8jnZs3cpCl8mTE94FEOgpvj59jdcf15bsPQPwBlHljR1mU7v3nk7YKzhkC+X2UD5GwJmhrYKQ==","a10":"5,65,1.1.6","x0":2,"a2":"ce4ad251636d34d09e14844cad562679"}',
    "sec-fetch-dest": "empty",
}
BASE_DATA: Dict[str, int] = {
    "cType": "mtiphone",
    "fpPlatform": 5,
    "wxOpenId": "",
    "appVersion": "12.23.407",
    "mtFingerprint": "",
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
    start_time = "10:59:59.850"  # 设置开始时间
    main(start_time)
