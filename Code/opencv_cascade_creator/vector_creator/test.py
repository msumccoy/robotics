import cv2

with open("master_label/info.lst") as file:
    line = file.readline()
    while line != "":
        segments = line.split(" ")
        name = segments[0]
        img = cv2.imread("master_label/" + name)
        num_labels = int(segments[1])
        coors = segments[2:]
        x = 0
        y = 1
        width = 2
        height = 3
        for i in range(num_labels):
            point1 = (int(coors[x]), int(coors[y]))
            point2 = (
                int(coors[x]) + int(coors[width]),
                int(coors[y]) + int(coors[height])
            )
            cv2.rectangle(img, point1, point2, (3, 252, 78))
            x += 4
            y += 4
            width += 4
            height += 4
        try:
            cv2.imshow("l", img)
            k = cv2.waitKey(5000)
        except:
            print(name)
            print(img)
        if k == 27:
            break
        line = file.readline()