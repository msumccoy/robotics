# for python 2
from collections import namedtuple
import serial, time, sys #for robot control
import io, picamera, picamera.array, cv2, numpy #for image recognition
import thread
from Queue import Queue

def set_head(new_pos, sleep_wait=0): # Commence Head Movement Function
    # Generate command to set servo position 0 (head servo)
    command = servo_command(new_pos, 0)

    try:

        # write array for Set Sensor array number
        #print ("Set Head position", command)
        ser.write(command)
        a = ""
        while a == "":
            a = ser.read(4)
        #print a.encode("hex")

    except serial.SerialException:
        #to clear buffer
        print ("serial port error")
        ser.flush()
        ser.close()
        sys.exit()


def scan_head(servo_num, sleep_wait=0):
    try:

        # write array for Set Servo array number
        #print ("Read head servo number", servo[servo_num])
        ser.write(servo[servo_num])
        a = ""
        while a == "":
            a = ser.read(9)
        #print a
        #print a.encode("hex")

        b = a[4:6]
        b = b[::-1]
        b_hex = b.encode("hex")
        current_position = int(b_hex, 16)
##        print "b_hex:", b_hex
        print "int b_hex:", current_position
##        print "Done."
        return current_position

    except serial.SerialException:
        # To clear Buffer
        print ("serial port error")
        ser.flush()
        ser.close()
        sys.exit()


def int2hex_str(number):
    hex_num = hex(number)[2:]
    if not (len(hex_num) % 2 == 0):
        hex_num = "0"+hex_num
    return hex_num.decode("hex")


def servo_command(pos, servo_num):
    command_buf = [None] * 7 # generate a command  with 7 bytes
    command_buf[0] = "\x07" # size of command (7 bytes)
    command_buf[1] = "\x0F" # command is to move servo
    command_buf[2] = int2hex_str(servo_num) # set servo number
    command_buf[3] = "\x01" # move at fastest speed
    hex_pos = int2hex_str(pos) # convert position from int to hex
    command_buf[4] = hex_pos[1] # position lower byte
    command_buf[5] = hex_pos[0] # position higher byte

    # compute checksum
    checksum = 0
    for i in range(6):
        checksum = checksum + int(command_buf[i].encode("hex"),16)
    hex_checksum = int2hex_str(checksum) # convert checksum from int to hex
    command_buf[6] = hex_checksum[len(hex_checksum)-1] # checksum byte will be lower byte of the hex_checksum

    # generate command
    command = ""
    for i in range(7):
        command = command + command_buf[i]

    return command


def face_center(facex1):

    #while True:
    with picamera.PiCamera() as camera:
        camera.resolution = (736,480)
        #camera.framerate = 10
        with picamera.array.PiRGBArray(camera) as stream:
            for frame in camera.capture_continuous(stream, format="bgr", use_video_port=True):
            #camera.capture(stream, format='bgr')
            #image = stream.array
                image = frame.array
                image = cv2.flip(image, 0)
                image = cv2.flip(image, 1)

                cv2.imshow('view', image)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Load a cascade file for detecting faces
                face_cascade = cv2.CascadeClassifier('/home/pi/Desktop/cv/faces.xml')

                # Convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Look for faces in the image using the loaded cascade file
                faces = face_cascade.detectMultiScale(gray, 1.1, 5)

                # Draw a rectangle around every found face
                # for (x, y, w, h) in faces:
                #     cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)
                # Find center point of  the face
                facex1.queue.clear()
                if len(faces) >=1:
                    tmp = 0
                    #print ("face found")
                    for (x, y, w, h) in faces:
                        tmp = (x + w / 2) #(y + h / 2)
                    facex1.put(tmp)
                else:
                    #print ("Face not found")
                    facex1.put(None)
                stream.truncate(0)

def input_thread(L):
    data = raw_input()
    L.append(data)

def play_rcb4_motion(mtn_num, sleep_wait=0): # function for running Leg Servos
        try:
                # write array for Stop Motion
                print("Stopping Motion", stop_motion)
                ser.write(stop_motion)
                a = ""
                while a == "":
                        a = ser.read(4)
                print a
                print a.encode("hex")
                time.sleep(0.05)

                # write array for Reset Program Counter
                print("Reseting Program Counter", reset_status) # i removed #
                ser.write(reset_status)
                a = ""
                while a == "":
                        a = ser.read(4)
                print a  # i added this
                print a.encode("hex")
                time.sleep(0.05)

                # write array for Set Motion
                print ("Set Motion", play_motion_bytes[mtn_num])
                ser.write(play_motion_bytes[mtn_num])
                a = ""
                while a == "":
                        a = ser.read(4)
                print a.encode("hex")

                # write array to run the motion
                print ("Running the Motion %s\n", resume_motion)
                ser.write(resume_motion)
                a = ""
                while a == "":
                        a = ser.read(4)
                print a.encode("hex")

                #to clear buffer
                ser.flush()

	except serial.SerialException:
                 #to clear buffer
                ser.flush()
                ser.close()
                sys.exit()

	# wait/sleep until the motion ends. this should be hard coded/timed and passed into this function.
	print ("Sleeping ", sleep_wait)
	time.sleep(sleep_wait)

	print "Done."

def reading(): # Function for using Ultra Sonic sensor

        import time

	import RPi.GPIO as GPIO

	GPIO.setwarnings(False)

	GPIO.setmode(GPIO.BCM)

        GPIO.setup(17,GPIO.OUT)

        GPIO.setup(27,GPIO.IN)

        GPIO.output(17, GPIO.LOW)

        time.sleep(0.3)


        GPIO.output(17, True)


        time.sleep(0.00001)


        GPIO.output(17, False)


        while GPIO.input(27) == 0:
                signaloff = time.time()


        while GPIO.input(27) == 1:
                signalon = time.time()

        timepassed = signalon - signaloff

        distance = timepassed * 17000

        if not(distance>=5 and distance<=90):
                distance = 3000

        GPIO.cleanup()
        return distance


######################################################
# define code byte sequences for the commands
ack_command = "\x04\xfe\x06\x08" # use for PING. will send 4 bytes and receive another 4 bytes.
get_options = "\x0a\x00\x20\x00\x00\x00\x00\x00\x02\x2c" # not used.


stop_motion = "\x09\x00\x02\x00\x00\x00\x10\x83\x9e"
reset_status = "\x11\x00\x02\x02\x00\x00\x4b\x04\x00\x00\x00\x00\x00\x00\x00\x00\x64"
resume_motion = "\x09\x00\x02\x00\x00\x00\x13\x83\xa1"


servo = [None] * 12
servo[0] = "\x0a\x00\x21\x00\x00\x00\x02\x00\x06\x33"
servo[1] = "\x0a\x00\x20\x00\x00\x00\x24\x00\x02\x50"
servo[2] = "\x0a\x00\x20\x00\x00\x00\x26\x00\x02\x52"
servo[3] = "\x0a\x00\x20\x00\x00\x00\x28\x00\x02\x54"
servo[4] = "\x0a\x00\x20\x00\x00\x00\x2a\x00\x02\x56"
servo[5] = "\x0a\x00\x20\x00\x00\x00\x2c\x00\x02\x58"
servo[6] = "\x0a\x00\x20\x00\x00\x00\x2e\x00\x02\x5a"
servo[7] = "\x0a\x00\x20\x00\x00\x00\x30\x00\x02\x5c"
servo[8] = "\x0a\x00\x20\x00\x00\x00\x32\x00\x02\x5e"
servo[9] = "\x0a\x00\x20\x00\x00\x00\x34\x00\x02\x60"
servo[10] = "\x0a\x00\x20\x00\x00\x00\x36\x00\x02\x62"
servo[11] = "\x0a\x00\x20\x00\x00\x00\x22\x00\x02\x4e"  #Formerly 0

##servo_ang = []
##for i in range(21):
##    servo_ang.append(135-4.5*i)


######################################################
# define code byte sequences for the commands
ack_command = "\x04\xfe\x06\x08" # use for PING. will send 4 bytes and receive another 4 bytes.
get_options = "\x0a\x00\x20\x00\x00\x00\x00\x00\x02\x2c" # not used.


stop_motion = "\x09\x00\x02\x00\x00\x00\x10\x83\x9e"
reset_status = "\x11\x00\x02\x02\x00\x00\x4b\x04\x00\x00\x00\x00\x00\x00\x00\x00\x64"
resume_motion = "\x09\x00\x02\x00\x00\x00\x13\x83\xa1"

play_motion_bytes = [None] * 101
play_motion_bytes[0] = "\x07\x0c\x80\x0b\x00\x00\x9e"   #Home Position
play_motion_bytes[1] = "\x07\x0c\x80\x13\x00\x00\xa6"   #Quick Walk Forward
play_motion_bytes[2] = "\x07\x0c\x80\x1b\x00\x00\xae"   #Quick Walk Backward
play_motion_bytes[3] = "\x07\x0c\x80\x23\x00\x00\xb6"   #Turn Left One Step
play_motion_bytes[4] = "\x07\x0c\x80\x2b\x00\x00\xbe"   #Turn Right One Step
play_motion_bytes[5] = "\x07\x0c\x80\x33\x00\x00\xc6"   #Walk Forward 7 Steps
play_motion_bytes[6] = "\x07\x0c\x80\x3b\x00\x00\xce"   #Walk Backward 7 Steps
play_motion_bytes[7] = "\x07\x0c\x80\x43\x00\x00\xd6"   #Turn Left 45 Degrees
play_motion_bytes[8] = "\x07\x0c\x80\x4b\x00\x00\xde"   #Turn Right 45 Degrees
play_motion_bytes[9] = "\x07\x0c\x80\x53\x00\x00\xe6"   #High Walk Forward 2 Steps
play_motion_bytes[10] = "\x07\x0c\x80\x5b\x00\x00\xee"  #Dance 1
play_motion_bytes[11] = "\x07\x0c\x80\x63\x00\x00\xf6"  #Dance 2 Wiggle
play_motion_bytes[12] = "\x07\x0c\x80\x6b\x00\x00\xfe"  #Turn Right 90 Degrees
play_motion_bytes[13] = "\x07\x0c\x80\x73\x00\x00\x06"  #Turn Left 90 Degrees
play_motion_bytes[14] = "\x07\x0c\x80\x7b\x00\x00\x0e"  #Quick Walk Forward and Backward
play_motion_bytes[15] = "\x07\x0c\x80\x83\x00\x00\x16"  #Quick Wiggle
play_motion_bytes[16] = "\x07\x0c\x80\x8b\x00\x00\x1e"  #Slow Wiggle
play_motion_bytes[17] = "\x07\x0c\x80\x93\x00\x00\x26"  #Turn Head
play_motion_bytes[18] = "\x07\x0c\x80\x9b\x00\x00\x2e"  #Slow Walk Forward 3 Steps
play_motion_bytes[19] = "\x07\x0c\x80\xa3\x00\x00\x36"  #Slow Walk Backward 3 Steps
play_motion_bytes[20] = "\x07\x0c\x80\xab\x00\x00\x3e"  #Continuous Walk Forward (50)
play_motion_bytes[21] = "\x07\x0c\x80\xb3\x00\x00\x46"  #Infinite Right turn
play_motion_bytes[22] = "\x07\x0c\x80\xbb\x00\x00\x4e"  #Infinite Left Turn


######################################################
# MAIN CODE
# open serial port communication to the robot
ser = serial.Serial("//dev//rfcomm2", 115200, serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE, timeout = 1) # create and open a serial port

while ser.isOpen()==False:
    ser.Open()

imagecenter = 368  # midpoint of X axis
resolution = 1.39  # angle per pixel

facex1 = Queue()
thread.start_new_thread(face_center, (facex1, ))
L = []
thread.start_new_thread(input_thread, (L, ))

while True:
    if L: #stop the loop if there is any keyboard input
        break

    myfacex = facex1.get() #get face coordinate from the queue
    distance = reading()
    distance2 = reading()
    distance3 = reading()

    if not myfacex == None: # found a face
        current_pos = scan_head(0)
        dpixel = myfacex - imagecenter
        new_pos = int (current_pos + resolution * dpixel)
        if new_pos >= 6000 & new_pos <= 9000:
            #print ("moving to new position", new_pos)
            set_head(new_pos)
            # write code here Kenneth
            print("dpixel =", dpixel)
            if -200 < dpixel < 200 and distance > 40: # object far and head center ken
                play_rcb4_motion(18) # walk forward
                time.sleep(2)
            elif -200 < dpixel < 200 and distance <= 40: #object near head center ken
                play_rcb4_motion(7) # turn left 45 degrees ken
                time.sleep(2.5)
                print("distance2 is", distance2)
                if distance2 <= 40: # object near ken
                    play_rcb4_motion(8) # turn right 45 ken
                    time.sleep(2.5)
                    play_rcb4_motion(8) # turn right 45 ken
                    time.sleep(2.5)
                    print("distance3 is", distance3)
                    if distance3 > 40: # no object in front of me
                        play_rcb4_motion(18) # move forward 3 steps ken
                    else:
                        time.sleep(.01)
                elif distance2 > 50:
                    play_rcb4_motion(18) # move forward 3 steps ken
                else:
                    time.sleep(.001)
            elif dpixel <= -200:
                play_rcb4_motion(7) # turn left 45 degrees ken
                time.sleep(2)
            elif dpixel >= 200:
                play_rcb4_motion(8) # turn right 45 degrees ken
                time.sleep(2)
            else:
                time.sleep(.01)
                print("sleeping")
        else:
            print ("position out of range", new_pos)
    elif myfacex == None: # there is no face Kenneth
        time.sleep(.001)

time.sleep(0.5)

ser.flush()
time.sleep(1)
ser.close()
time.sleep(1)

sys.exit()
