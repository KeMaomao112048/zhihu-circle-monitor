
from config.settings import FULL_URL_RING_DETAIL,FULL_URL_CREATE_COMMENT,FULL_URL_COMMENT_LIST
from utils.auth import generate_zhihu_headers
from utils.logger import logger
import requests
import json
def get_ring_detail(cir_ids):
    # Query 参数
    querystring = {
        "ring_id": cir_ids,
        "page_num": "1",
        "page_size": "20"
    }
    headers = generate_zhihu_headers()
    logger.info("正在请求圈子detail接口")
    response = requests.request("GET", FULL_URL_RING_DETAIL, headers=headers, params=querystring)
    logger.info("成功获取圈子帖子列表")
    return json.loads(response.text)

def publish_comment(content_token, content_type, content):
    headers = generate_zhihu_headers()
    
    # 2. 请求体
    data = {
        "content_token": content_token,
        "content_type": content_type,
        "content": content
    }

    # 3. 发送请求
    response = requests.post(FULL_URL_CREATE_COMMENT, headers=headers, json=data)
    
    return response.json()


def get_all_comments(pin_id):
    all_comments = []
    page_num = 1
    page_size = 50

    while True:
        headers = generate_zhihu_headers()
        params = {
            "content_token": pin_id,
            "content_type": "pin",
            "page_num": page_num,
            "page_size": page_size
        }

        try:
            resp = requests.get(FULL_URL_COMMENT_LIST, headers=headers, params=params)
            result = resp.json()
        except requests.RequestException as e:
            logger.error(f"请求评论接口失败 pin_id:{pin_id}: exc_info=True")
            break
        except Exception as e:
            logger.error(f"获取评论未知异常 pin_id:{pin_id}", exc_info=True)
            return []

        if result.get("status") != 0:
            break

        data = result.get("data", {})
        comments = data.get("comments", [])
        has_more = data.get("has_more", False)

        if not comments:
            break

        all_comments.extend(comments)

        if not has_more:
            break

        page_num += 1

    return all_comments