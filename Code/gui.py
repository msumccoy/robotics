import logging
import os
import tkinter as tk
import tkinter.font as tkFont
import time
import cv2
import psutil
from PIL import Image, ImageTk
import numpy as np

import log_set_up
from config import Conf
from camera import Camera
from misc import pretty_time
from variables import ExitControl


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
