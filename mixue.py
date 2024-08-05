from curl_cffi import requests
import json

headers = {
    "host": "mxsa.mxbc.net",
    "content-length": "173",
    "accept": "application/json, text/plain, */*",
    "access-token": "",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b19)XWEB/9193",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://mxsa-h5.mxbc.net",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://mxsa-h5.mxbc.net/",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
}
url = "https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm?type__1286=n4UxuDRD9D2DgB7QDsD7IQ44rYaT9KPwD"
data = {
    "marketingId": "1816854086004391938",
    "round": "19:00",
    "secretword": "茉莉奶绿销量突破2000万杯",
    "sign": "38aac17e450cdc97757457f430276816",
    "s": 2,
    "stamp": 1722770317130,
}
params = {"type__1286": "eqRxRDBDnD9Qi=K4GNDQuxBKwou7NQKDuW=+oD"}
proxy = {
    "http": "http://113.123.0.98:15001",
}
data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
# data = str(data)
print(data)
print(type(data))
data1 = '{"marketingId":"1816854086004391938","round":"18:00","secretword":"茉莉奶绿销量突破2000万杯","sign":"8851e5b463ade22a2b1ff479b2299baf","s":2,"stamp":1722768804764}'
print(data1)
print(type(data))
response = requests.post(url, headers=headers, data=data, impersonate="chrome100")

print(response.text)
print(response)
