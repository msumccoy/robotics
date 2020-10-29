import logging
import os
import sys
import threading
import tkinter as tk
import tkinter.font as tkFont
import time
import cv2
import psutil
from IPython.external.qt_for_kernel import QtGui
from PIL import Image, ImageTk
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap

import log_set_up
from config import Conf
from camera import Camera
from misc import pretty_time
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
        self.layout = {
            "quit_btn": {
                "row": 10,
                "col": 1,
                "col_span": 1,
                "row_span": 1,
                "sticky": "w",
            },
            "frame": {
                "row": 1,
                "col": 1,
                "col_span": 1,
                "row_span": 1,
                "sticky": "",
            },
            "mem": {
                "row": 1,
                "col": 1,
                "col_span": 1,
                "row_span": 1,
                "sticky": "nw",
            },
        }

        font_style = tkFont.Font(family="Lucida Grande", size=20)

        self.frame = tk.Label(self.root)
        self.mem_label = tk.Label(self.root, font=font_style)
        key = "mem"
        self.mem_label.grid(
            row=self.layout[key]["row"],
            column=self.layout[key]["col"],
            columnspan=self.layout[key]["col_span"],
            rowspan=self.layout[key]["row_span"],
            sticky=self.layout[key]["sticky"],
        )
        img = cv2.cvtColor(self.cam.frame_pure, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(image=Image.fromarray(img))
        self.frame.config(image=img)
        key = "frame"
        self.frame.grid(
            row=self.layout[key]["row"],
            column=self.layout[key]["col"],
            columnspan=self.layout[key]["col_span"],
            rowspan=self.layout[key]["row_span"],
            sticky=self.layout[key]["sticky"],
        )

        self.quit_btn = tk.Button(self.root, text="quit", command=self.close)
        key = "quit_btn"
        self.quit_btn.grid(
            row=self.layout[key]["row"],
            column=self.layout[key]["col"],
            columnspan=self.layout[key]["col_span"],
            rowspan=self.layout[key]["row_span"],
            sticky=self.layout[key]["sticky"],
        )

    def start(self):
        self.update_image()
        self.life_check()
        self.root.mainloop()

    def update_image(self):
        mem_use = self.process.memory_info().rss / 1024
        self.mem_label['text'] = mem_use
        with self.cam.lock:
            frame_tk = self.cam.frame_full
        img = cv2.cvtColor(frame_tk, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(image=Image.fromarray(img))
        self.frame.config(image=img)
        self.frame.photo_ref = img
        self.root.after(1, self.update_image)

    def life_check(self):
        if not ExitControl.gen:
            self.close()
        self.root.after(1000, self.life_check)

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

    def __init__(self, robot_type):
        self.app = QtWidgets.QApplication(sys.argv)
        super().__init__()
        self.main_window = QtWidgets.QMainWindow()
        self.setupUi(self.main_window)
        # self.cam = Camera.get_inst(robot_type)
        self.cam = cv2.VideoCapture(0)
        _, self.frame = self.cam.read()

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
        self.cont = True
        t = threading.Thread(target=self.play_vid)
        t.start()

    def button_action(self, text):
        print(f"Button pressed -- {text}")

    def play_vid(self):
        while self.cont:
            _, self.frame = self.cam.read()
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
        self.cont = False
        sys.exit()

    def clean_up(self):
        sys.exit(self.app.exec_())


def independent_test():
    from enums import RobotType
    robot_type = RobotType.SPIDER
    ui = GUI2(robot_type)
    ui.start()
    ui.clean_up()


if __name__ == "__main__":
    independent_test()
