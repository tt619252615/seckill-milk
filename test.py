import requests
import json

headers = {
    "host": "h5.gumingnc.com",
    "content-length": "109",
    "t-token": "tWPHd1721229807WtnhbUCAXp3",
    "cache-control": "max-age=0",
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJHT09ETUUuQ09NIiwiYXVkIjpbImFwcGxldCJdLCJpYXQiOjE3MjEyMjk2NTAsImp0aSI6IjM3NGQ4OTkwLTYxYjUtNDZhNS05MDJiLWUyMjZmYzVhYzE3ZiIsImVjcF9waG9uZSI6Im4vMXZoSVlzbS9KUGIrVlZDN0xlRXc9PSIsImNyZWF0ZV90aW1lc3RhbXAiOjE2MjM1NjU3MjMwMDAsImxvZ2luVHlwZSI6IjQxIiwib3Blbl9pZCI6Im9NekF3NVNid2hUNW1tdFM1VXZ6U2FoR3B4N1UiLCJuaWNrbmFtZSI6IuesqOesqOeGiiIsInVzZXJJZCI6IjE0MDM5NjI1MTc5NzUyNDA3MDYiLCJ2ZXJzaW9uIjoiMS4wIiwiZXhwIjoxNzIyMTk4MDUwfQ.aEpJCNi2xiOJtyhsN_hr8U31KYNusXZHSJ4ufcam7IXcwpEGEDzGNcRMwZfYBWTOCu3jpzc_9jxMJFxfaAp5UR_js9hyifriE80hIY6BoHHbRyTbgmfcYHIw5hoEfX8DTH5eKM-U7M6LvXr8cvgcMttOtVPbeUnqEdHCEnCrd2PMtd9tpaZfXA5iAqfDTZHPBf-EuKeK1L0aAV3RPLsDJmH91D8Og1AlIyIIQIAAa_XP8LmOgwiy9OPYj5xzeZcKKh4eWiOMYMdlOix9V80zVmJtZUpeibY0B2ozM-Gi2FTIcwEKFSHr3X1GxiK8rmvDuavKHX0-y6iNZc0kLeZ_6w",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b11)XWEB/9185",
    "content-type": "application/json",
    "accept": "*/*",
    "cookie":"acw_tc=276aedf517212296674305354e163ee5ffc6a0e4dfb64a29009ee1dd13a414; ntes_utid=tid._.PhnzmH%252BPpltEQlRFQQeWQfVDMME%252FS%252FDY._.0; tfstk=fpCqCCmBdSFqApBM43OwYzftrBwv9BECo1t6SNbMlnxc1EXrbwsPld1f5hWPjgpXmoR0bf7fJnT_XZxi_GjAlCs1_ThNJNCbkCavMId9skZQO17AkCKgNvAPgLYkkaDMofb-6jjMskZQNoBHs5AGC0y-8a7k2F8mnnjgZUxJWEAMmdmoEexkjCAGjLDkRFYiiEYmEU-lssly0K43uM7zqV2pHHbDmZTcZ6iBjZAt_f-2uK7fo3lis_B8NX2pmJ3WXItA-EST9jdDQ9Q67iPqiG7dwg8lx5lBmaQCdKC09Apei3pNiirqHnXf4pLkEVPpPMtlksXzW0bcAnRDrLN38avGFspdGuc2t9QXGOjTdYdVStAP4Jo9r-ahs1VtQKYJzHazrZAecJdlGD4EBApuyU-Q8yktBKmHzHaqOAH9HnLyAzvN.",
    "origin": "https://h5.gumingnc.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://h5.gumingnc.com/",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9"
}
cookies = {
    "acw_tc": "276aedf517212296674305354e163ee5ffc6a0e4dfb64a29009ee1dd13a414",
    "ntes_utid": "tid._.PhnzmH%%252BPpltEQlRFQQeWQfVDMME%%252FS%%252FDY._.0",
    "tfstk": "fpCqCCmBdSFqApBM43OwYzftrBwv9BECo1t6SNbMlnxc1EXrbwsPld1f5hWPjgpXmoR0bf7fJnT_XZxi_GjAlCs1_ThNJNCbkCavMId9skZQO17AkCKgNvAPgLYkkaDMofb-6jjMskZQNoBHs5AGC0y-8a7k2F8mnnjgZUxJWEAMmdmoEexkjCAGjLDkRFYiiEYmEU-lssly0K43uM7zqV2pHHbDmZTcZ6iBjZAt_f-2uK7fo3lis_B8NX2pmJ3WXItA-EST9jdDQ9Q67iPqiG7dwg8lx5lBmaQCdKC09Apei3pNiirqHnXf4pLkEVPpPMtlksXzW0bcAnRDrLN38avGFspdGuc2t9QXGOjTdYdVStAP4Jo9r-ahs1VtQKYJzHazrZAecJdlGD4EBApuyU-Q8yktBKmHzHaqOAH9HnLyAzvN."
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