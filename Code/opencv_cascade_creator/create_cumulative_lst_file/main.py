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

from config import Conf


def main():
    # Get directories with labeled images
    directory_list = [
        directory for directory in os.listdir(Conf.IMG_ROOT)
        if os.path.isdir(directory)
        and Conf.INFO_FILE in os.listdir(Conf.IMG_ROOT + directory)
    ]

    # Count total number of labeled images
    count = 0
    for directory in directory_list:
        count += len(os.listdir(Conf.IMG_ROOT + directory))

    # Rename each file with a unique name, recreate label file and create
    # master label file
    name_gen = (Conf.NAME + str(i) + Conf.IMG_TYPE for i in range(count))

    master = Conf.IMG_ROOT + Conf.INFO_FILE
    with open(master, "w") as master_file:
        for directory in directory_list:
            main_info = Conf.IMG_ROOT + directory + "/" + Conf.INFO_FILE
            temp_info = Conf.IMG_ROOT + directory + "/" + Conf.INFO_FILE_TEMP
            with open(main_info) as info_file:
                with open(temp_info, "w") as temp_file:
                    line = info_file.readline()
                    while line != "":
                        segments = line.split(" ")
                        old_name = segments[0]
                        new_name = name_gen.__next__()
                        print("old name --> {}: new name --> {}".format(
                            old_name, new_name
                        ))
                        os.rename(
                            Conf.IMG_ROOT + directory + "/" + old_name,
                            Conf.IMG_ROOT + directory + "/" + new_name
                        )
                        master_file.write(new_name)
                        temp_file.write(new_name)
                        for segment in segments[1:]:
                            master_file.write(" " + segment)
                            temp_file.write(" " + segment)
                        line = info_file.readline()
            os.remove(main_info)
            os.rename(temp_info, main_info)


if __name__ == '__main__':
    main()
