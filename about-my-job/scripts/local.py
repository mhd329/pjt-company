# import os
import sys


# current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 파일의 디렉토리
# root_dir = os.path.dirname(current_dir) # 루트 디렉토리 (상위 디렉토리)
# sys.path.append(root_dir) # 루트 디렉토리를 sys.path에 추가


import cv2
from camera import VideoStream as vs
from logger import video_logger as logger
from multiprocessing import Manager, synchronize
from settings import PROCESS_WORKERS, PROCESS_EXECUTOR


def run() -> None: # 로컬 실행
    stream = vs()
    cam_id = int(input("연결할 카메라 번호를 입력하세요: "))
    success = stream.connect(cam_id)
    if success:
        stream.show()
    else:
        print("연결에 실패했습니다.")


def run_multiprocess(camera_locks: dict[int, synchronize.Lock], cam_id: int) -> None: # 로컬 실행
    lock = camera_locks[cam_id] # 해당 cam_id의 Lock 가져오기
    if not lock.acquire(False): # Non-blocking 방식
        logger.info(f"CAM {cam_id} is already in use")
        return
    try:
        stream = vs()
        success = stream.connect(cam_id)
        if success:
            stream.show() # 이 메서드는 카메라 사용이 끝날 때까지 블로킹됨
    except Exception as e:
        logger.critical(f"CAM {cam_id} unexpected error = {e}", exc_info=True)
    finally: # 모든 상황에서 락을 반드시 해제해야 함
        camera_locks[cam_id].release()
        print(f"CAM {cam_id} is now available")


if __name__ == "__main__":
    # 버전 확인
    logger.info(f"Python version : {sys.version}")
    logger.info(f"GIL state : {sys._is_gil_enabled()}")
    logger.info(f"openCV version : {cv2.__version__}")
    with Manager() as manager:
        camera_locks = manager.dict({cam_id: manager.Lock() for cam_id in range(PROCESS_WORKERS)}) # 공유 dict 공간
        futures = [PROCESS_EXECUTOR.submit(run_multiprocess, camera_locks, cam_id) for cam_id in range(PROCESS_WORKERS)]
        results = [f.result() for f in futures]