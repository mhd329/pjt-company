import cv2
import sys
from .CamClass import Cam
from .CamLogger import cam_logger
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


# 버전 확인
cam_logger.info(f"Python version : {sys.version}")
cam_logger.info(f"GIL state : {sys._is_gil_enabled()}")
cam_logger.info(f"openCV version : {cv2.__version__}")


def single_thread(method: str, cam_number: int) -> None:
	cam_list = [Cam(i) for i in range(0, cam_number)]
	[*map(lambda cam: cam.run_local(method), cam_list)]


def multi_thread(method: str, cam_number: int) -> None:
	def run(args: tuple[str, int, bool]) -> None:
		method, thread_number = args
		cam_logger.info(f"Thread number : {thread_number}")
		cam = Cam(thread_number)
		cam.run_local(method)
	with ThreadPoolExecutor(max_workers=cam_number) as excutor:
		[*excutor.map(run, ((method, i) for i in range(0, cam_number)))]


def multi_process(method: str, cam_number: int) -> None:
	with ProcessPoolExecutor(max_workers=cam_number) as excutor:
		[*excutor.map(run_multiprocess, ((method, i) for i in range(0, cam_number)))]


def run_multiprocess(args: tuple[str, int, bool]) -> None:
	method, process_number = args
	cam_logger.info(f"Process number : {process_number}")
	cam = Cam(process_number)
	cam.run_local(method)


def main(method: str, cam_number: int) -> None:
	run_methods = {
		"st" : single_thread,
		"mt" : multi_thread,
		"mp" : multi_process,
	}
	run_methods[method](method, int(cam_number))


if __name__ == "__main__":
	"""
	sys.argv 인자의 첫 번째는 동시성 처리 방식, 두 번째는 연결된 카메라 수
	동시성 처리 방식의 종류 : "st" (single thread), "mt" (multi thread), "mp" (multi process)
	"""
	main(*sys.argv[1:])
