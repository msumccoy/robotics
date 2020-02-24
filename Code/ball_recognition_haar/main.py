"""
Kuwin Wyke
Midwestern State University

This module is used to test the use of haar cascades
"""

import numpy as np
import cv2

cascade_file = 'haarcascade_frontalface_default.xml'
cascade_file = "cascade.xml"

face_cascade = cv2.CascadeClassifier(cascade_file)

cap = cv2.VideoCapture(0)

while 1:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 500, 50)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]

    cv2.imshow('img', img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
