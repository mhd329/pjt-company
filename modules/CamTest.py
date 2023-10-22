import cv2
from CamLogger import cam_logger
from CamFunc import single_thread
from CamInit import initialize_cam
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# 버전 확인
cam_logger.info(f"openCV version : {cv2.__version__}")

def multi_thread(method: str):
	def run(thread_number: int):
		cam_logger.info("run")
		cam = initialize_cam(thread_number)
		cam.run(method)

	with ThreadPoolExecutor(max_workers=2) as excutor:
		# ThreadPoolExecutor 일때는 __main__에서 destroyAllWindows를 해야함.
		excutor.map(run, (0, 1))
		cv2.destroyAllWindows()

# def multi_process(method: str):
# 	if __name__ == "__main__":
# 		with ProcessPoolExecutor(max_workers=2) as excutor:
# 			excutor.map(make_multiprocess, (0, 1))

# def make_multiprocess(idx):
# 	def run_multiprocess(idx):
# 		wais_logger.info("run")
# 		cam = initialize_cam(idx)
# 		cam.run("mp")
# 	run_multiprocess(idx)

def multi_process(method: str):
	# def run_multiprocess(process_number: int):
	# 	wais_logger.info("run")
	# 	cam = initialize_cam(process_number)
	# 	cam.run(method)

	with ProcessPoolExecutor(max_workers=2) as excutor:
		# ProcessPoolExecutor 일때는 __main__이 아닌 key press 감지시 destroyAllWindows를 해야함
		excutor.map(run_multiprocess, (0, 1))
		# cv2.destroyAllWindows()

def run_multiprocess(process_number: int):
	cam_logger.info("run")
	cam = initialize_cam(process_number)
	cam.run("mp")

def run(method: str) -> None:
	method_dict = {
		"st" : single_thread,
		"mt" : multi_thread,
		"mp" : multi_process,
	}
	method_dict[method](method)

if __name__ == "__main__":
	# run("st")
	# run("mt")
	run("mp")