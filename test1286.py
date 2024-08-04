# This is a test file for js
from curl_cffi import requests
import json
import time
import hashlib
import execjs

# base parame
BASE_URL = "https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm"
HEADERS = {
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
DATA = {
    "marketingId": "1816854086004391938",
    "round": "18:00",
    "secretword": "茉莉奶绿销量突破2000万杯",
    "sign": "5244eda0a36addb577f5bf26296e76a4",
    "s": 2,
    "stamp": 1722766562301,
}
marketingId = "1816854086004391938"
round = "18:00"
secretword = "1"


def get_sign():
    with open("./js/mixue.js", "r", encoding="utf-8") as f:
        js_code = f.read()
    timestamp = int(time.time() * 1000)
    param = f"marketingId={marketingId}&round={round}&s=2&secretword={secretword}&stamp={timestamp}c274bac6493544b89d9c4f9d8d542b84"
    m = hashlib.md5(param.encode("utf8"))
    sign = m.hexdigest()
    DATA["sign"] = sign
    DATA["stamp"] = timestamp
    print(DATA)
    ctx = execjs.compile(js_code)
    sign = ctx.call("get_sign", DATA)
    return sign


def send_request():
    sign = get_sign()
    url = f"{BASE_URL}?type__1286={sign}"
    response = requests.post(
        url,
        headers=HEADERS,
        data=json.dumps(DATA, DATAseparators=(",", ":"), ensure_ascii=False),
    )
    print(response.text)
    print(response)
