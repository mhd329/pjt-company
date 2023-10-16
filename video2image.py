import os
import sys
import cv2
import glob

def main(*args):
    """
    1. 직접 파일을 실행할 경우 아래의 기본 경로를 변경해서 쓸 수 있다.
    2. 터미널에서 쓸 경우 실행 인자로 변환할 비디오가 있는 디렉토리와 변환된 이미지가 저장될 디렉토리를 인자로 전달할 수 있다.
    -> python video2image.py C:/data_set/videos/ C:/data_set/images/
    3. 저장될 디렉토리를 지정하지 않으면 비디오 디렉토리의 부모 디렉토리를 공유하는 위치에 새로 생성된다.
    -> python video2image.py C:/data_set/videos/
    -> os.makedirs(C:/data_set/images/)
    """
    video_path = r"C:/data_set/videos/"
    image_path = r"C:/data_set/images/"
    if len(args) > 1:
        video_path = args[1]
        assert os.path.isdir(args[1]), "파일은 경로로 지정될 수 없습니다."
        video_path = os.path.split(video_path)
        image_path = f"{video_path[0]}/images"
        if not video_path[1]:
            parent_path = os.path.dirname(video_path[0])
            image_path = f"{parent_path}/images"
    if len(args) > 2:
        image_path = args[2]

    if not os.path.exists(image_path):
        os.makedirs(image_path)

if __name__ == "__main__":
    main(sys.argv)
