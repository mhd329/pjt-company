import os
import sys
import cv2
import glob
from Video2ImageLogger import v2i_logger

def main(*args):
    """
    1. 직접 파일을 실행할 경우 아래의 기본 경로를 변경해서 쓸 수 있다.
    2. 터미널에서 쓸 경우 실행 인자로 변환할 비디오가 있는 디렉토리와 변환된 이미지가 저장될 디렉토리를 인자로 전달할 수 있다.
    -> python video2image.py C:/data_set/videos/ C:/data_set/images/
    3. 저장될 디렉토리를 지정하지 않으면 비디오 디렉토리의 부모 디렉토리를 공유하는 위치에 새로 생성된다.
    -> python video2image.py C:/data_set/videos/
    -> os.makedirs(C:/data_set/images/)
    """
    video_path = r"F:/dataset/videos/"
    image_path = r"F:/dataset/images/"
    v2i_logger.info(args[0])
    args = args[0]
    if len(args) > 1:
        v2i_logger.info(f"args[1] (video path) : {args[1]}")
        assert os.path.exists(args[1]), "지정된 경로를 찾을 수 없습니다."
        assert os.path.isdir(args[1]), "파일은 경로로 지정될 수 없습니다."
        video_path = args[1]
        parent, child = os.path.split(video_path)
        # 슬래시 없는 경우 (endswith 쓰고 싶었는데 경로가 역슬래시로 표현될 수도 있어서 유지함.)
        image_path = fr"{parent}/images/"
        video_path = fr"{parent}/{child}/"
        if not child: # 맨 마지막에 슬래시 있는 경우
            video_path = fr"{parent}/"
            parent = os.path.dirname(os.path.dirname(video_path))
            image_path = fr"{parent}/images/"
    if len(args) > 2:
        v2i_logger.info(f"args[2] (image path) : {args[2]}")
        if not os.path.exists(image_path):
            v2i_logger.info(f"{args[2]} is not found.")
            answer = input("경로 새로 만들기(y/n) : ")
            if answer == "y":
                os.makedirs(image_path)
                v2i_logger.info(f"{args[2]} is made by user.")
            assert os.path.exists(args[2]), "지정된 경로를 찾을 수 없습니다."
        assert os.path.isdir(args[2]), "파일은 경로로 지정될 수 없습니다."
        image_path = args[2]
        parent, child = os.path.split(image_path)
        image_path = fr"{parent}/{child}/"
        if not child: # 맨 마지막에 슬래시 있음
            image_path = fr"{parent}/"

    if not os.path.exists(image_path):
        os.makedirs(image_path)

    # video_list_mp4 = glob.glob(f"{target_path}/*.mp4")
    # video_list_mov = glob.glob(f"{target_path}/*.MOV")
    video_list = glob.glob(fr"{video_path}*.*")
    for video in video_list:
        total = 0
        success = 0
        skip = 0
        if os.path.isfile(video):
            _, file = os.path.split(video)
            file_name, file_ext = file.split(".")
            cap = cv2.VideoCapture(f"{video_path}{file_name}.{file_ext}")
            retval, frame = cap.read()
            if retval:
                processing_cnt = 0
                while retval:
                    cv2.imwrite("%s/%s %06d.jpg" % (image_path, file_name, processing_cnt), frame)
                    processing_cnt += 1
                    retval, frame = cap.read()
                v2i_logger.info(f"{video} Convert finished, processing count : {processing_cnt}.")
                success += 1
            else:
                skip += 1 # 리턴값 없으면(False 이면 == 재생할 수 없으면) skip
                v2i_logger.info(f"{video} is skipped, No return value.")
            cap.release() # 비디오 자원 해제
        else:
            skip += 1 # 파일이 아니면 skip
            v2i_logger.info(f"{video} is skipped, {video} is not file.")
        total += 1
    v2i_logger.info(f"({success}/{total}) Success : {success}, Skipped : {skip}, Total : {total}")
if __name__ == "__main__":
    main(sys.argv)
