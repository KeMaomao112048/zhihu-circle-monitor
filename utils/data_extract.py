from router.api import get_all_comments
def extract_for_ai(data):
    contents = data["data"]["contents"]
    seen_ids = set()
    result = []

    for pin in contents:
        pin_id = pin["pin_id"]

        # 去重
        if pin_id in seen_ids:
            continue
        seen_ids.add(pin_id)

        full_comments = get_all_comments(pin_id)

        # 构造 AI 需要的结构
        item = {
            "pin_id": pin_id,
            "post_author": pin["author_name"],
            "post_content": pin.get("content", ""),
            "comment_num": len(full_comments),
            "comments": []
        }

        # 提取评论
        comments = pin.get("comments", [])
        for c in full_comments:
            item["comments"].append({
                "comment_id": c.get("comment_id",""),
                "comment_author": c["author_name"],
                "comment_content": c["content"]
            })

        result.append(item)

    return result