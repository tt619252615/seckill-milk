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
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJHT09ETUUuQ09NIiwiYXVkIjpbImFwcGxldCJdLCJpYXQiOjE3MjEyMjk2NTAsImp0aSI6IjM3NGQ4OTkwLTYxYjUtNDZhNS05MDJiLWUyMjZmYzVhYzE3ZiIsImVjcF9waG9uZSI6Im4vMXZoSVlzbS9KUGIrVlZDN0xlRXc9PSIsImNyZWF0ZV90aW1lc3RhbXAiOjE2MjM1NjU3MjMwMDAsImxvZ2luVHlwZSI6IjQxIiwib3Blbl9pZCI6Im9NekF3NVNid2hUNW1tdFM1VXZ6U2FoR3B4N1UiLCJuaWNrbmFtZSI6IuesqOesqOeGiiIsInVzZXJJZCI6IjE0MDM5NjI1MTc5NzUyNDA3MDYiLCJ2ZXJzaW9uIjoiMS4wIiwiZXhwIjoxNzIyMTk4MDUwfQ.aEpJCNi2xiOJtyhsN_hr8U31KYNusXZHSJ4ufcam7IXcwpEGEDzGNcRMwZfYBWTOCu3jpzc_9jxMJFxfaAp5UR_js9hyifriE80hIY6BoHHbRyTbgmfcYHIw5hoEfX8DTH5eKM-U7M6LvXr8cvgcMttOtVPbeUnqEdHCEnCrd2PMtd9tpaZfXA5iAqfDTZHPBf-EuKeK1L0aAV3RPLsDJmH91D8Og1AlIyIIQIAAa_XP8LmOgwiy9OPYj5xzeZcKKh4eWiOMYMdlOix9V80zVmJtZUpeibY0B2ozM-Gi2FTIcwEKFSHr3X1GxiK8rmvDuavKHX0-y6iNZc0kLeZ_6w",
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
   
