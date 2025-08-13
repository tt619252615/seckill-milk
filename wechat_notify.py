from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
from datetime import datetime, timedelta
import requests
import json
import os
from typing import Dict, Any, Optional
from loguru import logger

class WechatNotifier:
    def __init__(self, app_id: str, app_secret: str, template_id: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.template_id = template_id
        self.client = WeChatClient(app_id, app_secret)
        self.wm = WeChatMessage(self.client)

    def get_words(self) -> str:
        """获取一言"""
        try:
            words = requests.get("https://tenapi.cn/v2/yiyan?format=json").json()
            if words['code'] != 200:
                return self.get_words()
            return words['data']['hitokoto']
        except Exception as e:
            logger.error(f"获取一言失败: {str(e)}")
            return "今天也要加油哦！"

    def get_time(self) -> str:
        """获取格式化的时间"""
        now = datetime.utcnow() + timedelta(hours=8)
        week_map = {
            'Monday': '星期一', 
            'Tuesday': '星期二', 
            'Wednesday': '星期三', 
            'Thursday': '星期四',
            'Friday': '星期五', 
            'Saturday': '星期六', 
            'Sunday': '星期天'
        }
        return now.strftime("%Y年%m月%d日") + week_map[now.strftime('%A')]

    def send_seckill_result(
        self, 
        user_id: str, 
        task_info: Dict[str, Any], 
        result: Dict[str, Any]
    ) -> bool:
        """发送秒杀结果通知"""
        try:
            data = {
                'time': {'value': f"🕒 {self.get_time()}"},
                'task_name': {'value': f"📌 {task_info.get('description', '未知任务')}"},
                'start_time': {'value': f"⏰ {task_info.get('start_time', '')}"},
                'status': {'value': '✅ 成功' if result.get('success') else '❌ 失败'},
                'message': {'value': f"📝 {result.get('message', '未知原因')}"},
                'details': {'value': f"📋 {result.get('details', '')}"}
            }
            
            res = self.wm.send_template(user_id, self.template_id, data)
            logger.info(f"消息推送成功: {res}")
            return True
        except Exception as e:
            logger.error(f"消息推送失败: {str(e)}")
            return False

class NotificationManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.notifier = None
            self.users = {}
            self.load_config()
            self.initialized = True

    def load_config(self):
        """加载配置"""
        try:
            with open("notify_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                
            self.notifier = WechatNotifier(
                app_id=config.get("app_id"),
                app_secret=config.get("app_secret"),
                template_id=config.get("template_id")
            )
            self.users = config.get("users", {})
            
        except Exception as e:
            logger.error(f"加载通知配置失败: {str(e)}")

    def notify_task_result(
        self, 
        task_info: Dict[str, Any], 
        result: Dict[str, Any]
    ) -> None:
        """通知任务结果"""
        if not self.notifier:
            logger.warning("通知服务未初始化")
            return

        for user_id in self.users.values():
            self.notifier.send_seckill_result(user_id, task_info, result) 