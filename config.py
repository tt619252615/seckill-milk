from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime, time

@dataclass
class UserConfig:
    account_name: str
    cookie_id: str
    cookie_name: str
    basurl: str
    headers: Dict
    data: Dict
    max_attempts: int = 10
    thread_count: int = 5
    key_value: str = ""
    key_message: str = ""
    proxy_flag: bool = False
    strategy_flag: Optional[str] = None
    strategy_params: Optional[Dict] = None

@dataclass
class SeckillConfig:
    start_time: time
    proxies: str
    users: List[UserConfig]
    mixues: List[Dict] = None
    bw_keywords: str = ""

    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'SeckillConfig':
        start_time = datetime.strptime(
            config_dict.get("start_time", ""), 
            "%H:%M:%S.%f"
        ).time()
        
        users = [
            UserConfig(**user_dict)
            for user_dict in config_dict.get("users", [])
        ]
        
        return cls(
            start_time=start_time,
            proxies=config_dict.get("proxies", ""),
            users=users,
            mixues=config_dict.get("mixues", []),
            bw_keywords=config_dict.get("bw_keywords", "")
        ) 

@dataclass
class SeckkillerConfig:
    cookie_id: str
    cookie_name: str
    headers: Dict[str, str]
    data: Dict[str, int]
    base_url: str
    proxy_url: str
    start_time: time
    account_name: Optional[str] = None
    max_attempts: int = 1
    thread_count: int = 1
    key_value: Optional[Dict[str, str]] = None
    key_message: str = None
    strategy_flag: Optional[str] = None
    strategy_params: Optional[Dict[str, str]] = None
    proxy_flag: bool = False
    time_diff: float = 0.0

    @classmethod
    def from_user_config(cls, user: UserConfig, global_config: SeckillConfig) -> 'SeckkillerConfig':
        return cls(
            cookie_id=user.cookie_id,
            cookie_name=user.cookie_name,
            headers=user.headers,
            data=user.data,
            base_url=user.basurl,
            proxy_url=global_config.proxies,
            start_time=global_config.start_time,
            account_name=user.account_name,
            max_attempts=user.max_attempts,
            thread_count=user.thread_count,
            key_value=user.key_value,
            key_message=user.key_message,
            strategy_flag=user.strategy_flag,
            strategy_params=user.strategy_params,
            proxy_flag=user.proxy_flag,
            time_diff=0.0
        ) 