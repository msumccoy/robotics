"""
Kuwin Wyke
Midwestern State University

This program is used to label images for OpenCV's C++ application to train
haar cascades. If the images are larger than config.Conf.MAX_IMG_WIDTH they
will be resized. The program also has the power to used the labeled images to
crop out the object to be used with OpenCV's application to create images.

*** HOW TO USE ***
To use this program place the images you want to label in the folder
designated by config.Conf.ORIG_IMG_FOLDER. Once completed the labeled images
will be in the folder designated by config.Conf.LABELED_IMG_FOLDER.

OUTDATED!!!!!!!!!!
"""
import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import messagebox
from functools import partial
try:
    from pynput import keyboard
    from win32gui import GetWindowText, GetForegroundWindow
    accept_keys = True
except ModuleNotFoundError:
    print(
        "Could not import neccesary module to accept keyboard inputs.\n"
        "Please ensure pynput and pywin32 are installed if you need this "
        "functionality."
    )
    accept_keys = False
    messagebox.showinfo(
        "Key board input will not work. see error message for more info"
    )

from config import Conf, CV_Window, TK_Window
from enums import IMG_LOC_TYPE, COORDS

############################################
import psutil
############################################


##############################################################################
##############################################################################
# Classes ####################################################################
##############################################################################
##############################################################################
class ImageHandler:
    """
    This class controls the behaviour of the image labeling system.
    """
    _inst = None

    def __init__(self):
        # Ensure the correct environment exist
        if not os.path.exists(Conf.CROPPED_IMG_FOLDER):
            os.mkdir(Conf.CROPPED_IMG_FOLDER)

        if not os.path.exists(Conf.DELETED_IMG_FOLDER):
            os.mkdir(Conf.DELETED_IMG_FOLDER)

        if not os.path.exists(Conf.INVALID_IMG_FOLDER):
            os.mkdir(Conf.INVALID_IMG_FOLDER)

        if not os.path.exists(Conf.ORIG_AFTER_LABEL):
            os.mkdir(Conf.ORIG_AFTER_LABEL)

        if not os.path.exists(Conf.SKIP_FOLDER):
            os.mkdir(Conf.SKIP_FOLDER)

        if not os.path.exists(Conf.LABELED_IMG_FOLDER):
            os.mkdir(Conf.LABELED_IMG_FOLDER)

        if not os.path.exists(Conf.ORIG_IMG_FOLDER):
            os.mkdir(Conf.ORIG_IMG_FOLDER)
            # If this folder does not exist there is nothing we can do
            print(
                "The folder with the original images was not found. "
                f"Folder name: {Conf.ORIG_IMG_FOLDER}"
            )

        self.labeled_image = False
        self.file_change = False
        self.first_point = True
        self.mask_section = False
        self.end = False

        # Dummy initialize variables
        self.img = None
        self.img_copy = None
        self.img_name = None
        self.x = None
        self.y = None

        self.unlabeled_images = [
            img for img in os.listdir(Conf.ORIG_IMG_FOLDER)
        ]
        self.num_unlabeled = len(self.unlabeled_images)
        self.num_remaining = self.num_unlabeled
        self.last_labeled = None
        self.current_img = None
        # Number of items in the image
        self.item_count = 0
        # All the coordinates for the bounding box (bb)
        self.bb_coords = []
        # Each image name and the bb coordinates
        self.num_labeled_objects = 0
        self.cv_label_dict_temp = {}
        self.cv_label_dict = {}
        if os.path.exists(f"{Conf.LABEL_FILE}"):
            with open(f"{Conf.LABEL_FILE}") as file:
                line = file.readline()
                while line:
                    segments = line.split(" ")
                    name = segments[0]
                    if os.path.exists(f"{Conf.LABELED_IMG_FOLDER}/{name}"):
                        num_labels = int(segments[1])
                        self.num_labeled_objects += num_labels
                        segments = segments[2:]
                        coords = []
                        for i in range(num_labels):
                            xy1 = (int(segments[0]), int(segments[1]))
                            xy2 = (
                                int(segments[0]) + int(segments[2]),
                                int(segments[1]) + int(segments[3])
                            )
                            coords.append((xy1, xy2))
                            segments = segments[4:]
                        self.cv_label_dict[name] = [
                            num_labels,
                            coords
                        ]
                    else:
                        self.file_change = True
                        print(
                            f"Labeled image not in folder: {name}\n"
                            "REMOVING from label file"
                        )
                    line = file.readline()
            images_in_folder = os.listdir(f"{Conf.LABELED_IMG_FOLDER}")
            for image in images_in_folder:
                if image not in self.cv_label_dict and image != "info.lst":
                    print(f"image not in label file: {image}")
        self.num_labeled_images = len(self.cv_label_dict)
        self.labeled_index = 0

        # Create OpenCV windows and set call back functions ##################
        cv2.namedWindow(CV_Window.MAIN_WINDOW)
        cv2.setMouseCallback(CV_Window.MAIN_WINDOW, mouse_events)

    def get_next(self):
        if self.num_remaining > 0:
            self.get_unlabeled()
        elif self.num_labeled_images > 0:
            self.get_labeled()
        else:
            cv2.destroyAllWindows()
            print("No Images to Label")
            messagebox.showinfo(
                "Alert",
                f"No Images to Label\nPlace images to label in "
                f"'{Conf.ORIG_IMG_FOLDER}' folder"
            )
            main_app.after(0, bt_close.invoke)

    def get_last_labeled(self):
        if len(self.cv_label_dict) < 1:
            messagebox.showinfo(
                "Alert",
                "There are no labeled images to show"
            )
            return
        if self.labeled_image:
            self.labeled_index -= 2
            if self.labeled_index < -1:
                self.labeled_index = self.num_labeled_images - 2
            elif self.labeled_index < 0:
                self.labeled_index = self.num_labeled_images - 1
        else:
            if self.last_labeled and self.last_labeled in self.cv_label_dict:
                i = 0
                for key in self.cv_label_dict:
                    if self.last_labeled == key:
                        break
                    i += 1
                self.labeled_index = i + 1
            else:
                self.labeled_index = self.num_labeled_images - 1
            self.unlabeled_images.insert(0, self.current_img)
            self.num_remaining += 1
        if not self.labeled_index < self.num_labeled_images:
            self.labeled_index = self.num_labeled_images - 1
        self.get_labeled()

    def get_labeled(self, image_name=None):
        if image_name is None:
            i = 0
            for key in self.cv_label_dict:
                if i == self.labeled_index:
                    self.img_name = key
                    self.labeled_index += 1
                    if not self.labeled_index < self.num_labeled_images:
                        self.labeled_index = 0
                    break
                i += 1
        elif image_name in self.cv_label_dict:
            self.img_name = image_name
            i = 0
            for key in self.cv_label_dict:
                if image_name == key:
                    break
                i += 1
            self.labeled_index = i + 1
        else:  # Not expected to be hit but put here just in case
            self.img = np.zeros(CV_Window.INFO_WINDOW_SIZE, np.uint8)
            cv2.putText(
                self.img,
                "No Image obtained",
                CV_Window.NAME_ORG,
                CV_Window.FONT,
                CV_Window.FONT_SCALE,
                CV_Window.COLOR2,
                CV_Window.THICKNESS
            )
            self.img_name = None
            return
        self.labeled_image = True
        self.img = cv2.imread(f"{Conf.LABELED_IMG_FOLDER}/{self.img_name}")
        self.img_copy = self.img.copy()
        cv2.putText(
            self.img_copy,
            self.img_name,
            CV_Window.NAME_ORG,
            CV_Window.FONT,
            CV_Window.FONT_SCALE,
            CV_Window.COLOR2,
            CV_Window.THICKNESS
        )
        self.item_count = self.cv_label_dict[self.img_name][0]
        self.bb_coords = self.cv_label_dict[self.img_name][1].copy()
        self.refresh_img()
        cv2.imshow(CV_Window.MAIN_WINDOW, self.img_copy)
        update_label_list()

    def get_unlabeled(self):
        self.labeled_image = False
        if self.num_remaining > 0:
            self.item_count = 0
            self.img_name = "0000"
            while self.img_name[-3:] != "jpg" and self.img_name[-3:] != "JPG":
                self.img_name = self.unlabeled_images[0]
                if self.img_name[-3:] == "jpg" or self.img_name[-3:] == "JPG":
                    self.last_labeled = self.current_img
                    self.current_img = self.unlabeled_images.pop(0)
                else:
                    invalid_file = self.unlabeled_images.pop(0)
                    try:
                        os.rename(
                            f"{Conf.ORIG_IMG_FOLDER}/{invalid_file}",
                            f"{Conf.INVALID_IMG_FOLDER}/{invalid_file}"
                        )
                        print(
                            f"'{invalid_file}' has an invalid file type\n"
                            f"Moved to '{Conf.INVALID_IMG_FOLDER}'"
                        )
                    except FileExistsError:
                        print(
                            f"Failed to move '{invalid_file}' to "
                            f"'{Conf.INVALID_IMG_FOLDER}' because file "
                            f"already exist\nDeleting PERMANENTLY"
                        )
                        os.remove(f"{Conf.ORIG_IMG_FOLDER}/{invalid_file}")
                self.num_remaining -= 1
            self.img = cv2.imread(
                f"{Conf.ORIG_IMG_FOLDER}/{self.img_name}"
            )
            height, width, _ = self.img.shape
            if width > Conf.MAX_IMG_WIDTH:
                quotient = width / Conf.MAX_IMG_WIDTH
                width = Conf.MAX_IMG_WIDTH
                height = height / quotient
                height = int(height)
                self.img = cv2.resize(self.img, (width, height))
            self.img_copy = self.img.copy()
            cv2.putText(
                self.img_copy,
                self.img_name,
                CV_Window.NAME_ORG,
                CV_Window.FONT,
                CV_Window.FONT_SCALE,
                CV_Window.COLOR2,
                CV_Window.THICKNESS
            )
            self.refresh_img()
            update_label_list()
            if self.img_name in self.cv_label_dict:
                messagebox.showinfo(
                    "alert",
                    f"'{self.img_name}' already labeled"
                )
        else:
            self.img_name = None
            self.img = None
            self.img_copy = None

    def save_labels(self):
        if (
                self.labeled_image and
                self.cv_label_dict[self.img_name][1] == self.bb_coords
        ):
            self.skip()
        elif self.bb_coords:
            print(f"Saving: {self.img_name}")
            if self.labeled_image:
                self.file_change = True
                self.num_labeled_objects -= self.cv_label_dict[self.img_name]
            else:
                try:
                    os.rename(
                        f"{Conf.ORIG_IMG_FOLDER}/{self.img_name}",
                        f"{Conf.ORIG_AFTER_LABEL}/{self.img_name}"
                    )
                    print(
                        f"Moving '{self.img_name}' to "
                        f"'{Conf.ORIG_AFTER_LABEL}' folder"
                    )
                except FileExistsError:
                    print(
                        f"Could not move '{self.img_name}' to "
                        f"'{Conf.ORIG_AFTER_LABEL}' because file already "
                        f"exists in the folder\nDeleting PERMANENTLY"
                    )
                    os.remove(f"{Conf.ORIG_IMG_FOLDER}/{self.img_name}")
            cv2.imwrite(
                f"{Conf.LABELED_IMG_FOLDER}/{self.img_name}",
                self.img
            )
            self.num_labeled_objects += self.item_count
            self.cv_label_dict[self.img_name] = (
                self.item_count,
                self.bb_coords
            )
            self.cv_label_dict_temp[self.img_name] = (
                self.item_count,
                self.bb_coords
            )
            if len(self.cv_label_dict_temp) >= Conf.MAX_UNSAVED:
                self.save_label_file()
            self.bb_coords = []
            self.num_labeled_images = len(self.cv_label_dict)
            self.get_next()
        else:
            print(
                "Cannot save because you have no bounding boxes defined\n"
                f"{TK_Window.SKIP}"
            )

    def skip(self):
        print("skipping")
        if not self.labeled_image:
            try:
                os.rename(
                    f"{Conf.ORIG_IMG_FOLDER}/{self.img_name}",
                    f"{Conf.SKIP_FOLDER}/{self.img_name}"
                )
                print(
                    f"Moving '{self.img_name}' to skip folder:"
                    f" {Conf.SKIP_FOLDER}"
                )
            except FileExistsError:
                print(
                    f"Could not move '{self.img_name}' because file already"
                    f" exist in skip folder: {Conf.SKIP_FOLDER}\n"
                    "Deleting PERMANENTLY"
                )
                os.remove(f"{Conf.ORIG_IMG_FOLDER}/{self.img_name}")
        self.bb_coords = []
        self.get_next()

    def restart(self):
        print("restarting labeling process")
        self.item_count = 0
        self.bb_coords = []
        self.first_point = True
        self.refresh_img()

    def delete_img(self):
        if self.labeled_image:
            folder = Conf.LABELED_IMG_FOLDER
            del self.cv_label_dict[self.img_name]
            self.num_labeled_images = len(self.cv_label_dict)
            self.file_change = True
        else:
            folder = Conf.ORIG_IMG_FOLDER
        try:
            os.rename(
                f"{folder}/{self.img_name}",
                f"{Conf.DELETED_IMG_FOLDER}/{self.img_name}"
            )
            print(
                f"Moving '{self.img_name}' to deletion folder from "
                f"'{folder}' folder"
            )
        except FileExistsError:
            print(
                f"Could not move '{self.img_name}' because file already "
                f"exist in folder:'{Conf.DELETED_IMG_FOLDER}'\n "
                "Deleting PERMANENTLY"
            )
            os.remove(f"{folder}/{self.img_name}")
        self.bb_coords = []
        self.get_next()

    def mask_section_toggle(self):
        if self.mask_section:
            self.mask_section = False
        else:
            self.mask_section = True
        display_mask_status()

    def refresh_img(self):
        self.img_copy = self.img.copy()
        cv2.putText(
            self.img_copy,
            self.img_name,
            CV_Window.NAME_ORG,
            CV_Window.FONT,
            CV_Window.FONT_SCALE,
            CV_Window.COLOR2,
            CV_Window.THICKNESS
        )
        for coords in self.bb_coords:
            cv2.rectangle(
                self.img_copy, coords[0], coords[1], CV_Window.COLOR
            )
        cv2.imshow(CV_Window.MAIN_WINDOW, self.img_copy)

    def validate_coords(self, x, y):
        # Edge detection algorithm to ensure boxes do not overlap.
        count = 0
        for coords in self.bb_coords:
            if (
                    coords[COORDS.POINT2.value][COORDS.X.value] < self.x
                    or
                    coords[COORDS.POINT1.value][COORDS.X.value] > x
                    or
                    coords[COORDS.POINT2.value][COORDS.Y.value] < self.y
                    or
                    coords[COORDS.POINT1.value][COORDS.Y.value] > y
            ):
                count += 1
        validated = True
        if not count == len(self.bb_coords):
            validated = messagebox.askyesno(
                "Alert",
                "did you mean to make your bounding boxes intersect?"
            )
        return validated

    def update_box(self, x, y):
        self.refresh_img()
        if self.mask_section:
            color = CV_Window.COLOR4
        else:
            color = CV_Window.COLOR
        cv2.rectangle(
            self.img_copy,
            (self.x, self.y),
            (x, y),
            color
        )
        cv2.imshow(CV_Window.MAIN_WINDOW, self.img_copy)

    def draw_cross(self, x, y):
        self.refresh_img()
        if self.mask_section:
            color = CV_Window.COLOR4
        else:
            color = CV_Window.COLOR
        height, width, _ = self.img_copy.shape
        cv2.line(self.img_copy, (x, 0), (x, height), color)
        cv2.line(self.img_copy, (0, y), (width, y), color)
        cv2.imshow(CV_Window.MAIN_WINDOW, self.img_copy)

    def set_top_left(self, x, y):
        # The upper left corner of the bounding box
        self.x = x
        self.y = y
        self.first_point = False
        cv2.circle(self.img_copy, (x, y), 1, CV_Window.COLOR)

    def set_bottom_right(self, x, y):
        # Switch the points if they were placed in wrong order
        if self.x > x:
            temp_x = self.x
            self.x = x
            x = temp_x
        if self.y > y:
            temp_y = self.y
            self.y = y
            y = temp_y

        if self.validate_coords(x, y):
            if self.mask_section:
                self.mask_section = False
                display_mask_status()
                if self.labeled_image:
                    response = messagebox.askyesno(
                        "Alert",
                        "You will have to relabel the image. Continue?"
                    )
                    if not response:
                        self.first_point = True
                        return
                cv2.rectangle(
                    self.img,
                    (self.x, self.y),
                    (x, y),
                    CV_Window.COLOR4,
                    -1
                )
                self.bb_coords = []
            else:
                self.bb_coords.append(((self.x, self.y), (x, y)))
                # Draw the bounding box
                cv2.rectangle(
                    self.img_copy,
                    (self.x, self.y),
                    (x, y),
                    CV_Window.COLOR,
                )
                self.item_count += 1
        else:
            print("Invalid coordinates, please re-enter them")
            self.refresh_img()
        self.first_point = True
        self.refresh_img()

    def save_label_file(self):
        # Save labeling data
        if self.cv_label_dict_temp != {} and not self.file_change:
            print("Appending to file")
            with open(Conf.LABEL_FILE, "a") as file:
                for key in self.cv_label_dict_temp:
                    line = f"{key} {self.cv_label_dict[key][0]} "
                    for coords in self.cv_label_dict_temp[key][1]:
                        width = (
                            coords[COORDS.POINT2.value][COORDS.X.value]
                            - coords[COORDS.POINT1.value][COORDS.X.value]
                        )
                        height = (
                            coords[COORDS.POINT2.value][COORDS.Y.value]
                            - coords[COORDS.POINT1.value][COORDS.Y.value]
                        )
                        line += (
                            f"{coords[COORDS.POINT1.value][COORDS.X.value]} "
                            f"{coords[COORDS.POINT1.value][COORDS.Y.value]} "
                            f"{width} {height} "
                        )
                    line += "\n"
                    file.write(line)
            self.cv_label_dict_temp = {}
        elif self.file_change:
            self.file_change = False
            print(f"Writing to file")
            with open(Conf.LABEL_FILE, "w") as file:
                for key in self.cv_label_dict:
                    line = f"{key} {self.cv_label_dict[key][0]} "
                    for coords in self.cv_label_dict[key][1]:
                        width = (
                                coords[COORDS.POINT2.value][COORDS.X.value]
                                - coords[COORDS.POINT1.value][COORDS.X.value]
                        )
                        height = (
                                coords[COORDS.POINT2.value][COORDS.Y.value]
                                - coords[COORDS.POINT1.value][COORDS.Y.value]
                        )
                        line += (
                            f"{coords[COORDS.POINT1.value][COORDS.X.value]} "
                            f"{coords[COORDS.POINT1.value][COORDS.Y.value]} "
                            f"{width} {height} "
                        )
                    line += "\n"
                    file.write(line)


##############################################################################
##############################################################################
# Functions ##################################################################
##############################################################################
##############################################################################
def mouse_events(event, x, y, flags, param):
    # This function is used to initiate the drawing of the bounding box or
    # cross hairs
    if event == cv2.EVENT_LBUTTONDOWN:
        if img_handler.first_point:
            img_handler.set_top_left(x, y)
        else:
            img_handler.set_bottom_right(x, y)
    elif event == cv2.EVENT_MOUSEMOVE:
        if img_handler.first_point:
            img_handler.draw_cross(x, y)
        else:
            img_handler.update_box(x, y)


def cut_out_objects():
    labels = {}
    if not os.path.exists(Conf.IMG_PATH_CROP):
        os.mkdir(Conf.IMG_PATH_CROP)
    with open(Conf.LABEL_FILE) as file:
        line = file.readline()
        while line != "":
            temp = line.split(" ")
            if temp[-1] == "\n":
                temp.pop()
            # Basic validation to ensure the number of coordinates is
            # correct
            if int(temp[1]) * 4 == len(temp) - 2:
                name = temp[0]
                num_labels = int(temp[1])
                temp.pop(0)
                temp.pop(0)
                labels[name] = [num_labels]
                for _ in range(num_labels):
                    # Save top left coordinates
                    # and the width and height
                    try:
                        labels[name].append(
                            [
                                (int(temp[0]), int(temp[1])),
                                (int(temp[2]), int(temp[3]))
                            ]
                        )
                        # Remove values that were just recorded
                        temp.pop(0)
                        temp.pop(0)
                        temp.pop(0)
                        temp.pop(0)
                    except ValueError:
                        print("{} not a valid name".format(name))
            else:
                print("Malformed string --> {}".format(line))
            line = file.readline()

    index = 0
    for key in labels:
        print(key, labels[key])
        img = cv2.imread(Conf.IMG_PATH + "/" + key, cv2.IMREAD_GRAYSCALE)
        num_labels = labels[key][0]
        for i in range(num_labels):
            x, y = labels[key][i + 1][0]
            width, height = labels[key][i + 1][1]
            crop_img = img[y:y + height, x:x + width]
            crop_img = cv2.resize(
                crop_img, (Conf.CROP_SIZE, Conf.CROP_SIZE)
            )
            cv2.rectangle(
                img, (x, y), (x + width, y + height), CV_Window.COLOR
            )
            name = Conf.IMG_PATH_CROP + "/_crop" + str(index) + ".jpg"
            cv2.imwrite(name, crop_img)
            index += 1


def update_label_list():
    i = 0
    for image in img_handler.cv_label_dict:
        # To prevent a new UI element being created each iteration check if
        # instance already exist then delete it
        if image in bt_cv_images:
            bt_cv_images[image].destroy()
        if image == img_handler.img_name:
            color = "blue"
        else:
            color = "black"
        bt_cv_images[image] = tk.Button(
            cv_inner,
            text=f"{image} -- #labeles: {img_handler.cv_label_dict[image][0]}",
            fg=color,
            command=partial(img_handler.get_labeled, image)
        )
        bt_cv_images[image].grid(row=i, column=0, sticky="we")
        i += 1
    cv_inner.update_idletasks()
    cv_canvas.config(scrollregion=cv_canvas.bbox("all"))

    #############################################
    cv_text_area.delete("1.0", tk.END)
    cv_text_area.insert(tk.END, f"Memory used: {process.memory_info().rss}\n")
    cv_text_area.insert(
        tk.END,
        f"Number of labeled pictures: {img_handler.num_labeled_images}\n"
    )
    cv_text_area.insert(
        tk.END,
        f"Number of objects: {img_handler.num_labeled_objects}\n"
    )
    cv_text_area.insert(
        tk.END,
        f"Number of unlabled pics remaining: {img_handler.num_remaining}\n"
    )
    #############################################

    if "tf label" in misc:
        misc["tf label"].destroy()
    misc["tf label"] = tk.Button(tf_inner, text="Currently not set up")
    # label.grid(row=0, column=0)
    misc["tf label"].grid()

    # Dipslay badge in top right corner saying if the image is labeled or not
    if img_handler.labeled_image:
        label = "Labeled"
        color = "red"
    else:
        label = "Unlabeled"
        color = "black"
    # To prevent a new UI element being created each iteration check if
    # instance already exist then delete it
    if "image type" in misc:
        misc["image type"].destroy()
    misc["image type"] = tk.Label(main_app, text=label, fg=color)
    misc["image type"].grid(row=0, column=1)


def display_mask_status():
    if img_handler.mask_section:
        label = "Mask On"
        color = "red"
    else:
        label = "Mask off"
        color = "black"
    if "mask" in misc:
        misc["mask"].destroy()
    misc["mask"] = tk.Label(main_app, text=label, fg=color)
    misc["mask"].grid(row=1, column=1)


def activate_opencv_labeling():
    print("activate_opencv_labeling")


def activate_tf_labeling():
    print("activate_tf_labeling")


def key_press(key):
    if GetWindowText(GetForegroundWindow()) == Conf.WINDOW_NAME:
        try:
            if key == keyboard.Key.space or key == keyboard.Key.enter:
                bt_save_current.invoke()
            elif key == keyboard.Key.esc:
                bt_close.invoke()
            elif key == keyboard.Key.backspace or key.char == 'b':
                bt_back.invoke()
            elif key.char == 's':
                bt_save_all.invoke()
            elif key.char == 'r':
                bt_restart.invoke()
            elif key.char == 'x':
                bt_skip.invoke()
            elif key.char == 'd':
                bt_delete.invoke()
            elif key.char == 'm':
                bt_mask.invoke()
        except AttributeError:
            pass


##############################################################################
##############################################################################
# Main Function ##############################################################
##############################################################################
##############################################################################
process = psutil.Process(os.getpid())
img_handler = ImageHandler()
bt_cv_images = {}
bt_tf_images = {}
misc = {}

row = 0
main_app = tk.Tk()
main_app.title(Conf.WINDOW_NAME)
main_app.geometry(f"{TK_Window.HEIGHT1}x{TK_Window.WIDTH1}")

# Create control/instruction buttons #########################################
heading = tk.Label(main_app, text="Press: ")
bt_save_current = tk.Button(
    main_app,
    text=TK_Window.SAVE_CURRENT,
    command=img_handler.save_labels
)
bt_save_all = tk.Button(
    main_app,
    text=TK_Window.SAVE_ALL,
    command=img_handler.save_label_file
)
bt_restart = tk.Button(
    main_app,
    text=TK_Window.RESTART,
    command=img_handler.restart
)
bt_skip = tk.Button(
    main_app,
    text=TK_Window.SKIP,
    command=img_handler.skip
)
bt_delete = tk.Button(
    main_app,
    text=TK_Window.DELETE,
    command=img_handler.delete_img
)
bt_mask = tk.Button(
    main_app,
    text=TK_Window.MASK,
    command=img_handler.mask_section_toggle
)
bt_back = tk.Button(
    main_app,
    text=TK_Window.GO_BACK,
    command=img_handler.get_last_labeled
)
bt_close = tk.Button(
    main_app,
    text="close",
    command=main_app.destroy
)  # placed on the grid closer to the bottom
spacer = tk.Label(main_app, text="")

# heading.grid(row=row, column=0, sticky="new")
# row += 1
bt_save_all.grid(row=row, column=0, sticky="new")
row += 1
bt_save_current.grid(row=row, column=0, sticky="new")
row += 1
bt_restart.grid(row=row, column=0, sticky="new")
row += 1
bt_skip.grid(row=row, column=0, sticky="new")
row += 1
bt_delete.grid(row=row, column=0, sticky="new")
row += 1
bt_mask.grid(row=row, column=0, sticky="new")
row += 1
bt_back.grid(row=row, column=0, sticky="new")
row += 1
spacer.grid(row=row, column=0, sticky="new")
row += 1

# Create main container for label display ####################################
cv_frame = tk.Frame(main_app)
cv_frame.grid(row=row, column=0)
tf_frame = tk.Frame(main_app)
tf_frame.grid(row=row, column=1)
row += 1

# Create OpenCV display area #################################################
cv_main_button = tk.Button(
    cv_frame,
    text=TK_Window.CV_BUTTON_TEXT,
    command=activate_opencv_labeling
)
cv_main_button.grid(row=0, column=0, sticky="we")
cv_canvas = tk.Canvas(
    cv_frame,
    width=TK_Window.WIDTH2,
    height=TK_Window.HEIGHT2
)
cv_canvas.grid(row=1, column=0)

cv_yscroll = tk.Scrollbar(
    cv_frame,
    orient="vertical",
    command=cv_canvas.yview
)
cv_yscroll.grid(row=1, column=1, sticky='ns')
cv_canvas.configure(yscrollcommand=cv_yscroll.set)

cv_inner = tk.Frame(cv_canvas, bg="white")
cv_canvas.create_window((0, 0), window=cv_inner, anchor='nw')

cv_inner.update_idletasks()
cv_canvas.config(scrollregion=cv_canvas.bbox("all"))

# Create TensorFlow display area #############################################
tf_main_button = tk.Button(
    tf_frame,
    text=TK_Window.TF_BUTTON_TEXT,
    command=activate_tf_labeling
)
tf_main_button.grid(row=0, column=0, sticky="we")
tf_canvas = tk.Canvas(
    tf_frame,
    width=TK_Window.WIDTH2,
    height=TK_Window.HEIGHT2
)
tf_canvas.grid(row=1, column=0)

tf_yscroll = tk.Scrollbar(
    tf_frame,
    orient="vertical",
    command=tf_canvas.yview
)
tf_yscroll.grid(row=1, column=1, sticky='ns')
tf_canvas.configure(yscrollcommand=tf_yscroll.set)

tf_inner = tk.Frame(tf_canvas, bg="white")
tf_canvas.create_window(
    (0, 0),
    window=tf_inner,
    anchor='nw'
)

tf_inner.update_idletasks()
tf_canvas.config(scrollregion=tf_canvas.bbox("all"))

# Create statistics area #####################################################
spacer1 = tk.Label(main_app, text="")

cv_text_area = tk.Text(main_app, height=7, width=45)
tf_text_area = tk.Text(main_app, height=7, width=45)

cv_text_area.insert(tk.END, "Test cv")
tf_text_area.insert(tk.END, "Test tf")

spacer1.grid(row=row, column=0, sticky="wn")
row += 1
cv_text_area.grid(row=row, column=0)
tf_text_area.grid(row=row, column=1)
row += 1


bt_close.grid(row=row, column=0)

# Set Keyboard Listener ######################################################
if accept_keys:
    key_listener = keyboard.Listener(on_press=key_press)
    key_listener.start()


# Activate auxiliary functions ###############################################
img_handler.get_next()
display_mask_status()

if __name__ == '__main__':
    main_app.mainloop()
    cv2.destroyAllWindows()
    img_handler.save_label_file()
