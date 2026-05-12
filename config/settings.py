import os
from dotenv import load_dotenv

# 加载根目录的 .env
load_dotenv()

# 统一读取所有环境变量
# 知乎API配置
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
RING_ID = os.getenv("RING_ID")

# API 地址（从环境读取）
BASE_URL = os.getenv("BASE_URL")
API_URL_RING_DETAIL = os.getenv("API_URL_RING_DETAIL")
API_URL_CREATE_COMMENT = os.getenv("API_URL_CREATE_COMMENT")
API_URL_COMMENT_LIST = os.getenv("API_URL_COMMENT_LIST")
# 拼接完整接口 URL
FULL_URL_RING_DETAIL = BASE_URL + API_URL_RING_DETAIL
FULL_URL_CREATE_COMMENT = BASE_URL + API_URL_CREATE_COMMENT
FULL_URL_COMMENT_LIST = BASE_URL + API_URL_COMMENT_LIST
# AI 配置
AI_BASE_URL = os.getenv("AI_BASE_URL")
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME")


from typing import Dict, List

from typing import Dict

class CircleSettings:
    def __init__(self):
        # 键：圈子名称，值：圈子ID
        self.circle_ids: Dict[str, str] = {
            "OpenClaw 人类观察员": "2001009660925334090",
            "A2A for Reconnect": "2015023739549529606",
            "黑客松脑洞补给站": "2029619126742656657"
        }

    def get_all(self) -> Dict[str, str]:
        return self.circle_ids

    def add_one(self, name: str, cid: str) -> bool:
        if name not in self.circle_ids:
            self.circle_ids[name] = cid
            return True
        return False

circle_config = CircleSettings()