#!/usr/bin/python3
import bidirectional_general as astmg
import astm_bidirectional_conf as conf
import fcntl, signal, logging

from astm_bidirectional_common import my_sql
from astm_bidirectional_common import file_mgmt

class astms(astmg.astmg, file_mgmt):
  def __init__(self):
    self.main_status=0
          #0=neutral
          #1=receiving
          #2=sending

    self.send_status=0
          #1=enq sent
          #2=1st ack received
          #3=data sent
          #4=2nd ack received
          #0=eot sent

    self.set_inbox(conf.inbox_data,conf.inbox_arch)
    self.set_outbox(conf.outbox_data,conf.outbox_arch)

    super().__init__()
    
    self.alarm_time=conf.alarm_time
    signal.signal(signal.SIGALRM, self.signal_handler)

  ###################################
  #override this function in subclass
  ###################################
  #read from enq to eot in single file
  #it will have stx->lf segments, with segment number 1...7..0..7
  def manage_read(self,data):

    #for receiving data
    if(data==b'\x05'):
      signal.alarm(0)
      
      self.main_status=1
      self.write_msg=b'\x06'
      self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
      self.error_set=self.read_set.union(self.write_set)    #update error set

      #new file need not be class global (unlike existing file -> which needs to be deleted)
      new_file=self.get_inbox_filename()
      self.fd=open(new_file,'wb')
      fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)   #lock file
      #Now use this fd for stx-etb/etx frame writing
      self.fd.write(data)
      print_to_log('File Content written:',data)
      
      signal.alarm(self.alarm_time)

    #difficult
    #see if last byte of data is LF or not
    #byte members are int. so int->chr(string) -> to byte
    #elif( chr( data[ len(data) - 1 ] ).encode() == b'\x0a'):
    #easy!!!
    elif(data[-1:] == b'\x0a'):
      signal.alarm(0)
      
      if(self.calculate_and_compare_checksum(data)==True):
        print_to_log('checksum matched:','Proceeding to write')
        self.fd.write(data)
        print_to_log('File Content written:',data)
        
        #removing other characters, not implimented here
        #self.fd.write(data[1:-5])
        #print_to_log('Full data:',data)
        #print_to_log('File Content written:',data[1:-5])
        #donot close, wait for eot
              
        self.write_msg=b'\x06'
        self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
        self.error_set=self.read_set.union(self.write_set)    #update error set      
      else:
        print_to_log('checksum mismatched:','Proceeding to send NAK')
        self.write_msg=b'\x15'
        self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
        self.error_set=self.read_set.union(self.write_set)    #update error set      
        
      signal.alarm(self.alarm_time)
  
    elif(data==b'\x04'):
      signal.alarm(0)

      self.fd.write(data)
      print_to_log('File Content written:',data)

      self.fd.close()
      self.main_status=0
      self.send_status=0
      #no need update set write_set
      
      #no need to set alarm
      #signal.alarm(self.alarm_time)

    #for sending data, not received during receive-transection
    #only during sending transaction
    if(data==b'\x06'):            #ACK

      if(self.send_status==1):
        self.send_status=2
        print_to_log('send_status=={}'.format(self.send_status),'post-ENQ ACK')

      if(self.send_status==3):
        self.send_status=4
        print_to_log('send_status=={}'.format(self.send_status),'post-LF ACK')

    if(data==b'\x15'):            #NAK
      self.send_status=4
      print_to_log('send_status=={}'.format(self.send_status),'post-LF NAK. Some error')
        
  ###################################
  #override this function in subclass
  ###################################
  #This handles only STX-ETX data. NO STX-ETB management is done
  def initiate_write(self):
    print_to_log('main_status={} send_status={}'.format(self.main_status,self.send_status),'Entering initiate_write()') 
    if(self.main_status!=0):
      print_to_log('main_status={} send_status={}'.format(self.main_status,self.send_status),'busy somewhre.. initiate_write() will not initiate anything') 
    else:
      print_to_log('main_status=={}'.format(self.main_status),'initiate_write() will find some pending work') 
      if(self.get_first_outbox_file()==True):                 #There is something to work      
        self.main_status=2                                    #announce that we are busy sending data
        print_to_log('main_status=={}'.format(self.main_status),'initiate_write() changed main_status to 2 to send data')
      else:
        print_to_log('main_status=={}'.format(self.main_status),'no data in outbox. sleeping for a while')
        return

    if(self.main_status==2):                                #in process of sending
      if(self.send_status==0):                                #eot was sent for sending
        self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
        self.error_set=self.read_set.union(self.write_set)    #update error set
        self.write_msg=b'\x05'                                #set message ENQ
        self.send_status=1                                    #status to ENQ sent
        print_to_log('send_status=={}'.format(self.send_status),'initiate_write() sent ENQ to write buffer')
        
      elif(self.send_status==2):                              #First ACK received. Time to send data 
        self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
        self.error_set=self.read_set.union(self.write_set)    #update error set
        
        self.get_first_outbox_file()                          #set current_outbox file
        fd=open(self.outbox_data+self.current_outbox_file,'rb')
        
        #data must not be >1024
        #it will be ETX data , not ETB data
        #Frame number will always be one and only one
        byte_data=fd.read(1024)                               
        
        print_to_log('File Content',byte_data)
        chksum=self.get_checksum(byte_data)
        print_to_log('CHKSUM',chksum)
        self.write_msg=byte_data #set message
        self.send_status=3                                    #dat sent
        print_to_log('send_status=={}'.format(self.send_status),'initiate_write() changed send_status to 3 (data sent to write buffer)')

      elif(self.send_status==4):                              #Second ACK received. Time to send data 
        self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
        self.error_set=self.read_set.union(self.write_set)    #update error set
        self.write_msg=b'\x04'                                #set message EOT
        self.archive_outbox_file()
        self.send_status=0                                    #dat sent
        self.main_status=0
        print_to_log('send_status=={}'.format(self.send_status),'initiate_write() sent EOT')
        print_to_log('main_status=={}'.format(self.main_status),'initiate_write() now, neutral')


  #######Specific funtions for ASTM        
  def get_checksum(self,data):
    checksum=0
    start_chk_counting=False
    for x in data:
      if(x==2):
        start_chk_counting=True
        #Exclude from chksum calculation
        continue

      if(start_chk_counting==True):
        checksum=(checksum+x)%256

      if(x==3):
        start_chk_counting=False
        #Include in chksum calculation
      if(x==23):
        start_chk_counting=False
        #Include in chksum calculation
 
    two_digit_checksum_string='{:X}'.format(checksum).zfill(2)
    return two_digit_checksum_string.encode()

  def compare_checksum(self, received_checksum, calculated_checksum):
    if(received_checksum==calculated_checksum):
      return True
    else:
      return False

  def calculate_and_compare_checksum(self, data):
    calculated_checksum=self.get_checksum(data)
    received_checksum=data[-4:-2]
    print_to_log(
                      'Calculated checsum={}'.format(calculated_checksum),
                      'Received checsum={}'.format(received_checksum)
                      )
    return self.compare_checksum(received_checksum,calculated_checksum)

  def signal_handler(self,signal, frame):
    print_to_log('Alarm Stopped','Signal:{} Frame:{}'.format(signal,frame))    
    try:
      if self.fd!=None:        
        self.fd.close()
        print_to_log('self.signal_handler()','file closed')
    except Exception as my_ex:
      print_to_log('self.signal_handler()','error in closing file:{}'.format(my_ex))
    
    print_to_log('Alarm..response NOT received in stipulated time','data receving/sending may be incomplate')


def print_to_log(object1,object2):
  logging.debug('{} {}'.format(object1,object2))
  
#Main Code###############################
#use this to device your own script
if __name__=='__main__':
  logging.basicConfig(filename=conf.astm_log_filename,level=logging.DEBUG)  
  #print('__name__ is ',__name__,',so running code')
  while True:
    m=astms()
    m.astmg_loop()
    #break; #useful during debugging  
    
