from CamClass import Cam

def initialize_cam(thread_number: int) -> Cam:
	cam = Cam(thread_number)
	cam.set_frame()
	cam.gen_frame()
	cam.add_callback()
	return cam