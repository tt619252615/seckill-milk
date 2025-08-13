from dataclasses import dataclass
from typing import Dict, List
from datetime import time, datetime
import json
from pathlib import Path
import glob
from loguru import logger
@dataclass
class TaskSchedule:
    start_time: time  # 任务开始时间
    config_file: str  # 配置文件路径
    enabled: bool = True  # 是否启用
    description: str = ""  # 任务描述

class ScheduleManager:
    def __init__(self, schedule_file: str = "schedule.json"):
        self.schedule_file = schedule_file
        self.schedules: Dict[str, List[TaskSchedule]] = {}
        self.load_schedules()

    def load_schedules(self):
        """加载调度配置"""
        try:
            with open(self.schedule_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for hour_str, tasks in data.items():
                    self.schedules[hour_str] = [
                        TaskSchedule(
                            start_time=datetime.strptime(task["start_time"], "%H:%M:%S.%f").time(),
                            config_file=task["config_file"],
                            enabled=task.get("enabled", True),
                            description=task.get("description", "")
                        )
                        for task in tasks
                    ]
        except FileNotFoundError:
            logger.warning(f"Schedule file {self.schedule_file} not found")

    def get_current_tasks(self) -> List[TaskSchedule]:
        """获取当前小时的任务"""
        current_hour = datetime.now().strftime("%H")
        return self.schedules.get(current_hour, [])

    def get_tasks_by_hour(self, hour: str) -> List[TaskSchedule]:
        """获取指定小时的任务"""
        return self.schedules.get(hour, [])

    def add_task(self, hour: str, task: TaskSchedule):
        """添加任务"""
        if hour not in self.schedules:
            self.schedules[hour] = []
        self.schedules[hour].append(task)
        self.save_schedules()

    def save_schedules(self):
        """保存调度配置"""
        data = {
            hour: [
                {
                    "start_time": task.start_time.strftime("%H:%M:%S.%f"),
                    "config_file": task.config_file,
                    "enabled": task.enabled,
                    "description": task.description
                }
                for task in tasks
            ]
            for hour, tasks in self.schedules.items()
        }
        with open(self.schedule_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def scan_config_files(config_dir: str = "./configs") -> List[str]:
        """扫描配置文件目录"""
        return glob.glob(f"{config_dir}/*.json") 