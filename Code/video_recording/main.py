"""
Kuwin Wyke
Midwestern State University

This program is used to test OpenCV's functionality of saving videos
"""
import cv2


def main():
    record_time = 500
    cam = cv2.VideoCapture(0)
    face_detector = cv2.CascadeClassifier(
        "haarcascade_frontalface_default.xml"
    )
    _, frame = cam.read()
    frame_height, frame_width, _ = frame.shape
    output = cv2.VideoWriter(
        "out.avi", cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
        30, (frame_width, frame_height)
    )

    for i in range(record_time):
        _, frame = cam.read()
        faces = face_detector.detectMultiScale(frame, 1.1, 10)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 75, 5))
        cv2.putText(
            frame, str(i), (10, 100),
            cv2.FONT_HERSHEY_PLAIN, 10, (255, 255, 255), 7
        )
        output.write(frame)
        cv2.imshow("hi", frame)
        k = cv2.waitKey(1) & 0xFF
        if k != -1 and k != 255:
            break
        else:
            print(i)

    cam.release()
    output.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
