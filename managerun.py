from multiuserseckill import Seckkiller
from datetime import datetime, date
from typing import Dict, Optional, List
import time
import json
import multiprocessing
from loguru import logger


class SeckillManager:
    def __init__(self, config_file: str, start_time: str):
        self.config_file = config_file
        self.start_time = datetime.strptime(start_time, "%H:%M:%S.%f").time()
        self.config = self.load_json_config()
        self.proxies = self.config.get("proxies", "")
        self.mixues = self.config.get("mixues", [])
        # self.use_encryption = self.config.get("use_encryption", False)

    def load_json_config(self) -> Dict:
        with open(self.config_file, "r", encoding="utf-8") as f:
            logger.info(f"Loading config from {self.config_file}...")
            return json.load(f)

    def worker(
        self,
        cookie_id: str,
        cookie_name: str,
        account_name: str,
        headers: Dict,
        data: Dict,
        basurl: str,
        max_attempts: int,
        thread_count: int,
        key_value: str,
        use_encryption: bool,
        encryption_params: Optional[Dict] = None,
        proxy_flag: bool = False,
    ) -> None:
        logger.info(f"Starting seckill for {account_name}...")
        seckkiller = Seckkiller(
            cookie_id,
            cookie_name,
            headers,
            data,
            basurl,
            self.proxies,
            self.start_time,
            account_name,
            max_attempts=max_attempts,
            thread_count=thread_count,
            key_value=key_value,
            use_encryption=use_encryption,
            encryption_params=encryption_params,
            proxy_flag=proxy_flag,
        )
        seckkiller.run()

    def print_remaining_time(self) -> None:
        while True:
            current_time = Seckkiller.get_network_time()
            remaining_seconds = (
                datetime.combine(date.today(), self.start_time)
                - datetime.combine(date.today(), current_time)
            ).total_seconds()
            if remaining_seconds <= 0:
                logger.info("Time is up! All processes should start seckill...")
                break
            logger.info(f"Remaining time: {remaining_seconds:.2f} seconds")
            time.sleep(0.5)

    def run(self) -> None:
        timer_process = multiprocessing.Process(target=self.print_remaining_time)
        timer_process.start()
        processes = []
        for user in self.config.get("users", []):
            account_name = user.get("account_name")
            cookie_id = user.get("cookie_id")
            cookie_name = user.get("cookie_name")
            basurl = user.get("basurl")
            max_attempts = user.get("max_attempts", 10)
            thread_count = user.get("thread_count", 5)
            key_value = user.get("key_value", "")
            headers = user.get("headers", {})
            data = user.get("data", {})
            use_encryption = user.get("use_encryption", False)
            proxy_flag = user.get("proxy_flag", False)

            encryption_params = None
            if use_encryption and self.mixues:
                encryption_params = self.mixues[0]
            # logger.info(f"cat all user info: {user}")
            p = multiprocessing.Process(
                target=self.worker,
                args=(
                    cookie_id,
                    cookie_name,
                    account_name,
                    headers,
                    data,
                    basurl,
                    max_attempts,
                    thread_count,
                    key_value,
                    use_encryption,
                    encryption_params,
                    proxy_flag,
                ),
            )
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
        timer_process.terminate()
        timer_process.join()


def main(start_time: str, config_file: str) -> None:
    manager = SeckillManager(config_file, start_time)
    manager.run()


if __name__ == "__main__":
    start_time = "21:33:59.950"
    config_file = "cookie.json"
    main(start_time, config_file)
