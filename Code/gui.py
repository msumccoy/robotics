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
from PIL import Image, ImageTk
import numpy as np

import log_set_up
from config import Conf
from camera import Camera
from misc import pretty_time
from robot_control import Robot
from variables import ExitControl


class MainClass:
    def __init__(self):
        self.root = tk.Tk()
        self.secondary_window = tk.Toplevel(self.root)
        self.root.title(Conf.CV_WINDOW)  # Set window title
        self.secondary_window.title("Testing system info")  # For posting testing info
        self.secondary_window.geometry("500x500")

        font_style = tkFont.Font(family="Lucida Grande", size=20)
        self.mem_label = tk.Label(self.root, font=font_style)
        self.btn_quit = tk.Button(self.root, text="quit")
        self.main_loop_label = tk.Label(self.root)
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
            self.tab_cam, label="RPi Cam Contrast Slider", from_=-100, to=100,
            orient=tk.HORIZONTAL, length=230
        )
        self.rpi_iso_slider = tk.Scale(
            self.tab_cam, label="RPi Cam ISO Slider", from_=0, to=1600,
            orient=tk.HORIZONTAL, length=230
        )

        self.btn_forward = tk.Button(self.tab_robot, text="Forward")
        self.btn_back = tk.Button(self.tab_robot, text="Backward")
        self.btn_left = tk.Button(self.tab_robot, text="Turn Left")
        self.btn_right = tk.Button(self.tab_robot, text="Turn Right")
        self.btn_stop = tk.Button(self.tab_robot, text="Stop")
        self.btn_kick = tk.Button(self.tab_robot, text="Kick")
        self.btn_dance = tk.Button(self.tab_robot, text="Dance")

        # Set up placement of elements in tabbed window ######################
        # Slider tab
        self.scale_slider.grid(row=1, column=1)
        self.neigh_slider.grid(row=2, column=1)
        self.rpi_brightness_slider.grid(row=3, column=1)
        self.rpi_contrast_slider.grid(row=4, column=1)
        self.rpi_iso_slider.grid(row=5, column=1)

        # set row sizes for sliders
        num_col, num_row = self.tab_cam.grid_size()
        for row in range(1, num_row + 1):
            self.tab_cam.grid_rowconfigure(row, minsize=Conf.G_SLIDE_HEIGHT)

        # Robot Control tab
        self.btn_forward.place(x=90, y=0, height=80, width=80)
        self.btn_back.place(x=90, y=130, height=80, width=80)
        self.btn_left.place(x=10, y=70, height=80, width=80)
        self.btn_right.place(x=170, y=70, height=80, width=80)
        self.btn_stop.place(x=90, y=80, height=50, width=80)
        self.btn_kick.place(x=10, y=230, height=40, width=240)
        self.btn_dance.place(x=10, y=280, height=40, width=240)
        ######################################################################

        # Set up placement for elements in main window #######################
        self.frame.grid(row=1, column=1)
        self.tab_main.grid(row=1, column=2, sticky="nw")
        self.mem_label.grid(row=10, column=2, sticky="nw")
        self.main_loop_label.grid(row=10, column=2, sticky="e")
        self.btn_quit.grid(row=10, column=1, sticky="w")
        ######################################################################
        self.info = tk.Label(self.secondary_window)
        self.info.pack()


class GUI(MainClass):
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    logger = logging.getLogger(Conf.LOG_GUI_NAME)

    def __init__(self, robot_type):
        super().__init__()
        self.main_logger.info(f"GUI: started on version {Conf.VERSION}")
        self.logger.info(
            f"GUI started on version {Conf.VERSION}:"
        )
        self.start_time = time.time()
        self.cam = Camera.get_inst(robot_type)
        self.robot = Robot.get_inst(robot_type)
        self.process = psutil.Process(os.getpid())
        self.btn_quit.configure(command=self.close)

        # Set bindings
        self.root.bind("<Escape>", self.escape)  # Set up escape shortcut
        self.root.bind('<Up>', self.shortcut_btn)
        self.root.bind('<Down>', self.shortcut_btn)
        self.root.bind('<Left>', self.shortcut_btn)
        self.root.bind('<Right>', self.shortcut_btn)
        self.root.bind('<S>', self.shortcut_btn)
        self.root.bind('<s>', self.shortcut_btn)
        self.root.bind('<space>', self.shortcut_btn)
        self.root.bind('<k>', self.shortcut_btn)
        self.root.bind('<K>', self.shortcut_btn)
        self.root.bind('<d>', self.shortcut_btn)
        self.root.bind('<D>', self.shortcut_btn)

        # Set functions executed on movement of slider
        self.scale_slider.configure(command=self.cam.set_scale)
        self.neigh_slider.configure(command=self.cam.set_neigh)
        self.rpi_brightness_slider.configure(command=self.cam.set_brightness)
        self.rpi_contrast_slider.configure(command=self.cam.set_contrast)
        self.rpi_iso_slider.configure(command=self.cam.set_iso)

        # Set shortcuts and commands for robot control buttons
        self.btn_forward.configure(
            command=lambda: self.robot_btn(Conf.CMD_FORWARD)
        )
        self.btn_back.configure(
            command=lambda: self.robot_btn(Conf.CMD_BACKWARD)
        )
        self.btn_left.configure(
            command=lambda: self.robot_btn(Conf.CMD_LEFT)
        )
        self.btn_right.configure(
            command=lambda: self.robot_btn(Conf.CMD_RIGHT)
        )
        self.btn_stop.configure(
            command=lambda: self.robot_btn(Conf.CMD_STOP)
        )
        self.btn_kick.configure(
            command=lambda: self.robot_btn(Conf.CMD_KICK)
        )
        self.btn_dance.configure(
            command=lambda: self.robot_btn(Conf.CMD_DANCE)
        )

        val = (self.cam.settings[self.cam.profile][Conf.CS_SCALE] - 1.005) / 0.1
        self.scale_slider.set(val)
        self.neigh_slider.set(self.cam.settings[self.cam.profile][Conf.CS_NEIGH])
        # Disable pi cam controls if not using pi cam
        if self.cam.is_pi_cam:
            self.rpi_brightness_slider.set(self.cam.cam.brightness)
            self.rpi_contrast_slider.set(self.cam.cam.contrast)
            self.rpi_iso_slider.set(self.cam.cam.iso)
        else:
            self.rpi_brightness_slider.grid_remove()
            self.rpi_contrast_slider.grid_remove()
            self.rpi_iso_slider.grid_remove()

        self.THRESHOLD = Conf.LOOP_DUR_THRESHOLD / 1000

    def start(self):
        self.root.after(1, self.update_image)
        self.root.after(100, self.life_check)
        self.root.after(100, self.check_main_loop_time)
        self.root.mainloop()
        if ExitControl.gen:
            ExitControl.gen = False

    def robot_btn(self, action):
        self.robot.send_command(action)

    def shortcut_btn(self, event):
        print(event)  # delete ###############################################
        if event.keysym == "Up":
            self.btn_forward.invoke()
        elif event.keysym == "Down":
            self.btn_back.invoke()
        elif event.keysym == "Left":
            self.btn_left.invoke()
        elif event.keysym == "Right":
            self.btn_right.invoke()
        elif (
                event.keysym == "s" or event.keysym == "S"
                or event.keysym == "space"
        ):
            self.btn_stop.invoke()
        elif event.keysym == "k" or event.keysym == "K":
            self.btn_kick.invoke()
        elif event.keysym == "d" or event.keysym == "D":
            self.btn_dance.invoke()

    def check_main_loop_time(self):
        mem_use = self.process.memory_info().rss / 1024
        self.mem_label['text'] = mem_use
        self.main_loop_label['text'] = f"{pretty_time(self.cam.main_loop_dur, False)}"
        if self.cam.main_loop_dur > self.THRESHOLD:
            self.main_loop_label['fg'] = "red"
        else:
            self.main_loop_label['fg'] = "black"
        # print(f"{pretty_time(self.cam.main_loop_dur, False)}, {self.i}")
        self.root.after(100, self.check_main_loop_time)

    def update_image(self):
        self.cam.main_loop_support()
        with self.cam.lock:
            frame_tk = self.cam.frame_full
        frame_tk = cv2.resize(
            frame_tk, (Conf.G_FRAME_WIDTH, Conf.G_FRAME_HEIGHT)
        )
        img = cv2.cvtColor(frame_tk, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(image=Image.fromarray(img))
        self.frame.config(image=img)
        self.frame.photo_ref = img
        self.root.after(50, self.update_image)

    def life_check(self):
        # Temporary to place system info into info window  ##################
        self.info['text'] = f"object detected: {self.cam.num_objects}"
        #####################################################################
        if not ExitControl.gen:
            self.close()
        self.root.after(50, self.life_check)  # Change back to 1000 after testing

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


def cam_starter(robot_type):
    cam = Camera.get_inst(
        robot_type,
        cam_num=-1,
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
