import requests
import json

headers = {
    "host": "h5.gumingnc.com",
    "content-length": "109",
    "t-token": "tWPHd1721229807WtnhbUCAXp3",
    "cache-control": "max-age=0",
    "authorization": "",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b11)XWEB/9185",
    "content-type": "application/json",
    "accept": "*/*",
    "cookie":"",
    "origin": "https://h5.gumingnc.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://h5.gumingnc.com/",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9"
}
cookies = {
    
}
data ={
    "channelCode": 20,
    "activityId": 14,
    "brandId": 1,
    "keyWordAnswer": "乌龙青",
    "consumptionInventoryId": 332319846
}
data = json.dumps(data)
url = "https://h5.gumingnc.com/newton-buyer/newton/buyer/ump/milk/tea/activity/fcfs"
response = requests.post(url, headers=headers, data=data,verify=False)

print(response.text)
print(response)
