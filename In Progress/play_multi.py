#!/opt/bin/python
from collections import namedtuple
import serial, time, sys

def play_rcb4_motionS(mtn_num, sleep_wait=0):  #Spider robot
        try:
# write array for Stop Motion
                print("Stopping Motion", stop_motion)
                ser1.write(stop_motion)
                a = ""
                while a == "":
                        a = ser1.read(4)
                print a
                print a.encode("hex")
                time.sleep(0.05)
                
                # write array for Reset Program Counter
                print("Reseting Program Counter", reset_status) # i removed #
                ser1.write(reset_status)
                a = ""
                while a == "":
                        a = ser1.read(4)
                print a  # i added this
                print a.encode("hex")
                time.sleep(0.05)
                
                # write array for Set Motion
                print ("Set Motion", play_motion_bytes[mtn_num])
                ser1.write(play_motion_bytes[mtn_num])
                a = ""
                while a == "":
                        a = ser1.read(4)
                print a.encode("hex")
                
                # write array to run the motion
                print ("Running the Motion %s\n", resume_motion)
                ser1.write(resume_motion)
                a = ""
                while a == "":
                        a = ser1.read(4)
                print a.encode("hex")

                #to clear buffer
                ser1.flush()

	except serial.SerialException:
                #to clear buffer
                ser1.flush()
                ser1.close()
                sys.exit()
                           
	# wait/sleep until the motion ends. this should be hard coded/timed and passed into this function.
	print ("Sleeping ", sleep_wait)
	time.sleep(sleep_wait)
	
	print "Done."

def play_rcb4_motionH(mtn_num, sleep_wait=0):  #Humanoid
        try:
                print("Stopping Motion", stop_motion)
                ser2.write(stop_motion)
                a = ""
                while a == "":
                        a = ser2.read(4)
                print a
                print a.encode("hex")
                time.sleep(0.05)
                
                # write array for Reset Program Counter
                print("Reseting Program Counter", reset_status) # i removed #
                ser2.write(reset_status)
                a = ""
                while a == "":
                        a = ser2.read(4)
                print a  # i added this
                print a.encode("hex")
                time.sleep(0.05)
                
                # write array for Set Motion
                print ("Set Motion", play_motion_bytes[mtn_num])
                ser2.write(play_motion_bytes[mtn_num])
                a = ""
                while a == "":
                        a = ser2.read(4)
                print a.encode("hex")
                
                # write array to run the motion
                print ("Running the Motion %s\n", resume_motion)
                ser2.write(resume_motion)
                a = ""
                while a == "":
                        a = ser2.read(4)
                print a.encode("hex")

                #to clear buffer
                ser2.flush()

        except serial.SerialException:
                 #to clear buffer
                ser2.flush()
                ser2.close()
                sys.exit()
                           
        # wait/sleep until the motion ends. this should be hard coded/timed and passed into this function.
        print ("Sleeping ", sleep_wait)
        time.sleep(sleep_wait)

        print "Done."	

######################################################	
# define code byte sequences for the commands
ack_command = "\x04\xfe\x06\x08" # use for PING. will send 4 bytes and receive another 4 bytes.
get_options = "\x0a\x00\x20\x00\x00\x00\x00\x00\x02\x2c" # not used.


stop_motion = "\x09\x00\x02\x00\x00\x00\x10\x83\x9e"
reset_status = "\x11\x00\x02\x02\x00\x00\x4b\x04\x00\x00\x00\x00\x00\x00\x00\x00\x64"
resume_motion = "\x09\x00\x02\x00\x00\x00\x13\x83\xa1"														

play_motion_bytes = [None] * 101
play_motion_bytes[0] = "\x07\x0c\x80\x0b\x00\x00\x9e"   #Home Position                  NO NOT USE ON HUMANOID
play_motion_bytes[1] = "\x07\x0c\x80\x13\x00\x00\xa6"   #Quick Walk Forward             HOME POSITION
play_motion_bytes[2] = "\x07\x0c\x80\x1b\x00\x00\xae"   #Quick Walk Backward            WAVE
play_motion_bytes[3] = "\x07\x0c\x80\x23\x00\x00\xb6"   #Turn Left One Step             FIST PUMP
play_motion_bytes[4] = "\x07\x0c\x80\x2b\x00\x00\xbe"   #Turn Right One Step            CRYING
play_motion_bytes[5] = "\x07\x0c\x80\x33\x00\x00\xc6"   #Walk Forward 7 Steps           BREAKDANCE
play_motion_bytes[6] = "\x07\x0c\x80\x3b\x00\x00\xce"   #Walk Backward 7 Steps          NOTHING STORED
play_motion_bytes[7] = "\x07\x0c\x80\x43\x00\x00\xd6"   #Turn Left 45 Degrees           CLAP           
play_motion_bytes[8] = "\x07\x0c\x80\x4b\x00\x00\xde"   #Turn Right 45 Degrees          CLAP AND FALL OVER          
play_motion_bytes[9] = "\x07\x0c\x80\x53\x00\x00\xe6"   #High Walk Forward 2 Steps      PUSH UPS     
play_motion_bytes[10] = "\x07\x0c\x80\x5b\x00\x00\xee"  #Dance 1                        RIGHT LEG SQUATS
play_motion_bytes[11] = "\x07\x0c\x80\x63\x00\x00\xf6"  #Dance 2 Wiggle                 JUMP AND FALL OVER
play_motion_bytes[12] = "\x07\x0c\x80\x6b\x00\x00\xfe"  #Turn Right 90 Degrees          STAND UP WHEN ROBOT ON BACK WITH WAVE
play_motion_bytes[13] = "\x07\x0c\x80\x73\x00\x00\x06"  #Turn Left 90 Degrees           STAND UP WHEN ROBOT ON FRONT
play_motion_bytes[14] = "\x07\x0c\x80\x7b\x00\x00\x0e"  #Quick Walk Forward and Backward    STAND UP WHEN ROBOT ON BACK    
play_motion_bytes[15] = "\x07\x0c\x80\x83\x00\x00\x16"  #Quick Wiggle                   WALK FORWARD 6 STEPS                 
play_motion_bytes[16] = "\x07\x0c\x80\x8b\x00\x00\x1e"  #Slow Wiggle                    WALK BACKWARD 6 STEPS
play_motion_bytes[17] = "\x07\x0c\x80\x93\x00\x00\x26"  #Turn Head                      WALK LEFT 5 STEPS
play_motion_bytes[18] = "\x07\x0c\x80\x9b\x00\x00\x2e"  #Slow Walk Forward 3 Steps      WALK RIGHT 5 STEPS
play_motion_bytes[19] = "\x07\x0c\x80\xa3\x00\x00\x36"  #Slow Walk Backward 3 Steps     ROTATE BACKWARDS COUNTER CLOCKWISE
play_motion_bytes[20] = "\x07\x0c\x80\xab\x00\x00\x3e"  #Continuous Walk Forward (50)   ROTATE BACKWARDS CLOCKWISE
play_motion_bytes[21] = "\x07\x0c\x80\xb3\x00\x00\x46"  #Infinite Right turn            WALK FORWARDS 6 BIG STEPS
play_motion_bytes[22] = "\x07\x0c\x80\xbb\x00\x00\x4e"  #Infinite Left Turn             WALK BACKWARDS 6 BIG STEPS
play_motion_bytes[23] = "\x07\x0c\x80\xc3\x00\x00\x56"  #                               WALK LEFT 5 BIG STEPS
play_motion_bytes[24] = "\x07\x0c\x80\xcb\x00\x00\x5e"  #                               WALK RIGHT 5 BIG STEPS
play_motion_bytes[25] = "\x07\x0c\x80\xd3\x00\x00\x66"  #                               LEFT FOOT KICK
play_motion_bytes[26] = "\x07\x0c\x80\xdb\x00\x00\x6e"  #                               RIGHT FOOT KICK
play_motion_bytes[27] = "\x07\x0c\x80\xe3\x00\x00\x76"  #                               LEFT SIDE KICK
play_motion_bytes[28] = "\x07\x0c\x80\xeb\x00\x00\x7e"  #                               RIGHT SIDE KICK
play_motion_bytes[29] = "\x07\x0c\x80\xf3\x00\x00\x86"  #                               LEFT BACK KICK
play_motion_bytes[30] = "\x07\x0c\x80\xfb\x00\x00\x8e"  #                               RIGHT BACK KICK
play_motion_bytes[31] = "\x07\x0c\x80\x03\x01\x00\x97"  #                               NOTHING
play_motion_bytes[32] = "\x07\x0c\x80\x0b\x01\x00\x9f"  #                               SQUAT
play_motion_bytes[33] = "\x07\x0c\x80\x13\x01\x00\xa7"  #                               RIGHT UPPERCUT
play_motion_bytes[34] = "\x07\x0c\x80\x1b\x01\x00\xaf"  #				BACKHAND LEFT
play_motion_bytes[35] = "\x07\x0c\x80\x23\x01\x00\xb7"  #                               BACKHAND RIGHT
play_motion_bytes[36] = "\x07\x0c\x80\x2b\x01\x00\xbf"  #                               LEFT STEP LEFT HAND UP 
play_motion_bytes[37] = "\x07\x0c\x80\x33\x01\x00\xc7"  #                               Right step right hand up
play_motion_bytes[38] = "\x07\x0c\x80\x3b\x01\x00\xd7"  #                               
play_motion_bytes[39] = "\x07\x0c\x80\x43\x01\x00\xdf"
play_motion_bytes[40] = "\x07\x0c\x80\x4b\x01\x00\xe7"
play_motion_bytes[41] = "\x07\x0c\x80\x53\x01\x00\x1f"
play_motion_bytes[42] = "\x07\x0c\x80\x5b\x01\x00\xef"
play_motion_bytes[43] = "\x07\x0c\x80\x63\x01\x00\xe7"
play_motion_bytes[44] = "\x07\x0c\x80\x6b\x01\x00\xff"


######################################################3
# MAIN CODE
#serial port should be "/dev/rfcomm<number>"

## Spider Robot
ser1 = serial.Serial("/dev/rfcomm2", 115200, serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE, timeout = 1) # create and open a serial port
while ser1.isOpen()==False:
        ser1.Open()
#####2018-06-26
time.sleep(0.05)
print("Initializing spider", stop_motion)
ser1.write(stop_motion)
time.sleep(1)
a = ""
while a == "":
	a = ser1.read(4)
#print(a)
#print(a.encode("hex"))
time.sleep(0.05)
#####2018-06-26

## Humanoid Robot        
ser2 = serial.Serial("/dev/rfcomm1", 115200, serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE, timeout = 1) # create and open a serial port
while ser2.isOpen()==False:
        ser2.Open()
#####2018-06-26
time.sleep(0.05)
print("Initializing humanoid", stop_motion)
ser2.write(stop_motion)
time.sleep(1)
a = ""
while a == "":
	a = ser2.read(4)
#print(a)
#print(a.encode("hex"))
time.sleep(0.05)
#####2018-06-26

time.sleep(1)

SP, HR = input("Spider Motion: "), input("Humanoid Motion: ")
play_rcb4_motionS(SP)
play_rcb4_motionH(HR)

ser1.flush()
ser2.flush()
time.sleep(1)
ser1.close()
ser2.close()
time.sleep(1)
              

sys.exit()
