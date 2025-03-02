import os
import cv2
import logging
from datetime import datetime


"""
파이썬 기본 logger 사용
참고자료 1 : https://docs.python.org/ko/3.11/howto/logging.html (공식 문서)
참고자료 2 : https://jh-bk.tistory.com/40 (일반 블로그)
"""


now = datetime.now()
now = now.strftime("%y%m%d")


# 로거 객체 생성 및 설정
log_path = r"./logs"
video_logger = logging.getLogger(__name__) # 로거가 사용되는 네임스페이스를 따름
video_logger.setLevel(logging.INFO) # 기본 INFO level 까지 로깅 (필요시 개별 파일마다 별도로 로그 레벨 설정가능)


if not os.path.exists(f"{log_path}"):
    os.makedirs(f"{log_path}")


if not os.path.exists(f"{log_path}/{now}_cam_events.log"):
    with open(f"{log_path}/{now}_cam_events.log", 'w', ) as f:
        pass


if not os.path.exists(f"{log_path}/{now}_cam_critical_events.log"):
    with open(f"{log_path}/{now}_cam_critical_events.log", 'w', ) as f:
        pass


# 일반 로깅
formatter = logging.Formatter("%(asctime)s %(levelname)s : %(processName)s[%(process)d] %(threadName)s[%(threadName)s] %(funcName)s() -> %(message)s")
file_handler = logging.FileHandler(f"{log_path}/{now}_cam_events.log")
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)


# 크리티컬 로깅
critical_formatter = logging.Formatter("!!!CRITICAL!!! %(asctime)s %(levelname)s : %(processName)s[%(process)d] %(threadName)s[%(threadName)s] %(funcName)s() -> %(message)s")
critical_file_handler = logging.FileHandler(f"{log_path}/{now}_cam_critical_events.log")
critical_file_handler.setFormatter(critical_formatter)
critical_file_handler.setLevel(logging.CRITICAL) # 크리티컬만 수집
critical_stream_handler = logging.StreamHandler()
critical_stream_handler.setFormatter(critical_formatter)
critical_stream_handler.setLevel(logging.CRITICAL) # 크리티컬만 수집


# 로거에 부착
video_logger.addHandler(file_handler)
video_logger.addHandler(stream_handler)
video_logger.addHandler(critical_file_handler)
video_logger.addHandler(critical_stream_handler)


# 클릭시 로그
def log_click(cam_id: int, click_cnt: int) -> None:
    from camera.frame_type import FrameType
    # logger.info(f"CAM {cam_id} clicked")
    video_logger.info(f"CAM {cam_id} frame type = {FrameType.get_name(click_cnt % 3)}") # 0, 1, 2 순서로 출력, 3으로 나눈 나머지, 0:일반, 1:그레이, 2:엣지


# while문 일정 시간 간격 로그
def log_while(cam_id: int, cap: cv2.VideoCapture, fps_sum: float, operation_cnt: int, fps_dot: int) -> None:
    fps_sum = fps_sum * (10 ** fps_dot) // 1 / (10 ** fps_dot)
    fps_avg = (fps_sum / operation_cnt) * (10 ** fps_dot) // 1 / (10 ** fps_dot)
    video_logger.info(f"CAM {cam_id}({cap})")
    video_logger.info(f"\tsetting frame : {cap.get(cv2.CAP_PROP_FPS)}")
    video_logger.info(f"\tframe sum : {fps_sum}")
    video_logger.info(f"\ttotal operation count : {operation_cnt}")
    video_logger.info(f"\tframe avg : {fps_avg}")