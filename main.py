from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from config.settings import circle_config
from server.ai_client import analyze_zhihu_posts_stream
from utils.output_queue import  API_STREAM_QUEUE
from router.api import get_ring_detail
from utils.data_extract import extract_for_ai
import threading 
from fastapi.responses import StreamingResponse
import queue
from fastapi.middleware.cors import CORSMiddleware

def api_stream_generator():
    chunk = API_STREAM_QUEUE.get(timeout=1)
    yield f"data: {chunk}\n\n" 
app = FastAPI(title="知乎圈子监控后端服务")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],    # 允许所有方法
    allow_headers=["*"],    # 允许所有请求头
)
# 添加圈子（只传 circle_id）
class AddCircleRequest(BaseModel):
    name: str
    circle_id: str

# 执行任务（可选指定 circle_id）
class TaskRunRequest(BaseModel):
    circle_id: Optional[str] = None  # 不传=执行所有

class CommonResp(BaseModel):
    code: int
    msg: str
    data: dict | None = None

# -------------------------- 接口 --------------------------
@app.get("/api/circle/list", response_model=CommonResp)
def get_circle_list():
    return CommonResp(
        code=200,
        msg="success",
        data={"circle_list": circle_config.get_all()}
    )

@app.post("/api/circle/add", response_model=CommonResp)
def add_circle(req: AddCircleRequest):
    ok = circle_config.add_one(req.name,req.circle_id)
    if not ok:
        raise HTTPException(status_code=400, detail="圈子ID已存在")
    return CommonResp(code=200, msg="添加成功", data={})

def producer_task(circle_id):
    circle_dict = circle_config.get_all()
    all_ids = list(circle_dict.values())
    target_ids = [circle_id] if circle_id else all_ids

    for cid in target_ids:
        raw_data = get_ring_detail(cid)
        ai_data = extract_for_ai(raw_data)

        analyze_zhihu_posts_stream(ai_data)

    # 发送结束标志
    API_STREAM_QUEUE.put(None)

async def sse_consumer():
    while True:
        try:
            # 🔥 从队列取数据（自动等待）
            chunk = API_STREAM_QUEUE.get()

            # 结束信号
            if chunk is None:
                yield f"data: [结束] 所有数据输出完成\n\n"
                break

            # 推送给前端
            yield f"data: {chunk}\n\n"

        except queue.Empty:
            yield f"data: [等待] 处理中...\n\n"



@app.post("/api/task/run")
def run_task_api(request: TaskRunRequest):
    circle_id = request.circle_id
    # 启动生产者（同级线程）
    t = threading.Thread(
        target=producer_task,
        args=(circle_id,),
        daemon=True
    )
    t.start()

    # 返回流式响应
    return StreamingResponse(
        sse_consumer(),
        media_type="text/event-stream",
        headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Content-Type-Options": "nosniff"
    }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)