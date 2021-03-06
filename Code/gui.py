import logging
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import time
import cv2
import psutil
from IPython.external.qt_for_kernel import QtGui
from PIL import Image, ImageTk
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QImage, QPixmap

import log_set_up
from config import Conf
from camera import Camera
from misc import pretty_time
from robot_control import Robot
from variables import ExitControl
from pyqt5_gui import Ui_MainWindow


class GUI:
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    logger = logging.getLogger(Conf.LOG_GUI_NAME)

    def __init__(self, robot_type):
        self.main_logger.info(f"GUI: started on version {Conf.VERSION}")
        self.logger.info(
            f"GUI started on version {Conf.VERSION}:"
        )
        self.start_time = time.time()
        self.cam = Camera.get_inst(robot_type)
        self.root = tk.Tk()
        self.process = psutil.Process(os.getpid())
        print(self.process.memory_info().rss / 1024)
        self.root.title(Conf.CV_WINDOW)  # Set window title
        self.root.geometry("734x548")  # Set window size --> width x height
        self.root.bind("<Escape>", self.escape)  # Set up escape shortcut

        font_style = tkFont.Font(family="Lucida Grande", size=20)
        self.mem_label = tk.Label(self.root, font=font_style)
        self.quit_btn = tk.Button(self.root, text="quit", command=self.close)
        self.frame = tk.Label(self.root)

        # Create tabs with controls
        self.tab_main = ttk.Notebook(self.root, width=271, height=471)
        self.tab_cam = ttk.Frame(self.tab_main)
        self.tab_robot = ttk.Frame(self.tab_main)
        self.tab_main.add(self.tab_cam, text="Camera Controls")
        self.tab_main.add(self.tab_robot, text="Robot Controls")

        # Set up controls in tabs
        self.scale_slider = tk.Scale(
            self.tab_cam, label="Scale Slider", from_=1, to=100,
            orient=tk.HORIZONTAL, length=230
        )
        self.neigh_slider = tk.Scale(
            self.tab_cam, label="Nearest Neighbour Slider", from_=1, to=100,
            orient=tk.HORIZONTAL, length=230
        )
        self.rpi_brightness_slider = tk.Scale(
            self.tab_cam, label="RPi Cam Brightness Slider", from_=1, to=100,
            orient=tk.HORIZONTAL, length=230
        )
        self.rpi_contrast_slider = tk.Scale(
            self.tab_cam, label="RPi Cam Contrast Slider", from_=1, to=100,
            orient=tk.HORIZONTAL, length=230
        )
        self.rpi_iso_slider = tk.Scale(
            self.tab_cam, label="RPi Cam ISO Slider", from_=1, to=100,
            orient=tk.HORIZONTAL, length=230
        )

        self.scale_slider.bind_all("<MouseWheel>", self.on_mouse_wheel)

        self.scale_slider.grid(row=1, column=1)
        self.neigh_slider.grid(row=2, column=1)
        self.rpi_brightness_slider.grid(row=3, column=1)
        self.rpi_contrast_slider.grid(row=4, column=1)
        self.rpi_iso_slider.grid(row=5, column=1)

        # Create frame for image
        self.frame_height = 491
        self.frame_width = 441

        # Set all elements in grid
        self.mem_label.grid(row=1, column=1, sticky="nw")
        self.frame.grid(row=1, column=1)
        self.quit_btn.grid(row=10, column=1, sticky="w")
        self.tab_main.grid(row=1, column=2, sticky="nw")

    def on_mouse_wheel(self, event):
        print("mouse wheel")
        print(event.x)
        print(event.y)

    def start(self):
        self.update_image()
        self.life_check()
        self.root.mainloop()
        if ExitControl.gen:
            ExitControl.gen = False

    def update_image(self):
        mem_use = self.process.memory_info().rss / 1024
        self.mem_label['text'] = mem_use
        self.cam.main_loop_support()
        with self.cam.lock:
            frame_tk = self.cam.frame_full
        frame_tk = cv2.resize(frame_tk, (self.frame_width, self.frame_height))
        img = cv2.cvtColor(frame_tk, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(image=Image.fromarray(img))
        self.frame.config(image=img)
        self.frame.photo_ref = img
        self.root.after(1, self.update_image)

    def life_check(self):
        if not ExitControl.gen:
            self.close()
        self.root.after(1000, self.life_check)

    def escape(self, event):
        self.close()

    def close(self):
        self.main_logger.info(
            "GUI: is closing after running for "
            f"{pretty_time(self.start_time)}"
        )
        self.logger.info(
            "GUI: is closing after running for "
            f"{pretty_time(self.start_time)}\n"
        )
        self.root.destroy()
        ExitControl.gen = False


class GUI2(Ui_MainWindow):
    """
    This class is just to test using PyQt5 before creating the actual class
    that will be used.
    """
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    logger = logging.getLogger(Conf.LOG_GUI_NAME)

    def __init__(self, robot_type):
        self.main_logger.info(f"GUI: started on version {Conf.VERSION}")
        self.logger.info(
            f"GUI: started on version {Conf.VERSION}\n"
            f"- robot: {robot_type}"
        )
        self.app = QtWidgets.QApplication(sys.argv)
        super().__init__()
        self.main_window = QtWidgets.QMainWindow()
        self.setupUi(self.main_window)
        self.cam = Camera.get_inst(robot_type)
        self.robot = Robot.get_inst(robot_type)

        # Set button actions  ################################################
        self.btn_forward.clicked.connect(
            lambda: self.button_action(Conf.CMD_FORWARD)
        )
        self.btn_back.clicked.connect(
            lambda: self.button_action(Conf.CMD_BACKWARD)
        )
        self.btn_left.clicked.connect(
            lambda: self.button_action(Conf.CMD_LEFT)
        )
        self.btn_right.clicked.connect(
            lambda: self.button_action(Conf.CMD_RIGHT)
        )
        self.btn_close.clicked.connect(self.close)
        ######################################################################
        val = (
              self.cam.settings[self.cam.profile][Conf.CS_SCALE] - 1.005
        ) / 0.1
        self.CV_Scale_slider.setValue(int(val))
        self.CV_Scale_val.setNum(val)
        self.CV_Neigh_slider.setValue(
            self.cam.settings[self.cam.profile][Conf.CS_NEIGH]
        )
        self.CV_Neigh_val.setNum(
            self.cam.settings[self.cam.profile][Conf.CS_NEIGH]
        )
        self.CV_Scale_slider.valueChanged.connect(self.set_scale)
        self.CV_Neigh_slider.valueChanged.connect(self.set_neigh)

        if self.cam.is_pi_cam:
            self.RPi_Brightness_label.setEnabled(True)
            self.RPi_Brightness_slider.setEnabled(True)
            self.RPi_Brightness_val.setEnabled(True)
            self.RPi_Contrast_label.setEnabled(True)
            self.RPi_Contrast_slider.setEnabled(True)
            self.RPi_Contrast_val.setEnabled(True)
            self.RPi_ISO_label.setEnabled(True)
            self.RPi_ISO_slider.setEnabled(True)
            self.RPi_ISO_val.setEnabled(True)
        self.RPi_Brightness_slider.valueChanged.connect(
            lambda: self.rpi_slider(1)
        )
        self.RPi_Contrast_slider.valueChanged.connect(
            lambda: self.rpi_slider(2)
        )
        self.RPi_ISO_slider.valueChanged.connect(
            lambda: self.rpi_slider(3)
        )
        ######################################################################

        vid_thread = threading.Thread(target=self.play_vid)
        vid_thread.start()

    def rpi_slider(self, option):
        if option == 1:
            self.RPi_Brightness_val.setNum(self.RPi_Brightness_slider.value())
        elif option == 2:
            self.RPi_Contrast_val.setNum(self.RPi_Contrast_slider.value())
        else:
            self.RPi_ISO_val.setNum(self.RPi_ISO_slider.value())

    def set_scale(self):
        val = int(self.CV_Scale_slider.value())
        self.cam.set_scale(val)
        self.CV_Scale_val.setNum(val)

    def set_neigh(self):
        val = self.CV_Neigh_slider.value()
        self.cam.set_neigh(val)
        self.CV_Neigh_val.setNum(val)

    def button_action(self, text):
        print(f"Button pressed -- {text}")

    def play_vid(self):
        time.sleep(.5)
        while ExitControl.gen:
            time.sleep(.09)
            self.cam.main_loop_support()
            self.frame = self.cam.frame_full
            height, width, chan = self.frame.shape
            bt_line = 3 * width
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            qImg = QImage(self.frame.data, width, height, bt_line, QImage.Format_RGB888)
            img = QtGui.QPixmap.fromImage(qImg)
            pixmap = QPixmap(img)
            self.image_frame.setPixmap(pixmap)

    def start(self):
        self.main_window.show()

    def close(self):
        ExitControl.gen = False
        sys.exit()

    def clean_up(self):
        sys.exit(self.app.exec_())


def cam_starter(robot_type):
    cam = Camera.get_inst(
        robot_type,
        # cam_num=2,
        # lens_type=LensType.DOUBLE,
        # record=True,
        # take_pic=True,
        # disp_img=True
    )
    try:
        cam.start_recognition()
    finally:
        cam.close()


def independent_test():
    from enums import RobotType
    robot_type = RobotType.SPIDER
    cam_thread = threading.Thread(target=cam_starter, args=(robot_type,))
    cam_thread.start()
    ui = GUI(robot_type)
    ui.start()


if __name__ == "__main__":
    independent_test()
