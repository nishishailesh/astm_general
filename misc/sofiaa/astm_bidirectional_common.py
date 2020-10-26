#!/usr/bin/python3
import os, fcntl,shutil,datetime, logging
import astm_bidirectional_conf as conf

from azure.iot.device import IoTHubDeviceClient, Message


#logging defined in child class, illogical
class file_mgmt(object):
  def __init__(self):
    pass
    
  def set_inbox(self,inbox_data,inbox_arch):
    self.inbox_data=inbox_data
    self.inbox_arch=inbox_arch
    

  def set_outbox(self,outbox_data,outbox_arch):
    self.outbox_data=outbox_data
    self.outbox_arch=outbox_arch

  def get_first_inbox_file(self):
    self.current_inbox_file=''
    inbox_files=os.listdir(self.inbox_data)
    for each_file in inbox_files:
      if(os.path.isfile(self.inbox_data+each_file)):
        self.current_inbox_file=each_file
        print_to_log('current inbox filepath:',self.inbox_data+self.current_inbox_file)
        try:
          fh=open(self.inbox_data+self.current_inbox_file,'rb')
          fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
          return True
        except Exception as my_ex:
         msg="{} is locked. trying next..".format(self.inbox_data+self.current_inbox_file)
         print_to_log(my_ex,msg)
    return False  #no file to read


  def get_first_outbox_file(self):
    self.current_outbox_file=''
    outbox_files=os.listdir(self.outbox_data)
    for each_file in outbox_files:
      if(os.path.isfile(self.outbox_data+each_file)):
        self.current_outbox_file=each_file
        print_to_log('current outbox filepath:',self.outbox_data+self.current_outbox_file)
        try:
          fh=open(self.outbox_data+self.current_outbox_file,'rb')
          fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
          return True
        except Exception as my_ex:
         msg="{} is locked. trying next..".format(self.outbox_data+self.current_outbox_file)
         print_to_log(my_ex,msg)
    return False  #no file to read

  def get_inbox_filename(self):
    dt=datetime.datetime.now()
    return self.inbox_data+dt.strftime("%Y-%m-%d-%H-%M-%S-%f")

  def get_outbox_filename(self):
    dt=datetime.datetime.now()
    return self.outbox_data+dt.strftime("%Y-%m-%d-%H-%M-%S-%f")


  def archive_outbox_file(self):
    shutil.move(self.outbox_data+self.current_outbox_file, self.outbox_arch+self.current_outbox_file)
    #pass #useful during debugging
    #full path from source to destination prevent exception on ovewriting

  def archive_inbox_file(self):
    shutil.move(self.inbox_data+self.current_inbox_file, self.inbox_arch+self.current_inbox_file)

#########PREPARATION############
#az iot hub monitor-events --hub-name DragonflyPHD-IoT-Hub
#tsql -H url -p 1433 -U user -P password -D database
#apt install python3-pip python3-setuptools
#pip3 install azure-iot-device

class  my_hub():
  def __init__(self,CONNECTION_STRING):
    self.client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

  def send_to_hub(self,str):
    try:
      print_to_log( "Sending message:",str)
      self.client.send_message(Message(str))
      print_to_log( "Message successfully sent" ,'No error')
      return True
    except Exception as my_ex:  
      print_to_log( "Message not sent" ,my_ex)
      return False
      
def print_to_log(object1,object2):
  logging.debug('{} {}'.format(object1,object2))
