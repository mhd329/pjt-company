from CamClass import Cam

def initialize_cam(component_number: int) -> Cam:
	cam = Cam(component_number)
	cam.set_frame()
	cam.gen_frame()
	cam.add_callback()
	return cam