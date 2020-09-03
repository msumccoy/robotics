"""
Kuwin Wyke
Midwestern State University

This module is used to create pictures to be used for labeling
"""
import cv2
import os

from config import Conf


def main():
    if not os.path.exists(Conf.IMG_FOLDER):
        os.mkdir(Conf.IMG_FOLDER)

    try:
        # get largest number in image folder to get next image number
        pic_num = max([int(i[:-4]) for i in os.listdir(Conf.IMG_FOLDER)]) + 1
    except ValueError as e:
        # no files in folder start from 0
        pic_num = 0

    print(f"Starting on pic num {pic_num}")

    cap = cv2.VideoCapture(0)
    not_end = True
    while not_end:
        # get camera image
        _, frame = cap.read()

        cv2.imshow(Conf.WINDOW_NAME, frame)
        k = cv2.waitKey(1)
        if k == ord('s') or k == ord('S') or k == 32:
            cv2.imwrite(f"{Conf.IMG_FOLDER}/{pic_num}.jpg", frame)
            print(f"saving img {Conf.IMG_FOLDER}/{pic_num}.jpg")
            pic_num += 1
        elif k != -1 and k != 255:
            print(f"exiting with code {k}")
            not_end = False

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
