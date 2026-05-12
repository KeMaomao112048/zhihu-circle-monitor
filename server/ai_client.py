import requests
import json
from config.settings import AI_BASE_URL, AI_MODEL_NAME
from utils.logger import logger
from router.api import publish_comment
from utils.output_queue import stream_print
REPLIED_COMMENTS = set()


def call_local_ai_stream(messages):
    url = f"{AI_BASE_URL}/v1/chat/completions"

    payload = {
        "model": AI_MODEL_NAME,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 2048,
        "stream": True
    }

    try:
        SESSION = requests.Session()
        response = SESSION.post(url, json=payload, stream=True)
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    json_str = line[6:]
                    if json_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(json_str)
                        content = data["choices"][0]["delta"].get("content", "")
                        if content:
                            yield content
                    except:
                        continue
    except Exception as e:
        return f"AI 调用失败：{str(e)}"



def analyze_zhihu_posts_stream(zhihu_data):
    pin_idx = 1
    for post in zhihu_data:
        
        pin_id = post["pin_id"]
        prompt = ""
        if post["comment_num"]:
        #拼接有评论的帖子
            stream_print(f"正在分析帖子 {pin_id} 的评论...")
            prompt = f"【帖子序数 pin_idx={pin_idx}】\n"
            pin_idx += 1
            prompt += f"【帖子ID{pin_id}】\n"
            prompt += f"作者：{post['post_author']}\n"
            prompt += f"帖子内容：{post['post_content']}\n"
            prompt += "对应评论：\n"
            for c_idx, c in enumerate(post["comments"]):
                prompt += f"  评论{c_idx+1}｜{c['comment_id']}｜{c['comment_author']}：{c['comment_content']}\n"       

        else:
            continue

        prompt += '''
        ## 任务
        你是圆桌讨论主理人，查看上面**每一条帖子**的评论，判断评论是否向着无意义的口水仗或情绪化的的方向演化，
        或在讨论僵持时引入个人ai观点或他人看法提供灵感

        ## 输出规则（必须严格遵守）
        1. 输出 **JSON 数组**
        2. 只判断数组里**每一条对应一篇帖子**的评论是否脱离帖子，不要评价帖子和帖子之间的内容
        3. 输出格式如下：
        [
            {
                "pin_index": "第{pin_idx}条帖子",
                "pin_id": "{帖子ID}",
                "post_author": "{帖子作者}",
                "post_content": "{帖子内容}",
                "core_topic": "{你总结的主题}",
                "comment_num": "{评论数量}",
                comments: [
                    {   
                        "comment_index": "1"
                        "comment_id": "{评论ID}",
                        "comment_auther": "{评论作者}",
                        "comment_content": "原文",
                        "comment_topic": "概括评论主题",
                        "is_intervene": "true/false,对比评论主题和帖子主题，判断评论主题是否偏离帖子主题，检查是否有口水化倾向或情绪化倾向，检查讨论是否僵持不下去需要引入新观点",
                        "intervene_reason": "简述介入原因",
                        "intervene_message": "判断评论是否向着无意义的口水仗或情绪化的的方向演化，或在讨论僵持时引入个人ai观点或他人看法提供灵感"
                    },
                    {
                        "comment_index": "2",
                        ···
                    }
                ]
            }
        ]
        **只输出纯净 JSON，不要任何其他文字**
        '''
        messages = [{"role": "user", "content": prompt}]
        ai_json_buffer = ""
        for chunk in call_local_ai_stream(messages):
            ai_json_buffer += chunk
            stream_print(chunk)
        stream_print("\n")

        try:
            ai_result = json.loads(ai_json_buffer)
            for post in ai_result:
                pin_id = post.get("pin_id", "")

                for comment in post.get("comments", []):
                    comment_id = comment.get("comment_id", "")
                    is_intervene = comment.get("is_intervene", False)
                    msg = comment.get("intervene_message", "")
                    # 判断是否介入
                    if is_intervene and msg and comment_id and comment_id not in REPLIED_COMMENTS:
                        stream_print(f"发现偏离评论：{comment_id}")

                        stream_print(f"自动引导：{msg}")

                        REPLIED_COMMENTS.add(comment_id)
                        res = publish_comment(
                            content_token=comment_id,    
                            content_type="comment",
                            content=msg
                        )
                        stream_print(f"评论发送完成：{res}")
        except json.JSONDecodeError:
            logger.error("JSON 解析失败",exc_info=True)
        except Exception as e:
            logger.error("解析 LLM 结果未知异常", exc_info=True)