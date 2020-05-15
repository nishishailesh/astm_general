#!/usr/bin/python3
import sys
import fcntl
import struct
import os

#defaults###############

############################
##########Start of (tty vs tcp)######
############################

#tty -> uncoment as needed
#connection_type='tty'
#input_tty='/dev/ttyS2'

#tcp ->uncomment as needed
connection_type='tcp'
#host_address='10.206.10.26'
host_address='11.207.1.1'
#host_address='12.207.3.240'
host_port='2576'

############################
##########END of (tty vs tcp)######
############################

s=None
x=None
logfile_name='/var/log/xl1000.astm.log'
log=1	#0=disable anyother=enable
#output_folder='/root/yumizen_h500.data/' #remember ending/
output_folder='/root/xl1000.data.from.equipment/' #remember ending/
input_folder='/root/xl1000.data.from.host/' #remember ending/
alarm_time=10
status='GET_ENQ_SEND_ENQ'

################################################

#ensure logging module is imported
try:
  import logging
except ModuleNotFoundError:
  exception_return = sys.exc_info()
  print(exception_return)
  print("Generally installed with all python installation. Refere to python documentation.")
  quit()

#ensure that log file is created/available
try:
  logging.basicConfig(filename=logfile_name,level=logging.DEBUG)
  print("See log at {}".format(logfile_name))
except FileNotFoundError:
  exception_return = sys.exc_info()
  print(exception_return)  
  print("{} can not be created. Folder donot exist? No permission?".format(logfile_name))
  quit()

#import other modules
try:
  import signal
  import datetime
  import time
except ModuleNotFoundError:
  exception_return = sys.exc_info()
  logging.debug(exception_return) 
  logging.debug("signal, datetime and serial modules are required. Install them")
  quit()   

#import serial or socket
if(connection_type=='tty'):
  try:
    import serial 
  except ModuleNotFoundError:
    exception_return = sys.exc_info()
    logging.debug(exception_return) 
    logging.debug("serial module (apt install python3-serial) is required. Install them")
    quit()   
elif(connection_type=='tcp'):
  try:
    import socket
  except ModuleNotFoundError:
    exception_return = sys.exc_info()
    logging.debug(exception_return) 
    logging.debug("socket module is required. Generally installed with basic python installation.")
    quit()   


def signal_handler(signal, frame):
  global x									#global file open
  global byte_array							#global array of byte
  global status
  msg='Alarm stopped status={}'.format(status)
  logging.debug(msg)
  sgl='signal:'+str(signal)
  logging.debug(sgl)
  logging.debug(frame)
  
  if(status=='GET_ENQ_SEND_ENQ'):
    logging.debug('Normal Read Break to see if any write work pending')

  
  else:
    msg='Alarm stopped previous status={}'.format(status)    
    logging.debug(msg)
    status='GET_ENQ_SEND_ENQ'
    msg='Noe new status={}'.format(status)    
    logging.debug(msg)
 
  '''   
  if(status!='GET_ENQ_SEND_ENQ'):
    try:
      if x!=None:
        x.write(''.join(byte_array))			#write to file everytime LF received, to prevent big data memory problem
        x.close()
    except Exception as my_ex:
      logging.debug(my_ex)
    
    byte_array=[]							#empty array      
    logging.debug('Alarm.... <EOT> NOT received. data may be incomplate')
  '''
      
    
def get_filename():
  dt=datetime.datetime.now()
  return output_folder+dt.strftime("%Y-%m-%d-%H-%M-%S-%f")

def get_port():
  if(connection_type=='tty'):
    try:
      port = serial.Serial(input_tty, baudrate=9600)	#if read() donot get its byte in 2 seconds it return
      return port
    except:
      exception_return = sys.exc_info()
      logging.debug(exception_return)
      logging.debug('is tty really existing? Quiting')
      quit()
      
  elif(connection_type=='tcp'):
    global s 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    """Set TCP keepalive on an open socket.
    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """    
    s.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE, 1)
 
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
      
    try:
      s.bind((host_address,int(host_port)))	#it is a tuple
    except:
      exception_return = sys.exc_info()
      logging.debug(exception_return)
      logging.debug('Some problem in bind. is ip and port correct? Quiting')
      quit()      
    logging.debug('post-bind pre-listen')
    s.listen(1)
 
    logging.debug('Listening Socket (s) details below:')
    logging.debug(s)    
 
    logging.debug('Waiting for connection from a client....')   
    conn_tuple = s.accept()	#This waits till connected
    logging.debug('Client request received. Listening+ Accepting Socket (conn_tuple) details below:')
    logging.debug(conn_tuple)
    conn_tuple[0].setblocking(0)  #also when recv() get b''
    
    return conn_tuple[0]
  
def my_read(port):
  if(connection_type=='tty'):
    return port.read(1)
  elif(connection_type=='tcp'):
    try:
      return port.recv(1)
    except Exception as my_ex:
      #logging.debug(my_ex)
      #msg='Network disconnection?? non-blocking read status={}'.format(status)
      #logging.debug(msg)
      #return b''	#nonblocking should not return false
      time.sleep(1)  #otherwise high CPU use in nonblocking read
      return False
      
def my_write(port,byte):
  if(connection_type=='tty'):
    return port.write(byte)
  elif(connection_type=='tcp'):
    return port.send(byte)

    
def get_first_file():
  inbox_files=os.listdir(input_folder)
  for each_file in inbox_files:
    if(os.path.isfile(input_folder+each_file)):
      current_file=each_file
      msg='File in queue is: '+current_file
      logging.debug(msg)
      try:
        fh=open(input_folder+current_file,'rb')
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return input_folder+current_file 
      except Exception as my_ex:
        logging.debug(my_ex)
        msg="{} is locked. trying next..".format(input_folder+current_file)
        logging.warning(msg)

  return False  #no file to read

#main loop##########################
if log==0:
  logging.disable(logging.CRITICAL)

signal.signal(signal.SIGALRM, signal_handler)
port=get_port()

#byte=b'd'									#Just to enter the loop
byte_array=[]								#initialized to ensure that first byte can be added
#while byte!=b'':							#removed, EOF should not exit program
while True:
  byte=my_read(port)

  if(byte==b''):
    logging.debug('<EOF> reached. Connection broken: details below')
    #<EOF> never reached with tty unless the device is not existing)
    if(connection_type=='tcp'):
      logging.debug('(Broken) Listening Socket (s) details below:')
      logging.debug(s)
      logging.debug('(From While)Waiting for connection from a client....') 
      conn_tuple = s.accept()	#This waits till connected
      logging.debug('(From While) Client request received. Listening+ Accepting Socket (conn_tuple) details below:')
      logging.debug(conn_tuple)
      port=conn_tuple[0]
      port.setblocking(0)
  elif(byte==False):
    pass   #this is due to nonblocking recv
  else:
    byte_array=byte_array+[chr(ord(byte))]	#add everything read to array, if not EOF. EOF have no ord
    logging.debug(ord(byte))

  if(byte==b'\x05'):
    signal.alarm(0)
    logging.debug('Alarm stopped')
    byte_array=[]				#empty array
    byte_array=byte_array+[chr(ord(byte))]	#add everything read to array requred here to add first byte
    my_write(port,b'\x06');
    cur_file=get_filename()					#get name of file to open
    
    x=open(cur_file,'w')					#open file
    fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)   #lock file

    status='GET_MSG_INCOMPLATE'
    msg='<ENQ> received. <ACK> Sent. status={}'.format(status)
    logging.debug(msg)

    msg='Name of File opened to save data:={}'.format(str(cur_file))    
    logging.debug(msg)
    
    signal.alarm(alarm_time)
    logging.debug('post-enq-ack Alarm started to receive other data')
    
  elif(byte==b'\x0a'):
    signal.alarm(0)
    logging.debug('Alarm stopped. LF received')
    my_write(port,b'\x06');
    try:
      x.write(''.join(byte_array))			#write to file everytime LF received, to prevent big data memory problem
      byte_array=[]							#empty array
    except Exception as my_ex:
      logging.debug(my_ex)
      logging.debug('Tried to write to a non-existant file??')
    
    status='GET_MSG_INCOMPLATE'
    msg='<LF> received. <ACK> Sent. array written to file. byte_array zeroed status={}'.format(status)
    logging.debug(msg)
    
    signal.alarm(alarm_time)
    logging.debug('post-lf-ack Alarm started to receive other data')
  elif(byte==b'\x04'):
    signal.alarm(0)
    logging.debug('Alarm stopped')
    
    try:
      if x!=None:
        x.write(''.join(byte_array))			#write to file everytime LF received, to prevent big data memory problem
        #fcntl.flock(x, fcntl.LOCK_UN)   #unlock file not required, because we are closing it
        x.close()
        
    except Exception as my_ex:
      logging.debug(my_ex)
      
    byte_array=[]							#empty array
    status='GET_ENQ_SEND_ENQ'
    msg='<EOT> received. array( only EOT remaining ) written to file. File closed: status={}'.format(status)
    logging.debug(msg)
    
  if(byte==b'\x06'):

    if(status=='SEND_MSG_ENQ_SENT'):
      status='SEND_MSG_ACK1_RECEIVED'
    if(status=='SEND_MSG_LF_SENT'):
      status='SEND_MSG_ACK2_RECEIVED'      
      
    msg='Received <ACK> from equipment status={}'.format(status)
    logging.debug(msg)
    
    if(status=='SEND_MSG_ACK1_RECEIVED'):
      msg='Will do something here then sending <LF>...'
      logging.debug(msg)
      signal.alarm(0)
      my_write(port,b'\x0a')
      signal.alarm(alarm_time)
      status='SEND_MSG_LF_SENT'
      msg='post <LF>-sent  alarm started to receive 2nd ACK status={}'.format(status)
      logging.debug(msg)

    if(status=='SEND_MSG_ACK2_RECEIVED'):
      signal.alarm(0)
      my_write(port,b'\x04')
      status='GET_ENQ_SEND_ENQ'
      msg='2nd ACK received EOT sent status={}'.format(status)

  if(status=='GET_ENQ_SEND_ENQ'):
    msg='Trying if there is anything in input_folder: {} to write to equipment status={}'.format(input_folder, status)
    logging.debug(msg)
    if(get_first_file()!=False):
      signal.alarm(0)
      my_write(port,b'\x05');
      status='SEND_MSG_ENQ_SENT'
      msg='Sending <ENQ> to equipment, status={}'.format(status)
      logging.debug(msg)
      signal.alarm(alarm_time)
      logging.debug('post ENQ alarm started to watch for ACK from equipment')    
      
