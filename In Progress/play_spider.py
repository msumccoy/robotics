#!/opt/bin/python
from collections import namedtuple
import serial, time, sys
# python_playmotion_dynamic_gen_2018_06_26-0502.py
def make_motion_cmd(motion_num):
	"""Return a hex motion command"""
	cmd_buffer = [None] * 7	#create empty command with length of 7 bytes
	cmd_buffer[0] = "07"	#store command length (7 = 7 bytes)
	cmd_buffer[1] = "0c"	#store command type (c = motion)
	cmd_buffer[2] = "80"	#store 80
	
	num_hex = int_to_hex_str(motion_num)	#convert motion number from integer to hex
	
	cmd_buffer[3] = num_hex[-2:]	#store the last two hex values (low byte)
	cmd_buffer[4] = num_hex[-4:-2]	#store the two hex values before the last two (high byte)
	
	cmd_buffer[5] = "00"	#store null
	
	checksum = 0		#create empty checksum
	
	for i in range(6):
		checksum += int(cmd_buffer[i], 16)	#convert hex bytes to int, sum each with previous checksum result

	cmd_buffer[6] = str(hex(checksum)[-2:])		#store the low byte of the final hex checksum
	cmd_hex_str = ""				#create empty placeholder for final command
	
	for i in range(7):
		cmd_hex_str += (r'\x' + cmd_buffer[i])		#merge hex bytes to one command string
	
	cmd_hex_str = cmd_hex_str.decode('string_escape')	#remove extra backslash from escape characters
	return cmd_hex_str					#return hex command string 

def int_to_hex_str(num_int):
	"""Return an integer converted to hex"""
	num_conv = (int(num_int) * 8) + 11	#convert integer number; multiply by 8, start at 11
	num_hex = hex(num_conv)[2:]		#convert number from int to hex, slice "0x" prefix
	
	if not((len(num_hex) % 2) == 0):
		num_hex = "0" + num_hex		#if length is not even, prefix with a 0 to make length even
	
	if ((len(num_hex) >= 4) == 0):
		num_hex = "00" + num_hex	#if length is not 4 or more, prefix with 00
		
	#alternate method to ensure minimum length of 4 using zero as padding
	#hex_num.zfill(4)
	
	return num_hex	#return hex value representing the original integer

def play_rcb4_motion(motion_num, sleep_wait=0):
	#"""Write a motion to serial port"""
	try:
		#write array for Stop Motion
		print("Stopping Motion", stop_motion)
		ser.write(stop_motion)
		a = ""
		while a == "":
			a = ser.read(4)
		print(a)
		print(a.encode("hex"))
		time.sleep(0.05)
		
		#write array for Reset Program Counter
		print("Reseting Program Counter", reset_status)	#debugging
		ser.write(reset_status)
		a = ""
		while a == "":
			a = ser.read(4)
		print(a)					#debugging
		print(a.encode("hex"))
		time.sleep(0.05)
		
		#prepare motion command
		motion_cmd_str = make_motion_cmd(motion_num)
		print("motion number: ", motion_num)		#debugging
		print("Set Motion", repr(motion_cmd_str))	#debugging
		
		#write array for Set Motion
		ser.write(motion_cmd_str)
		a = ""
		while a == "":
			a = ser.read(4)
		print(a.encode("hex"))
		
		#write array to run the motion
		print("Running the Motion %s\n", resume_motion)
		ser.write(resume_motion)
		a = ""
		while a == "":
			a = ser.read(4)
		print(a.encode("hex"))
		
		#clear buffer
		ser.flush()

	except serial.SerialException:
		#clear buffer
		ser.flush()
		ser.close()
		sys.exit()

	#wait/sleep until the motion ends. this should be hard coded/timed and passed into this function.
	print("Sleeping", sleep_wait)
	time.sleep(sleep_wait)
	
	print("Done.")
	

#--------------------------------------
#hardcoded byte sequences for commands
ack_command = "\x04\xfe\x06\x08"	#use for PING. will send 4 bytes and receive another 4 bytes.
get_options = "\x0a\x00\x20\x00\x00\x00\x00\x00\x02\x2c"	#not used

stop_motion = "\x09\x00\x02\x00\x00\x00\x10\x83\x9e"
reset_status = "\x11\x00\x02\x02\x00\x00\x4b\x04\x00\x00\x00\x00\x00\x00\x00\x00\x64"
resume_motion = "\x09\x00\x02\x00\x00\x00\x13\x83\xa1"

##sensor = [None] * 11
##sensor[0] = "\x0a\x00\x20\x00\x00\x00\x22\x00\x02\x4e"
##sensor[1] = "\x0a\x00\x20\x00\x00\x00\x24\x00\x02\x50"
##sensor[2] = "\x0a\x00\x20\x00\x00\x00\x26\x00\x02\x52"
##sensor[3] = "\x0a\x00\x20\x00\x00\x00\x28\x00\x02\x54"
##sensor[4] = "\x0a\x00\x20\x00\x00\x00\x2a\x00\x02\x56"
##sensor[5] = "\x0a\x00\x20\x00\x00\x00\x2c\x00\x02\x58"
##sensor[6] = "\x0a\x00\x20\x00\x00\x00\x2e\x00\x02\x5a"
##sensor[7] = "\x0a\x00\x20\x00\x00\x00\x30\x00\x02\x5c"
##sensor[8] = "\x0a\x00\x20\x00\x00\x00\x32\x00\x02\x5e"
##sensor[9] = "\x0a\x00\x20\x00\x00\x00\x34\x00\x02\x60"
##sensor[10] = "\x0a\x00\x20\x00\x00\x00\x36\x00\x02\x62"
##
##HeadServo = namedtuple("HeadServo", ['position', 'angle'])
##servo_angle = [None] * 21
##servo_angle[0] = HeadServo("\x07\x0F\x00\x01\x70\x17\x9E", 135)
##servo_angle[1] = HeadServo("\x07\x0F\x00\x01\x06\x18\x35", 130.5)
##servo_angle[2] = HeadServo("\x07\x0F\x00\x01\x9C\x18\xCB", 126)
##servo_angle[3] = HeadServo("\x07\x0F\x00\x01\x32\x19\x62", 121.5)
##servo_angle[4] = HeadServo("\x07\x0F\x00\x01\xC8\x19\xF8", 117)
##servo_angle[5] = HeadServo("\x07\x0F\x00\x01\x5E\x1A\x8F", 112.5)
##servo_angle[6] = HeadServo("\x07\x0F\x00\x01\xF4\x1A\x25", 108)
##servo_angle[7] = HeadServo("\x07\x0F\x00\x01\x8A\x1B\xBC", 103.5)
##servo_angle[8] = HeadServo("\x07\x0F\x00\x01\x20\x1C\x53", 99)
##servo_angle[9] = HeadServo("\x07\x0F\x00\x01\xB6\x1C\xE9", 94.5)
##servo_angle[10] = HeadServo("\x07\x0F\x00\x01\x4C\x1D\x80", 90)
##servo_angle[11] = HeadServo("\x07\x0F\x00\x01\xE2\x1D\x16", 85.5)
##servo_angle[12] = HeadServo("\x07\x0F\x00\x01\x78\x1E\xAD", 81)
##servo_angle[13] = HeadServo("\x07\x0F\x00\x01\x0E\x1F\x44", 76.5)
##servo_angle[14] = HeadServo("\x07\x0F\x00\x01\xA4\x1F\xDA", 72)
##servo_angle[15] = HeadServo("\x07\x0F\x00\x01\x3A\x20\x71", 67.5)
##servo_angle[16] = HeadServo("\x07\x0F\x00\x01\xD0\x20\x07", 63)
##servo_angle[17] = HeadServo("\x07\x0F\x00\x01\x66\x21\x9E", 58.5)
##servo_angle[18] = HeadServo("\x07\x0F\x00\x01\xFC\x21\x34", 54)
##servo_angle[19] = HeadServo("\x07\x0F\x00\x01\x92\x22\xCB", 49.5)
##servo_angle[20] = HeadServo("\x07\x0F\x00\x01\x28\x23\x62", 45)

#--------------------------------------
ser = serial.Serial("/dev/rfcomm2", 115200, serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE, timeout = 1)	# create and open a serial port

while ser.isOpen()==False:
	ser.Open()
	
time.sleep(0.05)

print("Initializing spider", stop_motion)
ser.write(stop_motion)
time.sleep(1)
a = ""
while a == "":
	a = ser.read(4)
#print(a)
#print(a.encode("hex"))
time.sleep(0.05)

play_rcb4_motion(int(input("Enter a motion number: ")), 1)

ser.flush()
time.sleep(1)
ser.close()
time.sleep(1)

sys.exit()
