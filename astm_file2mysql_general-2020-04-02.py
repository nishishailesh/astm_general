#!/usr/bin/python3
import os
import sys
import MySQLdb
import time
import logging

#to ensure that password is not in main sources
#prototype file is as follows

'''
example /var/gmcs_config/astm_var.py
#!/usr/bin/python3.7
my_user='uuu'
my_pass='ppp'
'''

sys.path.append('/var/gmcs_config')
import astm_var

#check if import successful
#print(dir(astm_var))

#Globals for configuration################
log=1
my_host='127.0.0.1'
my_user=astm_var.my_user
my_pass=astm_var.my_pass
my_db='cl_general'

inbox='/root/astm_general.data/'
archived='/root/astm_general.arch/'
log_filename='/var/log/astm_file2mysql_general.log'
logging.basicConfig(filename=log_filename,level=logging.DEBUG)
if log==0:
  logging.disable(logging.CRITICAL)

##########MYSQL##
def run_query(prepared_sql,data_tpl):
  con=MySQLdb.connect(my_host,my_user,my_pass,my_db)
  if(debug==1): print(con)
  if(con==None):
     if(debug==1): print("Can't connect to database")
  else:
    pass
    #print('connected')
  cur=con.cursor()
  cur.execute(prepared_sql,data_tpl)
  con.commit()
  return cur

def get_single_row(cur):
    return cur.fetchone()

#classes#################################
class astm_file(object):
  
  def __init__(self,inbox_folder,archived_folder):
    self.inbox=inbox_folder
    self.archived=archived_folder
    self.current_file=''
    self.wait_for=''
    self.previous_byte=''
    self.stx=b'\x02'
    self.etx=b'\x03'
    self.eot=b'\x04'
    self.enq=b'\x05'
    self.ack=b'\x06'
    self.lf =b'\x0a'
    self.cr =b'\x0d'
    self.etb=b'\x17'
    
  def get_first_file(self):
    inbox_files=os.listdir(self.inbox)
    for each_file in inbox_files:
      if(os.path.isfile(self.inbox+each_file)):
        self.current_file=each_file
        msg='File in queue is: '+self.current_file
        logging.debug(msg)
        return True
    return False  #no file to read

  def analyse_file(self):
    fh=open(self.inbox+self.current_file,'rb')
    msg='File full path is: '+self.inbox+self.current_file
    logging.debug(msg)
    while True:
      data=fh.read(1)
      #logging.debug(data)
      if data==b'':
        break
      elif data==b'\x06':
        self.manage_ack(data)
        
      elif data==b'\x02':
        self.manage_stx(data)
        
      elif data==b'\x0d':
        self.manage_cr(data)
        
      elif data==b'\x0a':
        self.manage_lf(data)
        
      elif data==b'\x17':
        self.manage_etb(data)
        
      elif data==b'\x03':
        self.manage_etx(data)
        
      elif data==b'\x05':
        self.manage_enq(data)
        
      elif data==b'\x04':
        self.manage_eot(data)

      else:
        self.manage_other(data)
        
      self.previous_byte=data


  def manage_ack(self,data):
    logging.debug('ACK')

  def manage_stx(self,data):
    logging.debug('STX')
    if (self.wait_for==self.stx):
      msg='Received :STX after ENQ. Wait for Frame number'
      logging.debug(msg)
    self.wait_for=''
    
  def manage_cr(self,data):
    logging.debug('CR')

  def manage_lf(self,data):
    logging.debug('LF')

  def manage_etb(self,data):
    logging.debug('ETB')

  def manage_etx(self,data):
    logging.debug('ETX')

  def manage_enq(self,data):
    logging.debug('ENQ')
    self.wait_for=self.stx
    msg='Waiting for :STX '
    logging.debug(msg)
    
  def manage_eot(self,data):
    logging.debug('EOT')

  def manage_other(self,data):
    logging.debug(data)
    if(self.previous_byte==self.stx):
      if chr(ord(data)).isnumeric()==True :
        msg='Number found, it is a frame number:'+ chr(ord(data))
        logging.debug(msg)
      #else:
      #  msg='Number not found???:'+ chr(ord(data))
      #  logging.debug(msg)
    #else:
    #  msg='Previous byte not STX??:'+ chr(ord(data) + ord(self.stx) )
    #  logging.debug(msg)
      
  def send_to_mysql(self):
    #sql='insert into primary_result_blob (sample_id,examination_id,result,uniq) values (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE result=%s'
    #data_tpl=(self.abx_result[30].rstrip(' '),key,self.abx_result[key],self.abx_result[26],self.abx_result[key])
    #run_query(sql,data_tpl)
    pass
 
  def archive_file(self):
    #os.rename(self.inbox+self.current_file,self.archived+self.current_file)
    pass
    
      
#Main Code###############################
if __name__=='__main__':
  #print('__name__ is ',__name__,',so running code')
  while True:
    m=astm_file(inbox,archived)
    if(m.get_first_file()):
      m.analyse_file()
      m.send_to_mysql()
      m.archive_file()
    time.sleep(1)
    break;
  
