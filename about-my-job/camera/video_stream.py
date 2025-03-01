import cv2
import time
import numpy
import threading
from .frame_type import FrameType
from logger import video_logger as logger, log_click, log_while


class VideoStream:
    """
    연결된 각 카메라는 이 클래스의 인스턴스로 비디오 스트림을 백그라운드에서 생성함.
    """
    operation_speed_limit = 16 # ms
    fps_dot = 2 # 소수점 자리수, 2이면 0.01까지 표현

    @classmethod
    def set_frame(cls, operation_speed_limit, fps_dot):
        """
        :param operation_speed_limit: 프레임 읽기 속도제한 -> 기본값 16 (약 60fps)
        :param fps_dot: fps 계산 소수점 자리수 -> 기본값 2
        """
        assert fps_dot >= 0
        assert operation_speed_limit >= 1
        cls.operation_speed_limit = operation_speed_limit
        cls.fps_dot = fps_dot # 소수점 자리수, 2이면 0.01까지 표현

    def __init__(self):
        logger.info(f"VideoStream initialize start")
        self.click_cnt = 0 # 마우스 클릭 횟수
        self.running = False # 초기 가동 상태
        self.thread = None # read, run 분리
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
        logger.info(f"CAM {self.cam_id} connected")
        return True

    def __disconnect(self) -> None: # 카메라 연결 해제
        self.__close_window() # 창 닫기
        self.cap.release()
        logger.info(f"CAM {self.cam_id} disconnected")

    def __set_resolution(self, width: int = 640, height: int = 480) -> None: # 해상도 설정
        self.width = width
        self.height = height
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
            comparison: numpy.ndarray = (frame == last_frame)
            if (not success) or (last_frame is not None and comparison.all()):
                time.sleep(0.01)
                continue
            operation_cnt += 1
            last_frame = frame  # 새로운 프레임 저장
            # 다른 프레임은 None으로 초기화하여 메모리 절약
            if self.click_cnt % 3 == 0: # 일반 화면
                self.frame[FrameType.NORMAL] = frame
                self.frame[FrameType.GRAY] = None
                self.frame[FrameType.EDGE] = None
            elif self.click_cnt % 3 == 1: # 흑백 화면
                self.frame[FrameType.NORMAL] = None
                self.frame[FrameType.GRAY] = frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self.frame[FrameType.EDGE] = None
            elif self.click_cnt % 3 == 2: # 윤곽선 화면
                self.frame[FrameType.NORMAL] = None
                self.frame[FrameType.GRAY] = None
                self.frame[FrameType.EDGE] = cv2.Canny(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 100, 200)
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
        while True:
            frame: cv2.typing.MatLike = self.frame[self.click_cnt % 3]
            key = cv2.waitKey(self.operation_speed_limit) & 0xFF
            if key == 27: # 연결 종료 (ESC)
                if self.thread:
                    self.running = False
                    self.thread.join() # 쓰레드 중지 대기
                    self.thread = None
                self.__disconnect()
                break
            if key == 113: # 프레임 갱신 루프 중지 (q)
                if self.thread:
                    self.running = False
                    self.thread.join() # 쓰레드 중지 대기
                    self.thread = None
                self.frame[FrameType.NORMAL] = None
                self.frame[FrameType.GRAY] = None
                self.frame[FrameType.EDGE] = None
                logger.info(f"CAM {self.cam_id} frame update loop stopped")
            if key == 115: # 프레임 갱신 루프 시작 (s)
                if not self.thread:
                    self.running = True
                    self.thread = threading.Thread(target=self.__update, daemon=True) # 프레임 생성 쓰레드
                    self.thread.start() # 쓰레드 시작
                    logger.info(f"CAM {self.cam_id} frame update loop started")
            show_fps = self.real_fps
            if frame is not None:
                display_frame = frame.copy()
            else:
                display_frame = dummy.copy()
                show_fps = 0.0
            cv2.putText(display_frame, f"{show_fps}", (30, 30), cv2.FONT_ITALIC, 1, (0, 255, 0), 2)
            cv2.imshow(f"CAM {self.cam_id}", display_frame)