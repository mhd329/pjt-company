import cv2


from time import time
from CamLogger import cam_logger


class Cam:
	"""
	Cam 생성 클래스.
	카메라 연결은 클래스의 인스턴스가 할당되어 작동함.
	"""
	def __init__(self, cam_index: int):
		self.cam_index = cam_index
		# self.is_clicked = 0 # 마우스 클릭 이벤트 플래그
		self.click_cnt = 0 # 마우스 클릭 횟수
		self.cap = cv2.VideoCapture(self.cam_index)
		# 캠 초기화
		cam_logger.info(f"CAM {self.cam_index} start!!!")
		self.__init_frame()
		cv2.setMouseCallback(f"CAM {self.cam_index}", self.__click_mouse)
		print(f"Current Camera FPS: {self.cap.get(cv2.CAP_PROP_FPS)}")


	# 창 설정
	def __init_frame(self, w: int = 640, h: int = 480):
		cam_logger.info(f"CAM {self.cam_index} set frame")
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
		cam_logger.info(f"CAM {self.cam_index} resolution = {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)} x {self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
		# # 프레임 제한
		# self.cam.set(CAP_PROP_FPS, 15)
		cv2.namedWindow(f"CAM {self.cam_index}", cv2.WINDOW_NORMAL)
		cv2.moveWindow(f"CAM {self.cam_index}", 0, 0)
		# setWindowProperty(winname, prop_id, prop_value[1, 0]) 1은 최상단으로 띄우기
		cv2.setWindowProperty(f"CAM {self.cam_index}", cv2.WND_PROP_TOPMOST, 1)
		cv2.resizeWindow(f"CAM {self.cam_index}", w, h)

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
		cam_logger.info(f"CAM {self.cam_index} mouse clicked total {self.click_cnt}, mod 3 = {self.click_cnt % 3}, frame_set[{self.click_cnt % 3}]")

	# while문 일정 시간 간격 로그
	def __log_while(self, method: str, sec60_total_frame: float, operation_cnt: int):
		sec60_avg_frame = (sec60_total_frame / operation_cnt) * 1000 // 1 / 1000
		cam_logger.info(f"CAM {self.cam_index}({self.cap}) : {method}")
		cam_logger.info(f"set frame rate : {self.cap.get(cv2.CAP_PROP_FPS)}")
		cam_logger.info(f"60sec frame sum : {sec60_total_frame}")
		cam_logger.info(f"60sec total operation count : {operation_cnt}")
		cam_logger.info(f"60sec frame avg : {sec60_avg_frame}")

	# 프레임 생성기
	def __frame_generator(self, method: str):
		operation_cnt = 0
		interval_sec60 = time() # 0초일때는 로그를 쓰지 않으려고 0 대신 time()을 할당함
		sec60_total_frame = 0
		prev = time()
		while True:
			reading_success, frame = self.cap.read()
			if not reading_success: # 비디오 송출값 없음
				cam_logger.info("No return value")
				self.cap.release()
				if method == "mp": # 멀티프로세스 방식인 경우 모든 창을 닫아줌
					cv2.destroyAllWindows()
				break
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			edge = cv2.Canny(gray, 100, 200)
			frame_set = {
				0: frame,
				1: gray,
				2: edge,
			}
			operation_cnt += 1

			cur = time()
			fps = 1 / (cur - prev)
			sec60_total_frame += fps
			prev = cur
			fps = str(fps * 1000 // 1 / 1000) # 소수점 세자리까지 출력
			cv2.putText(frame_set[self.click_cnt % 3], fps, (30, 30), cv2.FONT_ITALIC, 1, (0, 255, 0), 2)

			# 60초에 한번씩 로깅
			if interval_sec60 + 60 < time():
				self.__log_while(method, sec60_total_frame, operation_cnt)
				interval_sec60 = time()
				sec60_total_frame = 0
				operation_cnt = 0
			
			yield frame_set[self.click_cnt % 3]

	# 바이트 스트림 생성기
	def stream_bytes(self, method: str):
		frame_gen = self.__frame_generator(method)
		while True:
			frame: cv2.typing.MatLike = next(frame_gen)
			encoding_success, buffer = cv2.imencode('.jpg', frame)
			if not encoding_success:
				continue
			frame_bytes = buffer.tobytes()
			yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

	# 테스트
	def test(self, method: str) -> None:
		frame_gen = self.__frame_generator(method)
		while True:
			frame: cv2.typing.MatLike = next(frame_gen)
			cv2.imshow(f"CAM {self.cam_index}", frame)
			key = cv2.waitKey(50)
			if key == 27:
				self.cap.release()
				if method == "mp":
					cv2.destroyAllWindows()
				cam_logger.info("stop")
				break