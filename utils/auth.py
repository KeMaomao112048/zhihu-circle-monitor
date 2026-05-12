import time
import hmac
import hashlib
import base64
from config.settings import APP_KEY, APP_SECRET

# 生成签名
def generate_zhihu_headers():
    timestamp = str(int(time.time()))
    log_id = f"req_{int(time.time() * 1000)}"
    extra_info = ""
    
    sign_str = f"app_key:{APP_KEY}|ts:{timestamp}|logid:{log_id}|extra_info:{extra_info}"
    
    app_secret_bytes = APP_SECRET.encode("utf-8")
    sign_str_bytes = sign_str.encode("utf-8")
    
    hmac_obj = hmac.new(app_secret_bytes, sign_str_bytes, hashlib.sha256)
    sign = base64.b64encode(hmac_obj.digest()).decode("utf-8")

    headers = {
        "X-App-Key": APP_KEY,
        "X-Timestamp": timestamp,
        "X-Log-Id": log_id,
        "X-Sign": sign,
        "X-Extra-Info": ""
    }
    return headers

