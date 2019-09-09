import io
import picamera
import cv2
import numpy


#def face_dimensions():
#Create a memory stream so photos doesn't need to be saved in a file
stream = io.BytesIO()

#Get the picture (low resolution, so it should be quite fast)
#Here you can also specify other parameters (e.g.:rotate the image)
with picamera.PiCamera() as camera:
    #camera.resolution = (320, 240)
    camera.capture(stream, format='jpeg')
    

#Convert the picture into a numpy array
buff = numpy.fromstring(stream.getvalue(), dtype=numpy.uint8)

#Now creates an OpenCV image adn flip about the x-axis and y-axis
image = cv2.imdecode(buff, 1)
image = cv2.flip(image,0)
image = cv2.flip(image, 1)

#Load a cascade file for detecting faces
face_cascade = cv2.CascadeClassifier('/home/pi/Desktop/cv/faces.xml')

#Convert to grayscale
gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

#Look for faces in the image using the loaded cascade file
faces = face_cascade.detectMultiScale(gray, 1.1, 5)

print "Found "+str(len(faces))+" face(s)"

#Draw a rectangle around every found face
for (x,y,w,h) in faces:
    cv2.rectangle(image,(x,y),(x+w,y+h),(255,255,0),2)
    #### messing around here
    print "x= ", x
    print "y= ", y
    print "w= ", w
    print "h= ", h
    print "x+w= ", x+w
    print "y+h= ", y+h
    print "the center coordinates are x= ",(x + w/2), "and y= " ,(y + h/2)
    face_width = (x + w)
    face_height = (y + h)
    print "the pixel width of the face is ", face_width
    print "the pixel height of the face is ", face_height
    # if 1cm is equal to 0.02646
    pixel_conversion_factor = 0.02646
    calc_diameter = face_width * pixel_conversion_factor
    print "the actual diameter is ", calc_diameter, " centimeters"
    calc_height = face_height * pixel_conversion_factor
    print "calculated height is: ", calc_height, "cm"
    
    

##for (x,y,w,h) in faces:
##    print "the center coordinates are x= ",(x + w/2), "and y= " ,(y + h/2)

####

##for (x,y,w,h) in faces:
##    print
##for (x, y, w, h) in faces:
##                    face_width = (x + w)
##                    face_height = (y + h)
##                    if face_width or face_height >=1:
##
##                        print "the pixel width of the face is ", face_width
##                        print "the pixel height of the face is ", face_height
##                    
##
##                    elif face_width or face_height != int():
##                        print "the values could not be obtained, please try again"

                    #return face_width, face_height

#Save the result image
#cv2.imwrite('result.jpg', image)

if str(len(faces)) >=1:
    # Display the saved image with the recognized faces in a new window
    winName = "Recognized Faces"
    cv2.namedWindow(winName, cv2.WINDOW_AUTOSIZE)

    

# if 1cm is equal to 0.02646
pixel_conversion_factor = 0.02646

####

#def calc_diamater ():  ## actual diameter
calc_diameter = face_width * pixel_conversion_factor
##print "calculated diameter is: ", calc_diameter, "cm"

#def calc_height ():  ## actual height of object in cm
calc_height = face_height * pixel_conversion_factor
##print "calculated height is: ", calc_height, "cm"


while True:
        cv2.imshow(winName, image)
        key = cv2.waitKey(10)
        if key == 27:
            cv2.destroyWindow(winName)
            break

##def size_verification:
##    real_height = 1234  ## in cm
##    real_diameter = 1234  ## in cm
##
##    verified_diameter = real_diamter/calc_diameter)
##    verified_height = real_height/calc_height)
##    if 0.05 < verified_diameter < 2:
##        print "the diameter has been verified "
##    else:
##        print "the diameter could not be verified ", verified_diameter, " is the value given"
##
##    if 0.05 < verified_height < 2:
##        print "the height has been verified "
##    else:
##        print "the height could not be verified", verified_height, "is the value given"
##
##while True:
##    print "Attempting to get dimension"
##    face_dimensions()
##    print "attempting to get diameter"
##    calc_diameter()
##    print "attempting to get height"
##    calc_height()
##    key = cv2.waitKey(10)
##    if key == 27:
##        break









