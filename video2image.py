import os
import sys
import cv2
import glob

dirBase = "./data/"

def main(*args):
    try:
        os.mkdir(dirBase)
        print("Base Directory", dirBase, "Created") 
    except FileExistsError:
        print("Base Directory", dirBase, "already exists")

    output = glob.glob("../dataset/pellet_3dp/*.mp4") + glob.glob("../dataset/pellet_3dp/*.MOV")

    for path in output:
        file_path = os.path.splitext(path)[0]
        file_name = file_path.split("/")[-1]
        print(file_path)
        print(file_name)

        filename = os.path.basename(path)
        dirName = dirBase +file_name
        print(filename)

        try:
            os.mkdir(dirName)
            print("Directory", dirName, "Created") 
        except FileExistsError:
            print("Directory", dirName, "already exists")

        vidcap = cv2.VideoCapture(f"../dataset/pellet_3dp/{filename}")
        success, image = vidcap.read()
        count = 0

        while success:
            cv2.imwrite("%s/%s_%06d.jpg" % (dirName, file_name, count), image)     # save frame as JPEG file
            success, image = vidcap.read()
            # print('Read a new frame: ', success)
            count += 1
    print("Convert finished.")

if __name__ == "__main__":
    main(sys.argv)
