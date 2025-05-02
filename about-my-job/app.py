# 이미지 처리 관련 모듈
import cv2
import numpy as np


# 웹 서버 처리 관련 모듈
import asyncio
import uvicorn
# from waitress import serve
# from typing import Generator
from typing import AsyncGenerator
from multiprocessing import shared_memory
# from flask import Flask, render_template, Response
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse


# 환경설정
from settings import *
from logger import video_logger as logger


# app = Flask(__name__)
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    secret_key=SECRET_KEY,
    debug=DEBUG,
)
templates = Jinja2Templates(directory="templates")


# def generator(cam_id: int) -> Generator[bytes, None, None]:
async def generator(cam_id: int) -> AsyncGenerator[bytes, None, None]:
    stream = None
    dummy = cv2.imread("static/images/no-return-value.png")
    try:
        stream = shared_memory.SharedMemory(name=f"shm_{cam_id}") # 공유메로리 영역 오픈
        while True:
            frame = np.ndarray((480, 640, 3), dtype=np.uint8, buffer=stream.buf)
            if frame[:, :, 1:].sum() == 0: # R채널 제외한 부분이 0이면 그레이스케일을 강제로 넣은것
                frame = frame[:, :, 0]
            encoding_success, buffer = cv2.imencode('.jpg', frame)
            if not encoding_success:
                continue
            frame_bytes = buffer.tobytes()
            # yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            yield frame_bytes
            await asyncio.sleep(0.1)
    except FileNotFoundError as f:
        logger.error(f"CAM {cam_id} is not connected")
        if stream is not None:
            stream.unlink()
            stream.close()
        _, img_encoded = cv2.imencode(".jpg", dummy)
        img_bytes = img_encoded.tobytes()
        # yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + img_bytes + b"\r\n"
        yield img_bytes
        await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"CAM {cam_id} unexpected error = {e}", exc_info=True)
        if stream is not None:
            stream.unlink()
            stream.close()
        _, img_encoded = cv2.imencode(".jpg", dummy)
        img_bytes = img_encoded.tobytes()
        # yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + img_bytes + b"\r\n"
        yield img_bytes
        await asyncio.sleep(0.1)


# @app.route("/")
# def index():
#     return render_template("index.html", cam_number=PROCESS_WORKERS)
@app.get("/")
async def index():
    return templates.TemplateResponse("index.html", {"request": {}, "cam_number": PROCESS_WORKERS})


# @app.route(f"/video-feed/<int:cam_id>")
# def web_player(cam_id: int) -> Response:
#     return Response(generator(cam_id), mimetype="multipart/x-mixed-replace; boundary=frame")
@app.get(f"/video-feed/{{ cam_id }}")
async def web_player(cam_id: int) -> StreamingResponse:
    return StreamingResponse(content=generator(cam_id), media_type="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    # serve(app, host="127.0.0.1", port=8080, threads=16) # Waitress는 기본적으로 threaded=True
    # app.run(port=8080, debug=DEBUG) # 내부 run 코드를 보니 threaded 옵션이 기본으로 되어 있음.
    uvicorn.run(app, host="127.0.1", port=8080, workers=16, reload=DEBUG) # uvicorn은 기본적으로 fork 방식으로 동작함