#!/usr/bin/python3
import astm_bidirectional_general as astmg
import astm_bidirectional_conf as conf

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

  ###################################
  #override this function in subclass
  ###################################
  def manage_read(self,data):
    self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
    self.error_set=self.read_set.union(self.write_set)    #update error set

    #for receiving data
    if(data==b'\x05'):
      self.main_status=1
      self.write_msg=b'\x06'
    if(data==b'\x0a'):
      self.write_msg=b'\x06'
    if(data==b'\x04'):
      self.main_status=0

    #for sending data
    if(data==b'\x06'):
      if(self.main_status=1):
        self.main_status=2
      if(self.main_status=3):
        self.main_status=4

  ###################################
  #override this function in subclass
  ###################################
  def initiate_write(self):
    if(self.main_status!=0):
      self.print_to_log('main_status!=0','initiate_write() will not do anything') 
      return
    else:
      self.print_to_log('main_status=={}'.format(self.main_status),'initiate_write() will find some pending work') 
      self.main_status=2
      self.print_to_log('main_status=={}'.format(self.main_status),'initiate_write() changed status to 2 to send data')

      if(self.send_status==0):                                #eot was sent for sending
        self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
        self.error_set=self.read_set.union(self.write_set)    #update error set
        self.write_msg=b'\x05'                                #set message ACK
        self.send_status=1
        self.print_to_log('send_status=={}'.format(self.send_status),'initiate_write() changed send_status to 1 (ENQ sent to write buffer)')

      if(self.send_status==2):
        self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
        self.error_set=self.read_set.union(self.write_set)    #update error set
        
      #self.get_first_outbox_file()
      #fd=open(self.current_outbox_file,'rb')
      #not to be Locked, it is not being written
      #not locked: tested in get_first...
      #fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)
      #byte_data=fd.read(1024)
      #self.print_to_log('File Content',byte_data)

        self.write_msg=b'\x05' #set message
        self.send_status=1
        self.print_to_log('send_status=={}'.format(self.send_status),'initiate_write() changed send_status to 1 (ENQ sent to write buffer)')

      #self.get_first_outbox_file()
      #fd=open(self.current_outbox_file,'rb')
      #not to be Locked, it is not being written
      #not locked: tested in get_first...
      #fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)
      #byte_data=fd.read(1024)
      #self.print_to_log('File Content',byte_data)

      #self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
      #self.error_set=self.read_set.union(self.write_set)    #update error set
      #self.write_msg=b'REAL initiate_write() override me. send apple, pineapple \n' #set message
    pass 
 
#Main Code###############################
#use this to device your own script
if __name__=='__main__':
  #print('__name__ is ',__name__,',so running code')
  while True:
    m=astms()
    m.astmg_loop()
    #break; #useful during debugging  
    
