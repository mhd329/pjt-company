import os
import sys
import cv2
import glob

def main(*args):
    """
    터미널에서 쓸 경우 실행 인자로 타겟이 있는 디렉토리와 변환된 이미지가 저장될 디렉토리를 전달해준다.
    -> python video2image.py C:/data_set/videos/ C:/data_set/images/
    """
    target_path = "C:/data_set/videos"
    result_path = "C:/data_set/images"
    if len(args) > 1:
        # target_path = args[1]
        # result_path = args[2]
        print(f"long args : {args}")
    
    os.makedirs(result_path)

    video_list_mp4 = glob.glob(f"{target_path}/*.mp4")
    video_list_mov = glob.glob(f"{target_path}/*.MOV")
    

if __name__ == "__main__":
    main(sys.argv)
