from settings import *
from .CamClass import Cam
from .CamLogger import cam_logger
from flask import Blueprint, Response


multi_thread_web_bp = Blueprint("CamWeb", __name__)


@multi_thread_web_bp.route(f"/cam-feed/<int:cam_id>")
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

    cam_logger.info(f"Thread number : {cam_id}")
    cam = Cam(cam_id)
    # frame_gen = cam.generate_bytes("mt")
    frame_gen = cam.run_local("mt")
    return Response(frame_gen, mimetype="multipart/x-mixed-replace; boundary=frame")
    # cam.run_local("mt")
    # return Response()


# @multi_thread_web_bp.route(f"/cam-feed/<int:cam_id>")
# def multi_thread_web(cam_id: int) -> Response:
#     PROCESS_EXECUTOR.submit(get_frame_gen, cam_id)
#     return Response()


# def get_frame_gen(cam_id: int) -> Response:
#     cam_logger.info(f"Process number : {cam_id}")
#     cam = Cam(cam_id)
#     frame_gen = cam.run_local("mp")
#     # return Response(frame_gen, mimetype="multipart/x-mixed-replace; boundary=frame")