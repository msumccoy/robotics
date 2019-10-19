import cv2
import time
from picamera.array import PiRGBArray
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (320, 240)
raw_capture = PiRGBArray(camera)
time1 = time.time()
cycles = 0
while 1:
    cycles += 1
    total_time = time.time() - time1
    average = total_time / cycles
    print("Total = ", total_time)
    print("Average = ", average)
    camera.capture(raw_capture, format="bgr")
    frame = raw_capture.array
    raw_capture.truncate(0)
    cv2.imshow("Full image", frame)
    k = cv2.waitKey(5) & 0xFF
    if k != -1:
        break

camera.close()
cv2.destroyAllWindows()
