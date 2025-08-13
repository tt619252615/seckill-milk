from multiuserseckill import Seckkiller
from datetime import datetime, date, timedelta
from typing import Dict
import time
import json
import multiprocessing
from loguru import logger
from config import SeckillConfig, UserConfig, SeckkillerConfig

class SeckillManager:
    def __init__(self, config: dict = None, config_file: str = None):
        if config:
            self.config = SeckillConfig.from_dict(config)
        elif config_file:
            self.config_file = config_file
            with open(self.config_file, "r", encoding="utf-8") as f:
                logger.info(f"Loading config from {self.config_file}...")
                config_dict = json.load(f)
                self.config = SeckillConfig.from_dict(config_dict)
        else:
            raise ValueError("必须提供 config 或 config_file 参数")

    def sync_time(self) -> float:
        """同步时间，返回时间差"""
        network_time = Seckkiller.get_network_time()
        local_time = datetime.now().time()
        time_diff = (
            datetime.combine(date.today(), network_time) - 
            datetime.combine(date.today(), local_time)
        ).total_seconds()
        
        logger.info(f"网络时间与本地时间差: {time_diff:.3f} 秒")
        return time_diff

    def worker(self, user: UserConfig, time_diff: float) -> None:
        logger.info(f"Starting seckill for {user.account_name}...")
        
        strategy_params = None
        if user.strategy_flag == "mixue" and self.config.mixues:
            strategy_params = self.config.mixues[0]
        elif user.strategy_flag == "BW" and self.config.bw_keywords:
            strategy_params = self.config.bw_keywords
        elif user.strategy_flag and user.strategy_params:
            strategy_params = user.strategy_params
        
        user.strategy_params = strategy_params
        seckkiller_config = SeckkillerConfig.from_user_config(user, self.config)
        seckkiller_config.time_diff = time_diff  # 添加时间差到配置中
        seckkiller = Seckkiller(config=seckkiller_config)
        seckkiller.run()

    def print_remaining_time(self, time_diff: float) -> None:
        while True:
            # 使用本地时间加上时间差来计算当前实际时间
            current_local = datetime.now().time()
            adjusted_time = (
                datetime.combine(date.today(), current_local) + 
                timedelta(seconds=time_diff)
            ).time()
            
            remaining_seconds = (
                datetime.combine(date.today(), self.config.start_time)
                - datetime.combine(date.today(), adjusted_time)
            ).total_seconds()
            
            if remaining_seconds <= 0:
                logger.info("Time is up! All processes should start seckill...")
                break
                
            logger.info(f"Remaining time: {remaining_seconds:.2f} seconds")
            time.sleep(0.5)

    def run(self) -> None:
        # 在主进程中同步时间
        time_diff = self.sync_time()

        timer_process = multiprocessing.Process(
            target=self.print_remaining_time,
            args=(time_diff,)
        )
        timer_process.start()
        
        processes = []
        for user in self.config.users:
            p = multiprocessing.Process(
                target=self.worker,
                args=(user, time_diff)
            )
            p.start()
            processes.append(p)

        for p in processes:
            p.join()
        timer_process.terminate()
        timer_process.join()

    def stop_all(self):
        """停止所有进程"""
        # 实现停止逻辑
        pass

    async def run_async(self):
        """异步运行方法"""
        self.run()


def main(config_file: str) -> None:   
    manager = SeckillManager(config_file=config_file)
    manager.run()


if __name__ == "__main__":
    # start_time = "10:59:59.950"
    config_file = "./kudicookie.json"
    main(config_file)
