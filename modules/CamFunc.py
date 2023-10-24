from cv2 import \
    Canny, \
	cvtColor, \
	destroyAllWindows, \
    imshow, \
	putText, \
    waitKey, \
	COLOR_BGR2GRAY, \
	FONT_ITALIC

from time import time
from CamLogger import cam_logger
from CamInit import initialize_cam

# 어노테이션
from CamClass import Cam

def run(cam: Cam, method, operation_cnt, interval_sec60, sec60_total_frame, prev):
	retval, frame = cam.cap.read()
	if not retval: # 비디오 송출값 없음
		cam_logger.info("No return value")
		cam.cap.release()
		if method == "mp":
			destroyAllWindows()
		return
	operation_cnt += 1
	cur = time()
	fps = 1 / (cur - prev)
	sec60_total_frame += fps
	prev = cur
	fps = str(fps * 1000 // 1 / 1000)
	gray = cvtColor(frame, COLOR_BGR2GRAY)
	edge = Canny(gray, 100, 200)
	frame_set = {
		0: frame,
		1: gray,
		2: edge,
	}
	putText(frame_set[cam.click_cnt % 3], fps, (30, 30), FONT_ITALIC, 1, (0, 255, 0), 2)
	# imshow(f"CAM {self.cam_index}", frame)
	imshow(f"CAM {cam.cam_index}", frame_set[cam.click_cnt % 3])
	# 60초마다 로그 작성
	if interval_sec60 + 60 < time():
		cam.log_while(method, sec60_total_frame, operation_cnt)
		interval_sec60 = time()
		sec60_total_frame = 0
		operation_cnt = 0
	return (operation_cnt, interval_sec60, sec60_total_frame, prev)

def single_thread(method):
	cam_logger.info("run")
	cam0 = initialize_cam(0)
	cam1 = initialize_cam(1)
	operation_cnt0 = 0
	operation_cnt1 = 0
	interval0_sec60 = time() # 0초일때는 로그를 쓰지 않으려고 0 대신 time()을 할당함
	interval1_sec60 = time()
	sec60_total_frame0 = 0
	sec60_total_frame1 = 0
	prev0 = 0
	prev1 = 0
	while True:
		operation_cnt0, interval0_sec60, sec60_total_frame0, prev0 = run(cam0, method, operation_cnt0, interval0_sec60, sec60_total_frame0, prev0)
		operation_cnt1, interval1_sec60, sec60_total_frame1, prev1 = run(cam1, method, operation_cnt1, interval1_sec60, sec60_total_frame1, prev1)
		key = waitKey(50)
		if key == 27:
			cam0.cap.release()
			cam1.cap.release()
			if method == "mp":
				destroyAllWindows()
			cam_logger.info("stop")
			break