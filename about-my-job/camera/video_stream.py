import cv2
import time
import numpy as np
from .frame_type import FrameType
from multiprocessing import shared_memory
from concurrent.futures import ThreadPoolExecutor
from logger import video_logger as logger, log_click, log_while # 유일한 서버측 파일


THREAD_EXECUTOR = ThreadPoolExecutor(max_workers=2)


class VideoStream:
    """
    연결된 각 카메라는 이 클래스의 인스턴스로 비디오 스트림을 백그라운드에서 생성함.
    """
    operation_speed_limit = 16 # ms
    fps_dot = 2 # 소수점 자리수, 2이면 0.01까지 표현
    height = 480
    width = 640
    
    # 공유메모리 참조용 배열
    ref_array = np.zeros((height, width, 3), dtype=np.uint8) # 일반

    @classmethod
    def set_frame(cls, operation_speed_limit: int = 16, fps_dot: int = 2, height: int = 480, width: int = 640) -> None:
        """
        :param operation_speed_limit: 프레임 읽기 속도제한 -> 기본값 16 (약 60fps)
        :param fps_dot: fps 계산 소수점 자리수 -> 기본값 2
        :param height: 프레임 높이 -> 기본값 480
        :param width: 프레임 너비 -> 기본값 640
        """
        assert operation_speed_limit >= 1, "Wait time must be greater than 1"
        assert fps_dot >= 0, "Decimal point must be greater than 0"
        assert height >= 480, "Minimum height is 480"
        assert width >= 640, "Minimum width is 640"
        cls.operation_speed_limit = operation_speed_limit
        cls.fps_dot = fps_dot # 소수점 자리수, 2이면 0.01까지 표현
        cls.height = height
        cls.width = width

    def __init__(self) -> None:
        logger.info(f"VideoStream initialize start")
        self.click_cnt = 0 # 마우스 클릭 횟수
        self.running = False # 초기 가동 상태
        self.future = None # read, run 분리된 쓰레드의 작업 추적
        self.frame = {
            FrameType.NORMAL : None,
            FrameType.GRAY : None,
            FrameType.EDGE : None,
        }
        self.real_fps = 0.0
        logger.info(f"VideoStream initialize end")

    def connect(self, cam_id) -> bool: # 카메라 연결
        logger.info(f"CAM {cam_id} try connect")
        self.cam_id = cam_id
        self.cap = cv2.VideoCapture(self.cam_id)
        if not self.cap.isOpened():
            logger.info(f"CAM {self.cam_id} can not connect")
            return False
        self.__set_resolution() # 해상도 설정
        self.__open_window() # 창 열기
        logger.info(f"FPS = {self.cap.get(cv2.CAP_PROP_FPS)}")
        # 공유메모리 연결
        self.stream_shm = shared_memory.SharedMemory(name=f"shm_{self.cam_id}", create=True, size=self.ref_array.nbytes)
        logger.info(f"CAM {self.cam_id} connected")
        return True

    def __disconnect(self) -> None: # 카메라 연결 해제
        self.__close_window() # 창 닫기
        self.stream_shm.unlink() # 공유메모리 연결 해제
        self.stream_shm.close()
        self.cap.release()
        logger.info(f"CAM {self.cam_id} disconnected")

    def __set_resolution(self) -> None: # 해상도 설정
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        logger.info(f"resolution = {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)} x {self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

    # 마우스 클릭시 발생시킬 이벤트, 윈도우 떴을때만 가능함
    def __add_event(self, event: int, *args):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.click_cnt += 1
            log_click(self.cam_id, self.click_cnt)
            if self.click_cnt >= 3:
                self.click_cnt = 0

    # 창 열기
    def __open_window(self) -> None:
        logger.info(f"CAM {self.cam_id} window setting")
        cv2.namedWindow(f"CAM {self.cam_id}", cv2.WINDOW_NORMAL) # 창 생성
        cv2.resizeWindow(f"CAM {self.cam_id}", self.width, self.height) # 창 크기 조정
        cv2.moveWindow(f"CAM {self.cam_id}", 0, 0) # 생성된 창 위치 이동
        cv2.setWindowProperty(f"CAM {self.cam_id}", cv2.WND_PROP_TOPMOST, 1) # setWindowProperty(winname, prop_id, prop_value[1, 0]) 1은 최상단으로 띄우기
        cv2.setMouseCallback(f"CAM {self.cam_id}", self.__add_event) # 창 마우스클릭 이벤트 등록
        logger.info(f"add click event")
        logger.info(f"CAM {self.cam_id} window opened")

    # 창 닫기
    def __close_window(self) -> None:
        cv2.destroyWindow(f"CAM {self.cam_id}")
        logger.info(f"CAM {self.cam_id} window closed")

    # 프레임 갱신 (blocking I/O)
    def __update(self) -> None:
        fps_sum = 0.0
        operation_cnt = 0
        interval_sec60 = time.time() # 0초일때는 로그를 쓰지 않으려고 0 대신 time.time()을 할당함
        last_frame: cv2.typing.MatLike = None
        while self.running:
            start_time = time.time()
            success, frame = self.cap.read()
            comparison: np.ndarray = (frame == last_frame)
            if (not success) or (last_frame is not None and comparison.all()):
                time.sleep(0.01)
                continue
            operation_cnt += 1
            last_frame = frame  # 새로운 프레임 저장
            # 다른 프레임은 None으로 초기화하여 메모리 절약
            if self.click_cnt % 3 == 0: # 일반 화면
                shared_frame = frame
                self.frame[FrameType.NORMAL] = frame
                self.frame[FrameType.GRAY] = None
                self.frame[FrameType.EDGE] = None
            elif self.click_cnt % 3 == 1: # 흑백 화면
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                shared_frame = gray
                self.frame[FrameType.NORMAL] = None
                self.frame[FrameType.GRAY] = gray
                self.frame[FrameType.EDGE] = None
            elif self.click_cnt % 3 == 2: # 윤곽선 화면
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edge = cv2.Canny(gray, 100, 200)
                shared_frame = edge
                self.frame[FrameType.NORMAL] = None
                self.frame[FrameType.GRAY] = None
                self.frame[FrameType.EDGE] = edge
            # stream = np.ndarray(shared_frame.shape, dtype=shared_frame.dtype, buffer=self.stream_shm.buf)
            stream = np.ndarray((480, 640, 3), dtype=np.uint8, buffer=self.stream_shm.buf)
            if shared_frame.ndim == 2:
                stream[:, :, 0] = shared_frame # R채널에만 저장하고 나머지는 받는쪽에서 해석할거임
                stream[:, :, 1:] = 0
            else:
                stream[:] = shared_frame
            fps = 1 / (time.time() - start_time)
            fps: float = (fps * (10 ** self.fps_dot) // 1 / (10 ** self.fps_dot))
            fps_sum += fps
            self.real_fps = fps
            if interval_sec60 + 60 < time.time(): # 60초에 한번씩 로깅
                log_while(self.cam_id, self.cap, fps_sum, operation_cnt, self.fps_dot)
                interval_sec60 = time.time()
                fps_sum = 0.0
                operation_cnt = 0

    def show(self) -> None:
        show_fps = 0.0
        dummy = cv2.imread("static/images/no-return-value.png")
        stream = np.ndarray((480, 640, 3), dtype=np.uint8, buffer=self.stream_shm.buf)
        while True:
            frame: cv2.typing.MatLike = self.frame[self.click_cnt % 3]
            key = cv2.waitKey(self.operation_speed_limit) & 0xFF
            if key == 27: # 연결 종료 (ESC)
                if self.future is not None:
                    self.running = False # 루프 중단 시그널
                    self.future.result() # 쓰레드 완료처리 (블로킹)
                    self.future = None
                    self.frame[FrameType.NORMAL] = None
                    self.frame[FrameType.GRAY] = None
                    self.frame[FrameType.EDGE] = None
                    frame = None
                stream[:] = dummy
                self.__disconnect()
                break
            if key == 113: # 프레임 갱신 루프 중단 (q)
                if self.future is not None:
                    self.running = False # 루프 중단 시그널
                    self.future.result() # 쓰레드 완료처리 (블로킹)
                    self.future = None
                    self.frame[FrameType.NORMAL] = None
                    self.frame[FrameType.GRAY] = None
                    self.frame[FrameType.EDGE] = None
                    frame = None
                    stream[:] = dummy
                    logger.info(f"CAM {self.cam_id} frame update loop stopped")
            if key == 115: # 프레임 갱신 루프 시작 (s)
                if self.future is None:
                    self.running = True
                    self.future = THREAD_EXECUTOR.submit(self.__update) # 프레임 생성 쓰레드
                    logger.info(f"CAM {self.cam_id} frame update loop started")
            show_fps = self.real_fps
            if frame is None:
                display_frame = dummy.copy()
                show_fps = 0.0
            else:
                display_frame = frame.copy()
            cv2.putText(display_frame, f"{show_fps}", (30, 30), cv2.FONT_ITALIC, 1, (0, 255, 0), 2)
            cv2.imshow(f"CAM {self.cam_id}", display_frame)