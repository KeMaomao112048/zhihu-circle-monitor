import queue, threading, sys

CONSOLE_QUEUE = queue.Queue()
API_STREAM_QUEUE = queue.Queue()

# 控制台线程（保留）
def console_worker():
    while True:
        try:
            chunk = CONSOLE_QUEUE.get()
            sys.stdout.write(chunk)
            sys.stdout.flush()
        except queue.Empty:
            continue

threading.Thread(target=console_worker, daemon=True).start()

# 核心：同时写两个队列
def stream_print(chunk):    
    try:
        CONSOLE_QUEUE.put_nowait(chunk)
    except queue.Full:
        pass
    try:
        API_STREAM_QUEUE.put_nowait(chunk)
    except queue.Full:
        pass