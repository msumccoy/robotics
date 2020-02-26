"""
Kuwin Wyke
Midwestern State University

This program is used to create a cumulative text file containing the paths to
all positive photos for training.

To use this program, place labeled images with "info.lst" file in the root
of this program then run the script. The program will rename all labeled
images and create a master "info.lst" with all labels and rename each labeled
file in the original "info.lst" file.
"""
import os

import cv2
from config import Conf


def main():
    # Get directories with labeled images
    directory_list = [
        directory for directory in os.listdir(Conf.IMG_ROOT)
        if os.path.isdir(directory)
        and Conf.INFO_FILE in os.listdir(Conf.IMG_ROOT + directory)
        and directory != Conf.MASTER_LABEL_FOLDER
    ]

    # Create folder for all labeled images
    if not os.path.exists(Conf.IMG_ROOT + Conf.MASTER_LABEL_FOLDER):
        os.mkdir(Conf.IMG_ROOT + Conf.MASTER_LABEL_FOLDER)

    # Make sure master folder is empty
    for file in os.listdir(Conf.IMG_ROOT + Conf.MASTER_LABEL_FOLDER):
        os.remove(Conf.IMG_ROOT + Conf.MASTER_LABEL_FOLDER + "/" + file)

    # Count maximum number of labeled images
    count = 0; i = 0
    for directory in directory_list:
        count += len(os.listdir(Conf.IMG_ROOT + directory))
    count += len(directory_list)

    # Rename each file with a unique name, recreate label file and create
    # master label file
    name_gen = (str(i) + Conf.IMG_TYPE for i in range(count))

    master = Conf.IMG_ROOT + Conf.MASTER_LABEL_FOLDER + "/" + Conf.INFO_FILE
    with open(master, "w") as master_file:
        for directory in directory_list:
            main_info = Conf.IMG_ROOT + directory + "/" + Conf.INFO_FILE
            with open(main_info) as info_file:
                line = info_file.readline()
                while line != "":
                    segments = line.split(" ")
                    old_name = segments[0]
                    new_name = name_gen.__next__()
                    img = cv2.imread(
                        Conf.IMG_ROOT + directory + "/" + old_name
                    )
                    cv2.imwrite(
                        Conf.IMG_ROOT + Conf.MASTER_LABEL_FOLDER + "/"
                        + new_name,
                        img
                    )
                    print("old: {} --> new: {}".format(old_name, new_name))
                    master_file.write(new_name)
                    for segment in segments[1:]:
                        master_file.write(" " + segment)
                    line = info_file.readline()


if __name__ == '__main__':
    main()
