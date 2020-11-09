# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_v1.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(734, 548)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.image_frame = QtWidgets.QLabel(self.centralwidget)
        self.image_frame.setGeometry(QtCore.QRect(10, 10, 441, 491))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image_frame.sizePolicy().hasHeightForWidth())
        self.image_frame.setSizePolicy(sizePolicy)
        self.image_frame.setStatusTip("")
        self.image_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.image_frame.setScaledContents(True)
        self.image_frame.setObjectName("image_frame")
        self.btn_close = QtWidgets.QPushButton(self.centralwidget)
        self.btn_close.setGeometry(QtCore.QRect(450, 480, 271, 21))
        self.btn_close.setObjectName("btn_close")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(450, 10, 271, 471))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.CV_Scale_slider = QtWidgets.QSlider(self.tab)
        self.CV_Scale_slider.setGeometry(QtCore.QRect(20, 40, 201, 25))
        self.CV_Scale_slider.setStyleSheet("")
        self.CV_Scale_slider.setMinimum(1)
        self.CV_Scale_slider.setMaximum(30)
        self.CV_Scale_slider.setOrientation(QtCore.Qt.Horizontal)
        self.CV_Scale_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.CV_Scale_slider.setTickInterval(1)
        self.CV_Scale_slider.setObjectName("CV_Scale_slider")
        self.CV_Neigh_slider = QtWidgets.QSlider(self.tab)
        self.CV_Neigh_slider.setGeometry(QtCore.QRect(20, 100, 201, 25))
        self.CV_Neigh_slider.setMinimum(1)
        self.CV_Neigh_slider.setMaximum(30)
        self.CV_Neigh_slider.setOrientation(QtCore.Qt.Horizontal)
        self.CV_Neigh_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.CV_Neigh_slider.setTickInterval(1)
        self.CV_Neigh_slider.setObjectName("CV_Neigh_slider")
        self.CV_Scale_label = QtWidgets.QLabel(self.tab)
        self.CV_Scale_label.setGeometry(QtCore.QRect(20, 20, 81, 20))
        self.CV_Scale_label.setObjectName("CV_Scale_label")
        self.CV_Neigh_label = QtWidgets.QLabel(self.tab)
        self.CV_Neigh_label.setGeometry(QtCore.QRect(20, 80, 111, 16))
        self.CV_Neigh_label.setObjectName("CV_Neigh_label")
        self.CV_Scale_val = QtWidgets.QLabel(self.tab)
        self.CV_Scale_val.setGeometry(QtCore.QRect(230, 40, 31, 16))
        self.CV_Scale_val.setObjectName("CV_Scale_val")
        self.CV_Neigh_val = QtWidgets.QLabel(self.tab)
        self.CV_Neigh_val.setGeometry(QtCore.QRect(230, 100, 31, 16))
        self.CV_Neigh_val.setObjectName("CV_Neigh_val")
        self.RPi_Brightness_val = QtWidgets.QLabel(self.tab)
        self.RPi_Brightness_val.setEnabled(False)
        self.RPi_Brightness_val.setGeometry(QtCore.QRect(230, 160, 31, 16))
        self.RPi_Brightness_val.setObjectName("RPi_Brightness_val")
        self.RPi_Brightness_label = QtWidgets.QLabel(self.tab)
        self.RPi_Brightness_label.setEnabled(False)
        self.RPi_Brightness_label.setGeometry(QtCore.QRect(20, 140, 141, 16))
        self.RPi_Brightness_label.setObjectName("RPi_Brightness_label")
        self.RPi_Brightness_slider = QtWidgets.QSlider(self.tab)
        self.RPi_Brightness_slider.setEnabled(False)
        self.RPi_Brightness_slider.setGeometry(QtCore.QRect(20, 160, 201, 25))
        self.RPi_Brightness_slider.setMinimum(1)
        self.RPi_Brightness_slider.setMaximum(100)
        self.RPi_Brightness_slider.setProperty("value", 50)
        self.RPi_Brightness_slider.setOrientation(QtCore.Qt.Horizontal)
        self.RPi_Brightness_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.RPi_Brightness_slider.setTickInterval(10)
        self.RPi_Brightness_slider.setObjectName("RPi_Brightness_slider")
        self.RPi_Contrast_val = QtWidgets.QLabel(self.tab)
        self.RPi_Contrast_val.setEnabled(False)
        self.RPi_Contrast_val.setGeometry(QtCore.QRect(230, 220, 31, 16))
        self.RPi_Contrast_val.setObjectName("RPi_Contrast_val")
        self.RPi_Contrast_label = QtWidgets.QLabel(self.tab)
        self.RPi_Contrast_label.setEnabled(False)
        self.RPi_Contrast_label.setGeometry(QtCore.QRect(20, 200, 111, 16))
        self.RPi_Contrast_label.setObjectName("RPi_Contrast_label")
        self.RPi_Contrast_slider = QtWidgets.QSlider(self.tab)
        self.RPi_Contrast_slider.setEnabled(False)
        self.RPi_Contrast_slider.setGeometry(QtCore.QRect(20, 220, 201, 25))
        self.RPi_Contrast_slider.setMinimum(1)
        self.RPi_Contrast_slider.setMaximum(100)
        self.RPi_Contrast_slider.setProperty("value", 50)
        self.RPi_Contrast_slider.setOrientation(QtCore.Qt.Horizontal)
        self.RPi_Contrast_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.RPi_Contrast_slider.setTickInterval(10)
        self.RPi_Contrast_slider.setObjectName("RPi_Contrast_slider")
        self.RPi_ISO_val = QtWidgets.QLabel(self.tab)
        self.RPi_ISO_val.setEnabled(False)
        self.RPi_ISO_val.setGeometry(QtCore.QRect(230, 280, 31, 16))
        self.RPi_ISO_val.setObjectName("RPi_ISO_val")
        self.RPi_ISO_slider = QtWidgets.QSlider(self.tab)
        self.RPi_ISO_slider.setEnabled(False)
        self.RPi_ISO_slider.setGeometry(QtCore.QRect(20, 280, 201, 25))
        self.RPi_ISO_slider.setMinimum(0)
        self.RPi_ISO_slider.setMaximum(800)
        self.RPi_ISO_slider.setProperty("value", 0)
        self.RPi_ISO_slider.setOrientation(QtCore.Qt.Horizontal)
        self.RPi_ISO_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.RPi_ISO_slider.setTickInterval(50)
        self.RPi_ISO_slider.setObjectName("RPi_ISO_slider")
        self.RPi_ISO_label = QtWidgets.QLabel(self.tab)
        self.RPi_ISO_label.setEnabled(False)
        self.RPi_ISO_label.setGeometry(QtCore.QRect(20, 260, 111, 16))
        self.RPi_ISO_label.setObjectName("RPi_ISO_label")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.action_buttons = QtWidgets.QWidget(self.tab_2)
        self.action_buttons.setGeometry(QtCore.QRect(10, 10, 241, 211))
        self.action_buttons.setObjectName("action_buttons")
        self.btn_back = QtWidgets.QPushButton(self.action_buttons)
        self.btn_back.setGeometry(QtCore.QRect(80, 130, 80, 80))
        self.btn_back.setObjectName("btn_back")
        self.btn_left = QtWidgets.QPushButton(self.action_buttons)
        self.btn_left.setGeometry(QtCore.QRect(0, 70, 80, 80))
        self.btn_left.setObjectName("btn_left")
        self.btn_stop = QtWidgets.QPushButton(self.action_buttons)
        self.btn_stop.setGeometry(QtCore.QRect(80, 80, 80, 50))
        self.btn_stop.setObjectName("btn_stop")
        self.btn_right = QtWidgets.QPushButton(self.action_buttons)
        self.btn_right.setGeometry(QtCore.QRect(160, 70, 80, 80))
        self.btn_right.setObjectName("btn_right")
        self.btn_forward = QtWidgets.QPushButton(self.action_buttons)
        self.btn_forward.setGeometry(QtCore.QRect(80, 0, 80, 80))
        self.btn_forward.setToolTip("")
        self.btn_forward.setObjectName("btn_forward")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 734, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionRobot_Control = QtWidgets.QAction(MainWindow)
        self.actionRobot_Control.setObjectName("actionRobot_Control")

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.image_frame.setText(_translate("MainWindow", "Put Camera Image Here"))
        self.btn_close.setStatusTip(_translate("MainWindow", "Shortcut = esc"))
        self.btn_close.setText(_translate("MainWindow", "Close"))
        self.btn_close.setShortcut(_translate("MainWindow", "Esc"))
        self.CV_Scale_label.setText(_translate("MainWindow", "Scale Slider"))
        self.CV_Neigh_label.setText(_translate("MainWindow", "Neighbour Slider"))
        self.CV_Scale_val.setText(_translate("MainWindow", "1"))
        self.CV_Neigh_val.setText(_translate("MainWindow", "1"))
        self.RPi_Brightness_val.setText(_translate("MainWindow", "1"))
        self.RPi_Brightness_label.setText(_translate("MainWindow", "RPi Cam Brightness"))
        self.RPi_Contrast_val.setText(_translate("MainWindow", "1"))
        self.RPi_Contrast_label.setText(_translate("MainWindow", "RPi Cam Contras"))
        self.RPi_ISO_val.setText(_translate("MainWindow", "1"))
        self.RPi_ISO_label.setText(_translate("MainWindow", "RPi Cam ISO"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Camera Controls"))
        self.btn_back.setStatusTip(_translate("MainWindow", "Shortcut = Down arrow"))
        self.btn_back.setText(_translate("MainWindow", "Backward"))
        self.btn_back.setShortcut(_translate("MainWindow", "Down"))
        self.btn_left.setStatusTip(_translate("MainWindow", "Shortcut = left arrow"))
        self.btn_left.setText(_translate("MainWindow", "Turn Left"))
        self.btn_left.setShortcut(_translate("MainWindow", "Left"))
        self.btn_stop.setStatusTip(_translate("MainWindow", "Shortcut = spacebar"))
        self.btn_stop.setText(_translate("MainWindow", "Stop"))
        self.btn_stop.setShortcut(_translate("MainWindow", "Space"))
        self.btn_right.setStatusTip(_translate("MainWindow", "Shortcut = right arrow"))
        self.btn_right.setText(_translate("MainWindow", "Turn Right"))
        self.btn_right.setShortcut(_translate("MainWindow", "Right"))
        self.btn_forward.setStatusTip(_translate("MainWindow", "Shortcut = Up arrow"))
        self.btn_forward.setText(_translate("MainWindow", "Forward"))
        self.btn_forward.setShortcut(_translate("MainWindow", "Up"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Robot Control"))
        self.actionRobot_Control.setText(_translate("MainWindow", "Robot Control"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


# test test commit from pycharm

