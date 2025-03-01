from settings import *
from logger import logger
from scripts import run_local
from camera import VideoStream
from flask import Flask, render_template, Response


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", cam_number=MAX_WORKERS)


@app.route(f"/cam-feed/<int:cam_id>")
def multi_thread_web(cam_id: int) -> Response:

    # def get_frame_gen(cam_id: int) -> Response:
        # cam_logger.info(f"Thread number : {cam_id}")
        # cam = Cam(cam_id)
        # # frame_gen = cam.generate_bytes("mt")
        # frame_gen = cam.run_local_web("mt")
        # return Response(frame_gen, mimetype="multipart/x-mixed-replace; boundary=frame")
        # # cam.run_local("mt")
        # # return Response()

    # future: Future[Response] = THREAD_EXECUTOR.submit(get_frame_gen, cam_id)
    # result = future.result()
    # return result

    logger.info(f"Thread number : {cam_id}")
    stream = VideoStream(cam_id, logger)
    stream.start()
    # frame_gen = cam.generate_bytes("mt")
    # return Response(frame_gen, mimetype="multipart/x-mixed-replace; boundary=frame")
    run_local(stream, cam_id, logger)
    return Response()


if __name__ == "__main__":
    app.run(port=8080, debug=DEBUG) # 내부 run 코드를 보니 threaded 옵션이 기본으로 되어 있음.