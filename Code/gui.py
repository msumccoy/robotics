import logging
import tkinter as tk
import time
import cv2
from PIL import Image, ImageTk

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
        self.layout = {
            "quit_btn": {
                "row": 10,
                "col": 1,
                "col_span": 1,
                "row_span": 1,
            },
            "frame": {
                "row": 1,
                "col": 1,
                "col_span": 1,
                "row_span": 1,
            },
        }

        self.frame = tk.Label(self.root)
        img = cv2.cvtColor(self.cam.frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(image=Image.fromarray(img))
        self.frame.config(image=img)
        self.frame.grid(
            row=self.layout["frame"]["row"],
            column=self.layout["frame"]["col"],
            columnspan=self.layout["frame"]["col_span"],
            rowspan=self.layout["frame"]["row_span"],
        )

        self.quit_btn = tk.Button(self.root, text="quit", command=self.close)
        self.quit_btn.grid(
            row=self.layout["quit_btn"]["row"],
            column=self.layout["quit_btn"]["col"],
            columnspan=self.layout["quit_btn"]["col_span"],
            rowspan=self.layout["quit_btn"]["row_span"],
            sticky="nw"
        )

    def start(self):
        self.update_image()
        self.life_check()
        self.root.mainloop()

    def update_image(self):
        img = cv2.cvtColor(self.cam.frame_pure, cv2.COLOR_BGR2RGB)
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
