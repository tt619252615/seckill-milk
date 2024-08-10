# seckill-milk 小程序秒杀
小程序秒杀
seckill milk
wx小程序自行抓包。
小程序最近的活动guming奶茶，抓包获取cookie和authorization，然后填入代码即可。
data部分也需要修改，每天的id和答案不同。
# 目前没有测试，欢迎测试提交问题。
## 这个可以是一个通用的定时重发脚本，服用非常方便，替换相关请求参数即可。
### 新增proxy代理设置，非常方便。
### 增加 mixue加密算法，可以实现mixue抢奶茶。在cookie.yaml设置是否启动。不启动也不会影响正常抢购。
<<<<<<< HEAD
### mixue正常使用，使用update_seckill.py脚本即可。

=======
### mixue使用方法：
1.必须有node的环境，自行安装。
2.cookie.yaml中设置use_encryption: true
3.抓包小程序的AccessToken，填入cookie.yaml。
4.配置代理ip，mixue建议一定要配置，我使用的是json格式的提取。代理商不同格式可能不一样。
### 测试结果：
1.完全正常，设置好代理之后效果还不错。
>>>>>>> 75625b8832b89ab1c65c93e35c6be29f89dda729
### 正常秒杀(8.10)：
现在配置cookie.json 和managerun.run中的启动时间即可。
参数说明：
- start_time: 开始时间，格式为"HH:mm:ss"，例如" 00:00:00"
- users：类型是{}.
- --cookie_id: 用户id，授权的关键字段，字符串类型
- --account_name: 备注名，字符串类型。
- --cookie: 用户的cookie，字符串类型。
- --basurl：请求地址，字符串类型。
- --max_attempts: 最大尝试次数，整数类型。
- --thread_count: 线程数，整数类型。
- --key_value：返回的关键字，可用于停止脚本。
- --headers：请求头，可用于增加请求头。
- --data：请求参数，可用于增加请求参数。
- --proxy_flag：启用代理的标志，布尔类型。
- --use_encryption：是否使用mixue加密算法，布尔类型。
- proxies：代理地址，类型是str
- mixues：mixue加密算法的配置，可用于配置mixue加密算法的相关参数。
  截至目前我测试是正常的，有问题的可以提交issue。