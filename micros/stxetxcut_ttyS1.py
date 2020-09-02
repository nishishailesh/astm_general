#!/usr/bin/python3.7
import sys
import signal
import datetime
import serial 
import logging
#Globals for debug, debug=1#########
debug=0
logging.basicConfig(filename='/root/micros.log',level=logging.DEBUG)
#logging.debug("hiii");
#Globals for configuration##########
output_folder='/root/inbox1/' #remember ending/
input_tty='/dev/ttyS1'

#For testing
#socat -d -d - pty,raw,echo=0
#input_tty='/dev/pts/2'
alarm_time=10

#functions##########################
def signal_handler(signal, frame):
  if(debug==1): print ('Your alarm is over\nsignal=',signal,'\nframe=',frame,'\n')
  if(debug==1): print(byte_array)
  target_file=get_filename()
  x=open(target_file,'w')
  x.write(''.join(byte_array))
  x.close()
  logging.debug('Data(alarmed) received at '+str(target_file))

def get_filename():
  dt=datetime.datetime.now()
  return output_folder+dt.strftime("%Y-%m-%d-%H-%M-%S-%f")
 
#Globals############################
byte_array=[]
byte=b'd'

#start alarm signal#################
signal.signal(signal.SIGALRM, signal_handler)

#main loop##########################
port = serial.Serial(input_tty, baudrate=9600)

while byte!=b'':
  byte=port.read(1)
  if(byte==b'\x03'):
    if(debug==1): print("<ETX> received\n")
    if(debug==1): print(byte_array)
    signal.alarm(0)
    if(debug==1): print("Alarm Cancelled\n")
    target_file=get_filename()
    x=open(target_file,'w')
    x.write(''.join(byte_array))
    x.close()
    logging.debug('Data received at '+str(filename))
  elif(byte==b'\x02'):
    if(debug==1): print("<STX> received\n")
    byte_array=[]
    signal.alarm(alarm_time)
  elif(byte==b''):
    if(debug==1): print('EOF recived\n')
  else:
    byte_array=byte_array+[chr(ord(byte))]
