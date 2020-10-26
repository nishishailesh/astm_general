#!/usr/bin/python3
import os
import sys
#apt install python3-mysqldb
import MySQLdb
import time
import logging
import fcntl

import astm_bidirectional_conf as conf
from astm_bidirectional_common import my_sql, file_mgmt

#classes#################################
class astm_file(file_mgmt,my_sql):

  def __init__(self):
    self.set_inbox(conf.inbox_data,conf.inbox_arch)
    self.set_outbox(conf.outbox_data,conf.outbox_arch)
        
    self.wait_for=''
    self.previous_byte=''
    self.next_frame_number=1  #First frame after ENQ-STX is always 1 (not 0)
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
    
  def analyse_file(self):
    fh=open(self.inbox_data+self.current_inbox_file,'rb')
    print_to_log('File full path is: ', self.inbox_data+self.current_inbox_file)
    
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
        print_to_log('checksum=',two_digit_checksum_string)
        self.next_char_chksum_1=True
        
      elif data==b'\x03':
        self.manage_etx(data)
        two_digit_checksum_string='{chksum:X}'.format(chksum=self.checksum).zfill(2)
        print_to_log('checksum=',two_digit_checksum_string)
        self.next_char_chksum_1=True    
        
      elif data==b'\x05':
        self.manage_enq(data)
        
      elif data==b'\x04':
        self.manage_eot(data)

      else:
        self.manage_other(data)
        
      self.previous_byte=data
   
  def manage_ack(self,data):
    print_to_log('ACK',' detected')

  def manage_stx(self,data):
    print_to_log('STX', ' detected')
    if (self.wait_for==self.stx):
      print_to_log('Received :STX after ENQ',' Waiting for Frame number')
    self.wait_for=''
    self.checksum=0
    
  def manage_cr(self,data):
    print_to_log('CR',' detected')
    self.checksum=(self.checksum+ord(data))%256
    if self.previous_char_was_checksum2==False:
      self.relevant_data=self.relevant_data+[chr(ord(data))]
      
  def manage_lf(self,data):
    print_to_log('LF', ' detected')

  def manage_etb(self,data):
    print_to_log('ETB', ' detected')
    self.checksum=(self.checksum+ord(data))%256

  def manage_etx(self,data):
    print_to_log('ETX', ' detected')
    self.checksum=(self.checksum+ord(data))%256

  def manage_enq(self,data):
    print_to_log('ENQ', ' detected')
    self.wait_for=self.stx
    print_to_log('Waiting for :','STX')
    
  def manage_eot(self,data):
    print_to_log('EOT', ' detected')

  def manage_other(self,data):

    print_to_log('data=',data)
    this_is_frame_number=False #by default, it can be local
    
    #verfy frame number
    #if it is make sure it is not part of relevant data
    if(self.previous_byte==self.stx):
      if chr(ord(data)).isnumeric()==True :
        print_to_log('Number found, it is a frame number:', chr(ord(data)))
        if(self.next_frame_number==int(data)):
          this_is_frame_number=True
          print_to_log(
                        'expected frame number={}: '.format(self.next_frame_number),
                        'same obtained frame number={}'.format(chr(ord(data)))
                        )
          self.next_frame_number=self.next_frame_number+1
          if self.next_frame_number>7 :
            self.next_frame_number=0
        else:
          print_to_log(
                        'expected frame number={}: '.format(self.next_frame_number),
                        'different from obtained frame number={}'.format(chr(ord(data)))
                        )
      
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
      print_to_log('Checksum analysis',msg)  
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
    


  def mk_tuple(self):
    raw_data=''.join(self.relevant_data)  #list of string to to single string
    each_line=raw_data.split('\x0d')
    
    #last char is <CR>, so last element of tuple/list is empty
    for x in each_line:
      if len(x)>0:
        if   x[0]=='H':
          self.on_header(x)             #set delimiters
        elif x[0]=='P':
          self.on_patient(x)            #cleanup
        elif x[0]=='O':
          self.on_order(x)              #set sample_id
        elif x[0]=='Q':
          self.on_query(x)              #cleanup + sample_id
        #elif x[0]=='R':
        #  self.on_result(x)
        elif x[0]=='L':                 #cleanup
          self.on_termination(x)
        else:
          self.on_any_other_result(x)   #all other
          
    print_to_log('self.final_data',self.final_data)
    #for each_sample in self.final_data:
    #  msg='{}\t{}'.format(each_sample[0],each_sample[1])
    #  logging.debug(msg)
      
  def on_any_line(self,any_line):
    #print(any_line)
    temp=any_line.split(self.s1)
    print_to_log('exploded line is: ',temp)    
    return tuple(temp) 
    
  #must to identify seperators  
  def on_header(self,header_line):
    self.s1=header_line[1]
    self.s2=header_line[2]
    self.s3=header_line[3]
    self.s4=header_line[4]
    header_tuple=self.on_any_line(header_line)  #No use of this veriable

  #must for initialization/cleanup for next sample(=patient)
  #patient data complate if (1) next patient come (2) termination record come
  def on_patient(self,patient_line):
    #Manage previous patient here
    #Manage last patient on getting termination record
    if len(str(self.sample_id))>0:    #if previous patient exist
      self.final_data=self.final_data + ((self.sample_id,self.result),)
  
    patient_tuple=self.on_any_line(patient_line)
    
    #initialize
    try:
      print_to_log('New Patient arrived. Initializing...','number:{pn} '.format(pn=patient_tuple[1]))
    except Exception as my_ex:
      pstr='Look at P record <<<{}>>> Is it inappropriate? no patient_tuple[1] found'.format(patient_tuple)      
      print_to_log(pstr,my_ex)
      
    pstr='({psid}) ...'.format(psid=self.sample_id)
    print_to_log('Previous Sample Id:',pstr)
    self.sample_id=''
    pstr='({sid})'.format(sid=self.sample_id)
    print_to_log('Sample Id: after initialization', pstr)    

    pstr='({res}) ...'.format(res=self.result)
    print_to_log('Previous Results:',pstr)
    self.result=()
    pstr='({res})'.format(res=self.result)
    print_to_log('Results: after initialization:',pstr)
    self.result=self.result + (patient_tuple,)
    
  #must for finding sample ID in query record
  def on_query(self,query_line):
    #Manage previous query here (query donot have patient record
    #Manage last query on getting termination record
    if len(str(self.sample_id))>0:    #if previous patient exist
      self.final_data=self.final_data + ((self.sample_id,self.result),)
  
    query_tuple=self.on_any_line(query_line)
    
    #initialize
    try:
      print_to_log('New query arrived. Initializing...','sample_id:{} '.format(query_tuple[2]))
      self.sample_id=query_tuple[2]
    except Exception as my_ex:
      pstr='Look at Q record <<<{}>>> Is it inappropriate? no query_tuple[2] found'.format(query_tuple)
      print_to_log(pstr,my_ex)
      self.sample_id=''

    pstr='({res}) ...'.format(res=self.result)
    print_to_log('Previous Results:',pstr)
    self.result=()
    pstr='({res})'.format(res=self.result)
    print_to_log('Results: after initialization:',pstr)        

    self.result=self.result + (query_tuple,)
  
  #must for finding sample ID in patient record
  def on_order(self,order_line):
    order_tuple=self.on_any_line(order_line)
    #initialize
    self.result=self.result + (order_tuple,)
      
    try:
      self.sample_id=order_tuple[2]
      pstr='New Sample Id:({sid})'.format(sid=self.sample_id)
      logging.debug(pstr)
    except Exception as my_ex:
      pstr='Look at O record <<<{}>>> Is it inappropriate? no order_tuple[2] found'.format(order_tuple)
      logging.debug(pstr)
      logging.debug(my_ex)
          
  def on_any_other_result(self,result_line):
    result_tuple=self.on_any_line(result_line)
    #initialize
    self.result=self.result + (result_tuple,)

  #must for writing last patient results
  def on_termination(self,termination_line):
    termination_tuple=self.on_any_line(termination_line)
    self.result=self.result + (termination_tuple,)
    #update final data on recept of new patient and at last on termination
    if len(str(self.sample_id))>0:
      self.final_data=self.final_data + ((self.sample_id,self.result),)
    
def print_to_log(object1,object2):
  logging.debug('{} {}'.format(object1,object2))
  
#Main Code###############################
#use this to device your own script


if __name__=='__main__':
  logging.basicConfig(filename=conf.file2mysql_log_filename,level=logging.DEBUG)  

  #print('__name__ is ',__name__,',so running code')
  while True:
    m=astm_file()
    if(m.get_first_inbox_file()):
      m.analyse_file()
      m.mk_tuple()
      m.send_to_mysql() #specific for each equipment/lis
      m.archive_inbox_file() #comment, useful during debugging
    time.sleep(1)
    #break; #useful during debugging
  
    
