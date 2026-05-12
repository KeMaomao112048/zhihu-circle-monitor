import logging
import sys
import os
from logging.handlers import RotatingFileHandler

# 日志格式
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(filename)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志存放目录
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 文件日志按大小切割（防止文件过大）
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"),
    maxBytes=1024 * 1024 * 10,  # 10MB
    backupCount=5,
    encoding="utf-8",
)

file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# 控制台日志
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
console_handler.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)

# 配置根 logger
def get_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()  # 避免重复添加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

# 全局单例 logger
logger = get_logger()