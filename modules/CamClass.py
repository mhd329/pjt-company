from cv2 import \
    Canny, \
	cvtColor, \
	destroyAllWindows, \
    imshow, \
    resizeWindow, \
    moveWindow, \
    namedWindow, \
	putText, \
    setMouseCallback, \
    setWindowProperty, \
    waitKey, \
	COLOR_BGR2GRAY, \
	CAP_PROP_FPS, \
    CAP_PROP_FRAME_HEIGHT, \
    CAP_PROP_FRAME_WIDTH, \
    EVENT_FLAG_LBUTTON, \
	FONT_ITALIC, \
    WINDOW_NORMAL, \
    WND_PROP_TOPMOST, \
    VideoCapture

from time import time
from CamLogger import cam_logger

class Cam:
	def __init__(self, cam_index: int):
		self.cam_index = cam_index
		# self.is_clicked = 0 # 마우스 클릭 이벤트 플래그
		self.click_cnt = 0 # 마우스 클릭 횟수
		self.cap = VideoCapture(self.cam_index)

	# 창 설정
	def set_frame(self, w: int = 640, h: int = 480):
		cam_logger.info(f"CAM {self.cam_index} set frame")
		cam_logger.info(f"CAM {self.cam_index} resolution = {self.cap.get(CAP_PROP_FRAME_WIDTH)} x {self.cap.get(CAP_PROP_FRAME_HEIGHT)}")
		self.cap.set(CAP_PROP_FRAME_WIDTH, w)
		self.cap.set(CAP_PROP_FRAME_HEIGHT, h)
		cam_logger.info(f"CAM {self.cam_index} changed resolution = {self.cap.get(CAP_PROP_FRAME_WIDTH)} x {self.cap.get(CAP_PROP_FRAME_HEIGHT)}")
		# # 프레임 제한
		# self.cam.set(CAP_PROP_FPS, 15)

	# 창 생성
	def gen_frame(self, w: int = 640, h: int = 480):
		cam_logger.info(f"CAM {self.cam_index} generate frame")
		namedWindow(f"CAM {self.cam_index}", WINDOW_NORMAL)
		# setWindowProperty(winname, prop_id, prop_value[1, 0]) 1은 최상단으로 띄우기
		moveWindow(f"CAM {self.cam_index}", 0, 0)
		setWindowProperty(f"CAM {self.cam_index}", WND_PROP_TOPMOST, 1)
		resizeWindow(f"CAM {self.cam_index}", w, h)

	# 창을 마우스 클릭시 발생시킬 이벤트
	def click_mouse(self, event, *args):
		if event == EVENT_FLAG_LBUTTON:
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
			self.log_click()

	# 이벤트 등록
	def add_callback(self):
		setMouseCallback(f"CAM {self.cam_index}", self.click_mouse)

	# 클릭시 로그
	def log_click(self):
		# cam_logger.info(f"CAM {self.cam_index} clicked")
		cam_logger.info(f"CAM {self.cam_index} mouse clicked total {self.click_cnt}, mod 3 = {self.click_cnt % 3}, frame_set[{self.click_cnt % 3}]")

	# while문 일정 시간 간격 로그
	def log_while(self, method: str, sec60_total_frame: float, operation_cnt: int, /):
		sec60_avg_frame = (sec60_total_frame / operation_cnt) * 1000 // 1 / 1000
		cam_logger.info(f"CAM {self.cam_index}({self.cap}) : {method}")
		cam_logger.info(f"set frame rate : {self.cap.get(CAP_PROP_FPS)}")
		cam_logger.info(f"60sec frame sum : {sec60_total_frame}")
		cam_logger.info(f"60sec total operation count : {operation_cnt}")
		cam_logger.info(f"60sec frame avg : {sec60_avg_frame}")

	# 실행 함수
	def run(self, method):
		cam_logger.info("run")
		operation_cnt = 0
		# interval_secdot5 = time()
		# interval_sec1 = time()
		interval_sec60 = time() # 0초일때는 로그를 쓰지 않으려고 0 대신 time()을 할당함
		sec60_total_frame = 0
		prev = 0
		while True:
			retval, frame = self.cap.read()
			if not retval:
				cam_logger.info("not retval")
				# 15초 이상 retval 없을때 종료하는 로직 만들어야함
				# self.cap.release()
				# if method == "mp":
				# 	destroyAllWindows()
				# return
			gray = cvtColor(frame, COLOR_BGR2GRAY)
			edge = Canny(gray, 100, 200)
			frame_set = {
				0: frame,
				1: gray,
				2: edge,
			}
			operation_cnt += 1

			# # 1초에 한번씩 프레임 갱신
			# if interval_sec1 + 1 < time():
			# 	print(operation_cnt)
			# 	operation_cnt = 0
			# 	interval_sec1 = time()

			cur = time()
			fps = 1 / (cur - prev)
			sec60_total_frame += fps
			prev = cur
			fps = str(fps * 1000 // 1 / 1000)
			putText(frame_set[self.click_cnt % 3], fps, (30, 30), FONT_ITALIC, 1, (0, 255, 0), 2)

			# 0.5초에 한번씩 프레임 갱신
			# if interval_secdot5 + 0.5 < cur:
			# 	fps = str(fps * 1000 // 1 / 1000)
			# 	putText(frame_set[self.click_cnt % 3], fps, (30, 200), FONT_ITALIC, 1, (0, 255, 0), 1)
			# 	interval_secdot5 = cur

			# 60초에 한번씩 로깅
			if interval_sec60 + 60 < time():
				self.log_while(method, sec60_total_frame, operation_cnt)
				interval_sec60 = time()
				sec60_total_frame = 0
				operation_cnt = 0
			
			# imshow(f"CAM {self.cam_index}", frame)
			imshow(f"CAM {self.cam_index}", frame_set[self.click_cnt % 3])
			key = waitKey(50)
			if key == 27:
				self.cap.release()
				if method == "mp":
					destroyAllWindows()
				cam_logger.info("stop")
				break