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
          #0=enq sent
          #1=1st ack received
          #2=data sending
          #3=2nd ack received
          #4=eot sent
    
    self.set_inbox(conf.inbox)
    self.set_outbox(conf.outbox)

    super().__init__()

  ###################################
  #override this function in subclass
  ###################################
  def manage_read(self,data):
    self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
    self.error_set=self.read_set.union(self.write_set)    #update error set
    if(data==b'\x05'):
      self.main_status=1
      self.write_msg=b'\x06'  
    if(data==b'\x0a'):
      self.write_msg=b'\x06'
    if(data==b'\x04'):
      self.main_status=0
  
  ###################################
  #override this function in subclass
  ###################################
  def initiate_write(self):
    if(self.main_status!=0):
      self.print_to_log('main_status!=0','initiate_write() will not do anything') 
      return
    else:
      self.print_to_log('main_status==0','initiate_write() will find some pending work') 
      
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
    
