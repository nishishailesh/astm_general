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

'''
if anything is redirected, last newline is added.
To prevent it, use following
I needed this while outputting relevant data to a file via stdout redirection

echo -n `./astm_file2mysql_general.py` > x
'''

#print(dir(astm_var))

sys.path.append('/var/gmcs_config')
import astm_var

#check if import successful

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
    self.next_frame_number=1	#First frame after ENQ-STX is always 1 (not 0)
    self.next_char_chksum_1=False
    self.next_char_chksum_2=False
    self.file_chksum=''
    self.checksum=0
    self.relevant_data=[]
    self.previous_char_was_checksum2=False
    
    self.s1='|'
    self.s2='`'
    self.s3='^'
    self.s4='&'
    
    self.stx=b'\x02'
    self.etx=b'\x03'
    self.eot=b'\x04'
    self.enq=b'\x05'
    self.ack=b'\x06'
    self.lf =b'\x0a'
    self.cr =b'\x0d'
    self.etb=b'\x17'
    self.text_data=b''
    
    self.sample_id=''
    self.result=()      #a tuple to store one sample result
    self.final_data=()  #a tuple to store all sample results of one file
    
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
        two_digit_checksum_string='{chksum:X}'.format(chksum=self.checksum).zfill(2)
        logging.debug('checksum='+two_digit_checksum_string)
        self.next_char_chksum_1=True
        
      elif data==b'\x03':
        self.manage_etx(data)
        two_digit_checksum_string='{chksum:X}'.format(chksum=self.checksum).zfill(2)
        logging.debug('checksum='+two_digit_checksum_string)
        self.next_char_chksum_1=True    
        
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
    self.checksum=0
    
  def manage_cr(self,data):
    logging.debug('CR')
    self.checksum=(self.checksum+ord(data))%256
    if self.previous_char_was_checksum2==False:
      self.relevant_data=self.relevant_data+[chr(ord(data))]
      


  def manage_lf(self,data):
    logging.debug('LF')

  def manage_etb(self,data):
    logging.debug('ETB')
    self.checksum=(self.checksum+ord(data))%256

  def manage_etx(self,data):
    logging.debug('ETX')
    self.checksum=(self.checksum+ord(data))%256

  def manage_enq(self,data):
    logging.debug('ENQ')
    self.wait_for=self.stx
    msg='Waiting for :STX '
    logging.debug(msg)
    
  def manage_eot(self,data):
    logging.debug('EOT')

  def manage_other(self,data):

    logging.debug(data)
    this_is_frame_number=False #by default, it can be local
    
    #verfy frame number
    #if it is make sure it is not part of relevant data
    if(self.previous_byte==self.stx):
      if chr(ord(data)).isnumeric()==True :
        msg='Number found, it is a frame number:'+ chr(ord(data))
        logging.debug(msg)
        if(self.next_frame_number==int(data)):
          this_is_frame_number=True
          msg='Expected frame number :'+ chr(ord(data)) + ' is correct'
          logging.debug(msg)
          self.next_frame_number=self.next_frame_number+1
          if self.next_frame_number>7 :
            self.next_frame_number=0
        else:
          #msg='Un-Expected frame number ??:'+ chr(ord(data) + ' >> Expected '+ self.next_frame_number )
          msg='Un-Expected frame number ??:{} but {} >> Expected '.format(chr(ord(data)), self.next_frame_number)
          logging.debug(msg)
      
    #verify checksum or calculate it
    if self.next_char_chksum_1 ==True:
      self.file_chksum=self.file_chksum + chr(ord(data))
      self.next_char_chksum_1=False
      self.next_char_chksum_2=True
      self.previous_char_was_checksum2=False
      
    elif self.next_char_chksum_2 ==True:
      self.file_chksum=self.file_chksum + chr(ord(data))
      self.next_char_chksum_2=False
      two_digit_checksum_string='{chksum:X}'.format(chksum=self.checksum).zfill(2)  
      self.previous_char_was_checksum2=True
      
      #two_digit_file_checksum_string=''.join(self.file_chksum)              
      two_digit_file_checksum_string=self.file_chksum
      
      if two_digit_file_checksum_string==two_digit_checksum_string:
        msg='Checksum matched'
      else:
        msg='Checksum not matched'+str(self.file_chksum) +'<>'+ two_digit_checksum_string
      logging.debug(msg)  
      self.file_chksum='' 
    else:    
      self.checksum=(self.checksum+ord(data))%256
      #checksum include everything after stx(not stx) including/upto ETB/ETX 
      #ETX,ETB,CR taken care of in its function
      
      self.previous_char_was_checksum2=False

      #include everything except STX,ETX EOT,ETB,LF etc 
      # include CR in its own function (if not after checksum)
      # exclude frame numbers too      
      if this_is_frame_number!=True:
        self.relevant_data=self.relevant_data+[chr(ord(data))]
        
  def send_to_mysql(self):
    #sql='insert into primary_result_blob (sample_id,examination_id,result,uniq) values (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE result=%s'
    #data_tpl=(self.abx_result[30].rstrip(' '),key,self.abx_result[key],self.abx_result[26],self.abx_result[key])
    #run_query(sql,data_tpl)
    pass #useful during debugging
 
  def archive_file(self):
    os.rename(self.inbox+self.current_file,self.archived+self.current_file)
    pass #useful during debugging
    


  def mk_tuple(self):
    raw_data=''.join(m.relevant_data)
    each_line=raw_data.split('\x0d')
    
    #last char is <CR>, so last element of tuple is empty
    for x in each_line:
      if len(x)>0:
        if   x[0]=='H':
          self.on_header(x)
        elif x[0]=='P':
          self.on_patient(x)
        elif x[0]=='O':
          self.on_order(x)
        #elif x[0]=='R':
        #  self.on_result(x)
        elif x[0]=='L':
          self.on_termination(x)
        else:
          self.on_any_other_result(x)
          
    #print(self.final_data)
    for each_sample in self.final_data:
      msg='{}\t{}'.format(each_sample[0],each_sample[1])
      logging.debug(msg)
      
  def on_any_line(self,any_line):
    #print(any_line)
    temp=any_line.split(self.s1)
    logging.debug(temp)    
    return temp 
    
  #must to identify seperators  
  def on_header(self,header_line):
    self.s1=header_line[1]
    self.s2=header_line[2]
    self.s3=header_line[3]
    self.s4=header_line[4]
    header_tuple=self.on_any_line(header_line)

  #must for initialization/cleanup for next sample
  def on_patient(self,patient_line):
    #Manage previous patient (here and last patient on getting termination record
    if len(str(self.sample_id))>0:
      self.final_data=self.final_data + ((self.sample_id,self.result),)
    
    patient_tuple=self.on_any_line(patient_line)
    #initialize
    pstr='New Patient number:{pn} arrived. Initializing...'.format(pn=patient_tuple[1])
    logging.debug(pstr)
    pstr='Previous Sample Id:({psid}) ...'.format(psid=self.sample_id)
    logging.debug(pstr)
    self.sample_id=''
    pstr='Sample Id:({sid}) after initialization'.format(sid=self.sample_id)
    logging.debug(pstr)    

    pstr='Previous Results:({res}) ...'.format(res=self.result)
    logging.debug(pstr)
    self.result=()
    pstr='Results:({res}) after initialization'.format(res=self.result)
    logging.debug(pstr)

  #must for finding sample ID
  def on_order(self,order_line):
    order_tuple=self.on_any_line(order_line)
    #initialize
    self.sample_id=order_tuple[2]
    pstr='New Sample Id:({sid})'.format(sid=self.sample_id)
    logging.debug(pstr)

  '''
  #Removed,  because some equipments report results in 'M' fields, too
  #So better to export data for next processing, instead of taking decision here
  
  def on_result(self,result_line):
    result_tuple=self.on_any_line(result_line)
    #initialize
    examination_id_tuple=result_tuple[2].split(self.s3)
    examination_id=examination_id_tuple[3]
    self.result=self.result + ((examination_id,result_tuple[3],result_tuple[4]),)
    pstr='New Result:({res})'.format(res=self.result)
    logging.debug(pstr)
  '''


  def on_any_other_result(self,result_line):
    result_tuple=self.on_any_line(result_line)
    #initialize
    self.result=self.result + (result_tuple,)
    #pstr='New Result:({res})'.format(res=self.result)
    #logging.debug(pstr)

  #must for writing last results/etc
  def on_termination(self,termination_line):
    termination_tuple=self.on_any_line(termination_line)
    #update final data on recept of new patient and at last on termination
    if len(str(self.sample_id))>0:
      self.final_data=self.final_data + ((self.sample_id,self.result),)

#Main Code###############################
if __name__=='__main__':
  #print('__name__ is ',__name__,',so running code')
  while True:
    m=astm_file(inbox,archived)
    if(m.get_first_file()):
      m.analyse_file()
      m.mk_tuple()
      m.send_to_mysql()
      m.archive_file()
    time.sleep(1)
    #break; #useful during debugging
  
    
