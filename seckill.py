import requests
import json
from typing import Dict, Optional
from loguru import logger
NETWORK_TIME_URL = 'http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp' #获取网络时间
BASE_URL  = 'https://h5.gumingnc.com/newton-buyer/newton/buyer/ump/milk/tea/activity/fcfs'
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
    "accept-language": "zh-CN,zh;q=0.9"
}
BASE_DATA ={
    "channelCode": 20,
    "activityId": 14,
    "brandId": 1,
    "keyWordAnswer": "乌龙青",
    "consumptionInventoryId": 332319846
}
class Seckiller():
    """
    description: tThis class is used to get the seckill url of the product.
    """
    def __init__(self, cookie_id: str, start_time:int) -> None:
        self.cookie_id = cookie_id
        self._headers = {**DEFAULT_HEADERS, "Cookie": cookie_id}
        self._data = BASE_DATA
        self.star_time = start_time
    

    def post_seckill_url(self)-> None:
        try:
            response = requests.post(
                self._url,
                headers=self._headers,
                data=json.dumps(self._data),
            )
            logger.debug(f"Response: {response.text["msg"]}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
    def starte_seckill(self,started_time:int) -> None:
        pass



    @staticmethod
    def get_network_time() -> Optional[int]:
        try:
            response = requests.get(NETWORK_TIME_URL)
            return response.json()["data"]["t"] / 1000.0
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
    @staticmethod
    def print_remaining_time()-> None:
        network_time = Seckiller.get_network_time()
        if network_time is None:
            return
        remaining_time = network_time - Seckiller.start_time
        logger.info(f"Remaining time: {remaining_time}")
        if remaining_time < 0:
            logger.error("Time is up!")
            return
        else:
            logger.info("Time is up!")
            return
   
