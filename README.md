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
### mixue使用方法：
1.必须有node的环境，自行安装。
2.cookie.yaml中设置use_encryption: true
3.抓包小程序的AccessToken，填入cookie.yaml。
4.配置代理ip，mixue建议一定要配置，我使用的是json格式的提取。代理商不同格式可能不一样。
### 测试结果：
1.完全正常，设置好代理之后效果还不错。
