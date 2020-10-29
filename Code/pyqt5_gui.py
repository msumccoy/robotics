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
        MainWindow.resize(789, 451)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.image_frame = QtWidgets.QLabel(self.centralwidget)
        self.image_frame.setGeometry(QtCore.QRect(10, 10, 401, 291))
        self.image_frame.setStatusTip("")
        self.image_frame.setObjectName("image_frame")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(440, 30, 300, 250))
        self.widget.setObjectName("widget")
        self.btn_back = QtWidgets.QPushButton(self.widget)
        self.btn_back.setGeometry(QtCore.QRect(100, 150, 100, 100))
        self.btn_back.setObjectName("btn_back")
        self.btn_left = QtWidgets.QPushButton(self.widget)
        self.btn_left.setGeometry(QtCore.QRect(0, 60, 100, 100))
        self.btn_left.setObjectName("btn_left")
        self.btn_stop = QtWidgets.QPushButton(self.widget)
        self.btn_stop.setGeometry(QtCore.QRect(100, 100, 100, 50))
        self.btn_stop.setObjectName("btn_stop")
        self.btn_right = QtWidgets.QPushButton(self.widget)
        self.btn_right.setGeometry(QtCore.QRect(200, 60, 100, 100))
        self.btn_right.setObjectName("btn_right")
        self.btn_forward = QtWidgets.QPushButton(self.widget)
        self.btn_forward.setGeometry(QtCore.QRect(100, 0, 100, 100))
        self.btn_forward.setToolTip("")
        self.btn_forward.setObjectName("btn_forward")
        self.btn_close = QtWidgets.QPushButton(self.centralwidget)
        self.btn_close.setGeometry(QtCore.QRect(680, 380, 80, 23))
        self.btn_close.setObjectName("btn_close")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 789, 20))
        self.menubar.setObjectName("menubar")
        self.menuCamera = QtWidgets.QMenu(self.menubar)
        self.menuCamera.setObjectName("menuCamera")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionRobot_Control = QtWidgets.QAction(MainWindow)
        self.actionRobot_Control.setObjectName("actionRobot_Control")
        self.menuCamera.addAction(self.actionRobot_Control)
        self.menubar.addAction(self.menuCamera.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.image_frame.setText(_translate("MainWindow", "Put Camera Image Here"))
        self.btn_back.setStatusTip(_translate("MainWindow", "Send back command to robot"))
        self.btn_back.setText(_translate("MainWindow", "Backward"))
        self.btn_back.setShortcut(_translate("MainWindow", "Down"))
        self.btn_left.setStatusTip(_translate("MainWindow", "Send turn left command to robot"))
        self.btn_left.setText(_translate("MainWindow", "Turn Left"))
        self.btn_left.setShortcut(_translate("MainWindow", "Left"))
        self.btn_stop.setStatusTip(_translate("MainWindow", "Stop robot motion and disable auto"))
        self.btn_stop.setText(_translate("MainWindow", "Stop"))
        self.btn_stop.setShortcut(_translate("MainWindow", "Space"))
        self.btn_right.setStatusTip(_translate("MainWindow", "Send turn right command to robt"))
        self.btn_right.setText(_translate("MainWindow", "Turn Right"))
        self.btn_right.setShortcut(_translate("MainWindow", "Right"))
        self.btn_forward.setStatusTip(_translate("MainWindow", "Send forward command to robot"))
        self.btn_forward.setText(_translate("MainWindow", "Forward"))
        self.btn_forward.setShortcut(_translate("MainWindow", "Up"))
        self.btn_close.setStatusTip(_translate("MainWindow", "Close program"))
        self.btn_close.setText(_translate("MainWindow", "Close"))
        self.btn_close.setShortcut(_translate("MainWindow", "Esc"))
        self.menuCamera.setTitle(_translate("MainWindow", "Camera"))
        self.actionRobot_Control.setText(_translate("MainWindow", "Robot Control"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

