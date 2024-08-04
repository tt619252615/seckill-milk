import asyncio
import aiohttp
from aiohttp import ClientSession
from datetime import datetime
import threading
from typing import Dict, Optional, List
import json
import random
from loguru import logger
import hashlib
import yaml
import time
import execjs
from datetime import datetime, date

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
        self.start_time: datetime.time = start_time
        self.proxy_list: List[Dict[str, str]] = []
        self.use_encryption: bool = use_encryption
        self.encryption_params: Optional[Dict[str, str]] = encryption_params
        self.encryption_js = None
        if self.use_encryption:
            with open("./js/mixue.js", "r", encoding="utf-8") as js_file:
                self.encryption_js = execjs.compile(js_file.read())

    async def encrypt_data(self, current_time: datetime) -> None:
        if not self.use_encryption or not self.encryption_params:
            return

        marketingId = self.encryption_params.get("marketingId", "")
        round = self.encryption_params.get("round", "")
        secretword = self.encryption_params.get("secretword", "")
        timestamp = int(current_time.timestamp() * 1000)

        logger.debug(f"[{self.account_name}] Round time: {timestamp}")
        param = f"marketingId={marketingId}&round={round}&s=2&secretword={secretword}&stamp={timestamp}c274bac6493544b89d9c4f9d8d542b84"
        logger.debug(f"[{self.account_name}] Encryption param: {param}")
        m = hashlib.md5(param.encode("utf8"))
        sign = m.hexdigest()
        logger.debug(f"[{self.account_name}] Sign: {self._data.update}")
        self._data.update(
            {
                "marketingId": marketingId,
                "round": round,
                "sign": sign,
                "secretword": secretword,
                "stamp": timestamp,
            }
        )
        # parmas = (
        #     f"https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm{self._data}"
        # )
        # encrypted_str = f'https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm{"marketingId":{marketingId},"round":"20:00","secretword":"茉莉奶绿销量突破1500万杯","sign":"dc3525e1d54580fcc018fefa35a1c39b","s":2,"stamp":1722611924892}'
        encrypted_str = f'https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm{{"marketingId":"{marketingId}","round":"{round}","secretword":"{secretword}","sign":"{sign}","s":2,"stamp":{timestamp}}}'
        print(encrypted_str)
        encrypted_str = self.encryption_js.call("get_sig", encrypted_str)
        logger.debug(f"[{self.account_name}] Encrypted data: {encrypted_str}")
        return encrypted_str

    async def post_seckill_url(self, session: aiohttp.ClientSession) -> None:
        try:
            proxy = random.choice(self.proxy_list) if self.proxy_list else None
            proxies = f"http://{proxy['ip']}:{proxy['port']}" if proxy else None
            logger.debug(f"[{self.account_name}] Using proxy: {proxies}")
            current_time = datetime.now()
            if self.use_encryption:
                type_1286 = await self.encrypt_data(current_time)
                BASE_URL = f"https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm?type__1286={type_1286}"
            logger.debug(f"[{self.account_name}] Data: {self._data}")
            logger.debug(f"[{self.account_name}] BASE_URL: {BASE_URL}")
            async with session.post(
                BASE_URL,
                headers=self._headers,
                json=json.dumps(self._data, separators=(",", ":"), ensure_ascii=False),
                proxy=proxies,
            ) as response:
                response_data = await response.text()
                logger.debug(f"[{self.account_name}] Response: {response_data}")
                if "success" in response_data.get("msg", "").lower():
                    self.stop_flag.set()
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")

        self.attempts += 1
        if self.attempts >= self.max_attempts:
            self.stop_flag.set()

    async def start_seckill(self) -> None:
        await self.wait_for_start_time()
        async with aiohttp.ClientSession() as session:
            while not self.stop_flag.is_set():
                await self.post_seckill_url(session)
                await asyncio.sleep(0.1)  # 避免请求过于频繁

    @staticmethod
    async def get_network_time() -> datetime.time:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(NETWORK_TIME_URL) as response:
                    res = await response.json()
                    now_time = int(res["data"]["t"]) / 1000.0
                    return datetime.fromtimestamp(now_time).time()
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            return datetime.now().time()

    @staticmethod
    async def get_proxy_ips(max_retries=3, retry_delay=5) -> List[Dict[str, str]]:
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(PROXY_URL) as response:
                        text = await response.text()
                        try:
                            data = json.loads(text)
                            if data["success"] and data["code"] == 0:
                                return data["data"]
                            else:
                                logger.error(f"Failed to get proxy IPs: {data['msg']}")
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse response as JSON: {text}")

                if attempt < max_retries - 1:  # 不是最后一次尝试
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)

            except Exception as e:
                logger.error(f"Failed to get proxy IPs: {e}")
                if attempt < max_retries - 1:  # 不是最后一次尝试
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)

        return []  # 如果所有尝试都失败，返回空列表

    async def wait_for_start_time(self) -> None:
        while True:
            current_time = await self.get_network_time()
            if current_time >= self.start_time:
                logger.info(f"[{self.account_name}] Starting seckill...")
                break
            # 在等待期间获取代理IP
            if not self.proxy_list:
                self.proxy_list = await self.get_proxy_ips()
                if self.proxy_list:
                    logger.info(
                        f"[{self.account_name}] Got {len(self.proxy_list)} proxy IPs"
                    )
            await asyncio.sleep(0.01)  # 小的睡眠时间以避免过度消耗CPU

    async def run(self) -> None:
        logger.info(f"[{self.account_name}] Waiting for start time: {self.start_time}")
        await self.start_seckill()


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

    async def worker(self, account_name: str, cookie_id: str) -> None:
        use_encryption = self.config.get("use_encryption", False)
        encryption_params = None
        if use_encryption:
            encryption_params = {
                "marketingId": self.config.get("marketingId", ""),
                "round": self.config.get("round", ""),
                "secretword": self.config.get("secretword", ""),
            }

        seckkiller = Seckkiller(
            cookie_id,
            self.start_time,
            account_name,
            use_encryption=use_encryption,
            encryption_params=encryption_params,
        )
        await seckkiller.run()

    async def print_remaining_time(self) -> None:
        while True:
            current_time = await Seckkiller.get_network_time()
            remaining_seconds = (
                datetime.combine(date.today(), self.start_time)
                - datetime.combine(date.today(), current_time)
            ).total_seconds()
            if remaining_seconds <= 0:
                logger.info("Time is up! All processes should start seckill...")
                break
            logger.info(f"Remaining time: {remaining_seconds:.2f} seconds")
            await asyncio.sleep(0.5)

    async def run(self) -> None:
        remaining_time_task = asyncio.create_task(self.print_remaining_time())

        tasks = [
            self.worker(account_name, cookie_id)
            for account_name, cookie_id in self.account_cookie_map.items()
        ]

        await asyncio.gather(*tasks)
        remaining_time_task.cancel()


def main(start_time: str, config_file: str = "cookie.yaml") -> None:
    manager = SeckillManager(config_file, start_time)
    asyncio.run(manager.run())


if __name__ == "__main__":
    start_time = "09:53:00.000"  # 设置开始时间
    main(start_time)
