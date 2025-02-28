import cv2
from time import time
from typing import Generator
from .CamLogger import cam_logger
from .CamFrameEnum import FrameType


class Cam:
	"""
	Cam 생성 클래스.
	카메라 연결은 클래스의 인스턴스가 할당되어 작동함.
	"""
	def __init__(self, cam_index: int, frame_count: int = 30, fps_dot: int = 3): # 기본 프레임 제한 30, 소수점 자리수 3
		self.cam_index = cam_index
		self.click_cnt = 0 # 마우스 클릭 횟수
		self.fps_dot = fps_dot # 소수점 자리수, 3이면 0.001까지 표현
		self.cap = cv2.VideoCapture(self.cam_index) # 카메라 연결
		self.cap.set(cv2.CAP_PROP_FPS, frame_count) # 프레임 제한 설정

	# 창 설정
	def __init_frame(self, w: int = 640, h: int = 480):
		cam_logger.info(f"CAM {self.cam_index} set frame")
		# set(cv2.CAP_PROP_FRAME_WIDTH, w) : 프레임 너비 설정
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
		# set(cv2.CAP_PROP_FRAME_HEIGHT, h) : 프레임 높이 설정
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
		cam_logger.info(f"CAM {self.cam_index} resolution = {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)} x {self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

		# namedWindow(winname, flags) 창 생성
		cv2.namedWindow(f"CAM {self.cam_index}", cv2.WINDOW_NORMAL)
		# resizeWindow(winname, width, height) 창 크기 조정
		cv2.resizeWindow(f"CAM {self.cam_index}", w, h)
		# moveWindow(winname, x, y) 생성된 창 위치 이동
		cv2.moveWindow(f"CAM {self.cam_index}", 0, 0)
		# setWindowProperty(winname, prop_id, prop_value[1, 0]) 1은 최상단으로 띄우기
		cv2.setWindowProperty(f"CAM {self.cam_index}", cv2.WND_PROP_TOPMOST, 1)
		cam_logger.info(f"CAM current FPS: {self.cap.get(cv2.CAP_PROP_FPS)}")
		cam_logger.info(f"CAM {self.cam_index} start!!!")

	# 창을 마우스 클릭시 발생시킬 이벤트
	def __click_mouse(self, event: int, *args):
		if event == cv2.EVENT_FLAG_LBUTTON:
			self.__log_click()
			# 클릭시 창 크기를 변경하는 로직
			# if not self.is_clicked:
			# 	self.is_clicked = True
			# 	moveWindow(f"CAM {self.cam_index}", 0, 0)
			# 	resizeWindow(f"CAM {self.cam_index}", 640, 480)
			# else:
			# 	self.is_clicked = False
			# 	moveWindow(f"CAM {self.cam_index}", 0, 0)
			# 	resizeWindow(f"CAM {self.cam_index}", 1600, 900)

			# 클릭시 카운트 증가
			self.click_cnt += 1

	# 클릭시 로그
	def __log_click(self):
		# cam_logger.info(f"CAM {self.cam_index} clicked")
		cam_logger.info(f"CAM {self.cam_index} frame_set[{self.click_cnt % 3}]") # 0, 1, 2 순서로 출력, 3으로 나눈 나머지, 0:일반, 1:그레이, 2:엣지

	# while문 일정 시간 간격 로그
	def __log_while(self, method: str, sec60_fps_sum: float, while_cnt: int) -> None:
		sec60_fps_avg = (sec60_fps_sum / while_cnt) * 1000 // 1 / 1000
		cam_logger.info(f"CAM {self.cam_index}({self.cap})")
		cam_logger.info(f"\tmethod : {method}")
		cam_logger.info(f"\tset frame rate : {self.cap.get(cv2.CAP_PROP_FPS)}")
		cam_logger.info(f"\t60sec frame sum : {sec60_fps_sum}")
		cam_logger.info(f"\t60sec total operation count : {while_cnt}")
		cam_logger.info(f"\t60sec frame avg : {sec60_fps_avg}")

	def __check_fps(self, prev: float, sec60_fps_sum: float, frame: tuple[cv2.typing.MatLike | None]) -> tuple[float, float]:
		cur = time()
		diff = cur - prev
		prev = cur

		fps = 1 / diff if diff > 0 else 0
		fps = fps * (10 ** self.fps_dot) // 1 / (10 ** self.fps_dot)
		sec60_fps_sum += fps

		cv2.putText(frame[self.click_cnt % 3], str(fps), (30, 30), cv2.FONT_ITALIC, 1, (0, 255, 0), 2)

		return prev, sec60_fps_sum

	# 프레임 생성기
	def __generate_frame(self, method: str) -> Generator[cv2.typing.MatLike, None, None]:
		normal_frame = None
		gray_frame = None
		edge_frame = None
		while_cnt = 0
		interval_sec60 = time() # 0초일때는 로그를 쓰지 않으려고 0 대신 time()을 할당함
		sec60_fps_sum = 0
		prev = time()
		while True:
			cv2.waitKey(50)
			while_cnt += 1
			reading_success, normal_frame = self.cap.read()
			if not reading_success: # 비디오 송출값 없음
				cam_logger.info("No return value")
				break
			if self.click_cnt % 3 == FrameType.GRAY.value:
				gray_frame = cv2.cvtColor(normal_frame, cv2.COLOR_BGR2GRAY)
				# 다른 프레임은 None으로 초기화하여 메모리 절약
				normal_frame = None
				edge_frame = None
			if self.click_cnt % 3 == FrameType.EDGE.value:
				edge_frame = cv2.Canny(cv2.cvtColor(normal_frame, cv2.COLOR_BGR2GRAY), 100, 200)
				# 다른 프레임은 None으로 초기화하여 메모리 절약
				normal_frame = None
				gray_frame = None

			frame = (normal_frame, gray_frame, edge_frame)

			# FPS 체크
			prev, sec60_fps_sum = self.__check_fps(prev, sec60_fps_sum, frame)

			# 60초에 한번씩 로깅
			if interval_sec60 + 60 < time():
				self.__log_while(method, sec60_fps_sum, while_cnt)
				interval_sec60 = time()
				sec60_fps_sum = 0
				while_cnt = 0
			yield frame[self.click_cnt % 3]

	# 로컬 실행
	def run_local(self, method: str) -> None:
		# 로컬캠 초기화
		self.__init_frame()
		cv2.setMouseCallback(f"CAM {self.cam_index}", self.__click_mouse)
		# 프레임 생성기
		frame_gen = self.__generate_frame(method)
		while True:
			try:
				frame: cv2.typing.MatLike = next(frame_gen)
				cv2.imshow(f"CAM {self.cam_index}", frame)
				if cv2.waitKey(50) & 0xFF == 27:
					self.cap.release()
					cam_logger.info("Local cam disconnected")
					cv2.destroyWindow(f"CAM {self.cam_index}")
					break
			except StopIteration:
				cam_logger.info("Generator shutdown")
				cv2.destroyWindow(f"CAM {self.cam_index}")
				break

	# 바이트 생성기
	def generate_bytes(self, method: str) -> Generator[bytes, None, int]:
		# 프레임 생성기
		frame_gen = self.__generate_frame(method)
		while True:
			try:
				frame: cv2.typing.MatLike = next(frame_gen)
				encoding_success, buffer = cv2.imencode('.jpg', frame)
				if not encoding_success:
					continue
				frame_bytes = buffer.tobytes()
				cv2.waitKey(50)
				yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
			except StopIteration:
				cam_logger.info("Generator shutdown")
				break
		img = cv2.imread("static/images/no-return-value.png")
		_, img_encoded = cv2.imencode(".jpg", img)
		img_bytes = img_encoded.tobytes()
		yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + img_bytes + b"\r\n"

	# 로컬 + 웹 실행
	def run_local_web(self, method: str) -> Generator[bytes, None, int]:
		# 로컬캠 초기화
		self.__init_frame()
		cv2.setMouseCallback(f"CAM {self.cam_index}", self.__click_mouse)
		# 프레임 생성기
		frame_gen_local = self.__generate_frame(method)
		frame_gen_web = self.__generate_frame(method)
		while True:
			try:
				frame_local: cv2.typing.MatLike = next(frame_gen_local)
				cv2.imshow(f"CAM {self.cam_index}", frame_local)

				frame_web: cv2.typing.MatLike = next(frame_gen_web)
				encoding_success, buffer = cv2.imencode('.jpg', frame_web)
				if not encoding_success:
					continue

				if cv2.waitKey(50) & 0xFF == 27:
					self.cap.release()
					cam_logger.info("Cam disconnected")
					cv2.destroyWindow(f"CAM {self.cam_index}")
					break

				frame_bytes = buffer.tobytes()
				yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
			except StopIteration:
				cam_logger.info("Generator shutdown")
				cv2.destroyWindow(f"CAM {self.cam_index}")
				break
		img = cv2.imread("static/images/no-return-value.png")
		_, img_encoded = cv2.imencode(".jpg", img)
		img_bytes = img_encoded.tobytes()
		yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + img_bytes + b"\r\n"