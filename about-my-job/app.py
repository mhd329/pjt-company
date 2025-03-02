import cv2
import numpy as np


from typing import Generator
from multiprocessing import shared_memory
from flask import Flask, render_template, Response


from settings import *
from logger import video_logger as logger


app = Flask(__name__)


def generator(cam_id: int) -> Generator[bytes, None, None]:
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
            yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
    except FileNotFoundError as f:
        logger.error(f"CAM {cam_id} is not connected")
        if stream is not None:
            stream.unlink()
            stream.close()
        _, img_encoded = cv2.imencode(".jpg", dummy)
        img_bytes = img_encoded.tobytes()
        yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + img_bytes + b"\r\n"
    except Exception as e:
        logger.error(f"CAM {cam_id} unexpected error = {e}", exc_info=True)
        if stream is not None:
            stream.unlink()
            stream.close()
        _, img_encoded = cv2.imencode(".jpg", dummy)
        img_bytes = img_encoded.tobytes()
        yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + img_bytes + b"\r\n"


@app.route("/")
def index():
    return render_template("index.html", cam_number=PROCESS_WORKERS)


@app.route(f"/video-feed/<int:cam_id>")
def web_player(cam_id: int) -> Response:
    return Response(generator(cam_id), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(port=8080, debug=DEBUG) # 내부 run 코드를 보니 threaded 옵션이 기본으로 되어 있음.