import cv2
import sys
from CamLogger import cam_logger
from CamClass import Cam
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


# 버전 확인
cam_logger.info(f"openCV version : {cv2.__version__}")


def single_thread(method: str, cams_number: int) -> None:
	cam_list = [Cam(i) for i in range(0, cams_number)]
	[*map(lambda cam: cam.test(method), cam_list)]


def multi_thread(method: str, cams_number: int) -> None:
	def run(args: tuple[str, int, bool]) -> None:
		method, thread_number = args
		cam_logger.info(f"thread number : {thread_number}")
		cam = Cam(thread_number)
		cam.test(method)
	with ThreadPoolExecutor(max_workers=cams_number) as excutor:
		# ThreadPoolExecutor 일때는 __main__에서 destroyAllWindows를 해야함.
		[*excutor.map(run, ((method, i) for i in range(0, cams_number)))]
	cv2.destroyAllWindows()


def multi_process(method: str, cams_number: int) -> None:
	with ProcessPoolExecutor(max_workers=cams_number) as excutor:
		# ProcessPoolExecutor 일때는 __main__이 아닌 key press 감지시 destroyAllWindows를 해야함
		[*excutor.map(run_multiprocess, ((method, i) for i in range(0, cams_number)))]


def run_multiprocess(args: tuple[str, int, bool]) -> None:
	method, process_number = args
	cam_logger.info(f"process number : {process_number}")
	cam = Cam(process_number)
	cam.test(method)


def main(method: str, cams_number: int) -> None:
	run_methods = {
		"st" : single_thread,
		"mt" : multi_thread,
		"mp" : multi_process,
	}
	run_methods[method](method, int(cams_number))


if __name__ == "__main__":
	"""
	sys.argv 인자의 첫 번째는 동시성 처리 방식, 두 번째는 연결된 카메라 수
	동시성 처리 방식의 종류 : "st" (single thread), "mt" (multi thread), "mp" (multi process)
	"""
	main(*sys.argv[1:])
