#!/usr/bin/python3
import os
import sys
#apt install python3-mysqldb
import MySQLdb
import time
import logging
import fcntl

import astm_bidirectional_conf as conf
from astm_file2mysql_bidirectional_general import astm_file

#For mysql password
sys.path.append('/var/gmcs_config')
import astm_var

#classes#################################
class astm_file_xl1000(astm_file):
  equipment=conf.equipment  #no self. only inside defination 
  def manage_final_data(self):
    print_to_log('final_data',self.final_data)
    con=self.get_link(astm_var.my_host,astm_var.my_user,astm_var.my_pass,astm_var.my_db)
       
    prepared_sql='insert into primary_result \
                             (sample_id,examination_id,result,uniq) \
                             values \
                             (%s,%s,%s,%s) \
                             ON DUPLICATE KEY UPDATE result=%s'


    prepared_sql_q='select r.sample_id,r.examination_id, h.code from result r,host_code h \
                      where \
                        r.sample_id=%s and \
                        r.examination_id=h.examination_id and \
                        h.equipment=%s'
                      
    for each_sample in self.final_data:

      for each_record in each_sample[1]:
        if(each_record[0]=='R'):
          
          sample_id=each_sample[0]
          print_to_log('sample_id',sample_id)

          if(sample_id.rstrip(' ').isnumeric() == False):
            print_to_log('sample_id is not number:',sample_id)
            return False;
                  
          print_to_log('R tuple:',each_record)
          ex_code=each_record[2].split(self.s3)[3]
          ex_result=each_record[3]
          
          #uniq=each_record[12]
          uniq='{}{}'.format(each_record[12],'|XL_1000')
          examination_id=self.get_eid_for_sid_code(con,sample_id,ex_code)
          if(examination_id==False):
            msg="Skipping the while loop once"
            print_to_log(msg,' .. because no eid for this sid and this code')
            continue
          msg='{}={}'.format(examination_id,ex_result)
          print_to_log('examination_id={}'.format(examination_id),'ex_result={}'.format(ex_result))
          
          data_tpl=(sample_id,examination_id,ex_result,uniq,ex_result)
          
          try:          
            cur=self.run_query(con,prepared_sql,data_tpl)
 
            msg=prepared_sql
            print_to_log('R prepared_sql:',msg)
            msg=data_tpl
            print_to_log('R data tuple:',msg)
            print_to_log('R cursor:',cur)            
            self.close_cursor(cur)
            
          except Exception as my_ex:
            msg=prepared_sql
            print_to_log('R prepared_sql:',msg)
            msg=data_tpl
            print_to_log('R data tuple:',msg)
            print_to_log('R exception description:',my_ex)

        if(each_record[0]=='Q'):
          
          #set sample_id, there is ^ for profile and ` for multiple sample_id in xl1000
          #Q|1|^1007149`1007152`1007151`1007150`1007148|||S|||||||O
          #in R record it is plain
          #sample_id=each_sample[0].split(self.s3)[1]
          sample_id_list=each_sample[0].split(self.s3)[1].split(self.s2)
          print_to_log('sample_id_list:',sample_id_list)

          for sample_id in sample_id_list:
            if(sample_id.rstrip(' ').isnumeric() == False):
              print_to_log('sample_id is not number:',sample_id)
              continue;
            
            #get examination codes
            print_to_log('Q tuple:',each_record)
            print_to_log('Q prepared_sql:',prepared_sql_q)
            data_tpl=(sample_id,self.equipment)
            print_to_log('Q data tuple:',data_tpl)
            try: 
              cur=self.run_query(con,prepared_sql_q,data_tpl)
              print_to_log('Q cursor:',cur)
            except Exception as my_ex:
              print_to_log('Q exception description:',my_ex)
            
            single_q_data=self.get_single_row(cur)
            requested_examination_code=()
            while(single_q_data):
              print_to_log('examination_id={}'.format(single_q_data[1]), ' code={}'.format(single_q_data[2]))
              requested_examination_code=requested_examination_code+(single_q_data[2],)
              single_q_data=self.get_single_row(cur)
            
            self.close_cursor(cur)
            
            print_to_log(
                        'Sample ID {}:'.format(sample_id),
                        'Following is requested {}:'.format(requested_examination_code)
                        )
                        
            order_to_send=self.make_order(sample_id,requested_examination_code)
            print_to_log('Order ready',order_to_send)
            fname=self.get_outbox_filename()
            print_to_log('file to be written',fname)
            fd=open(fname,'bw')
            fd.write(order_to_send)
            fd.close()
            print_to_log('file written to outbox .. ',' .. and closed')
          
    self.close_link(con)

  def make_order(self,sample_id,requested_examination_code):
    '''
    <STX>1H|`^&|||MBDC_Online ^V2.11<CR> 
    P|1|0081692|7||Neumann-Raber^Jurg||19330401|M<CR>  
    O|1|00176860^01||^^^SGPTD`^^^SGOTD`|R||20100607074420[T1] ||||A||||Serum<CR>  
    L|1N<CR><ETX>1D<CR><LF>
    '''
    
    '''
    '^^^'+'`^^^'.join(('ALB','CRR'))+'`'
    ^^^ALB`^^^CRR`
    
    b'^^^'+'`^^^'.join(('ALB','CRR')).encode()+b'`'
    
    ex_code^03 = 5-7 ml, -1=10 ml, others are not barcoded
    
    A : Add the requested tests or batteries to the existing sample
    N : New requests accompanying a new sample
    P : Pending sample (Add but don't schedule)
    C : Cancel request for the battery or tests named (Delete Test)

    '''
    
    ex_code_str=b'^^^'+'`^^^'.join(requested_examination_code).encode()+b'`'
    
    
    #frame_number=1 in headerline, but not used, because only one frame(STX-ETX-LF will be sent per EOT)
    print_to_log('seperators ',self.s1)
    header_line=  b'1H'+self.s1.encode()+self.s2.encode()+self.s3.encode()+self.s4.encode()+b'|||cl_general'
    patient_line= b'P|1|||||||'
    #order_line=   b'O|1|'+sample_id.encode()+b'^01||'+ex_code_str+b'|R||||||N||||serum'
    #order_line=   b'O|1|'+sample_id.encode()+b'^02||'+ex_code_str+b'|R||||||N||||serum'
    order_line=   b'O|1|'+sample_id.encode()+b'^03||'+ex_code_str+b'|R||||||N||||serum'
    #order_line=   b'O|1|'+sample_id.encode()+b'||'+ex_code_str+b'|R||||||N||||serum'
    terminator_line=b'L|1N'
    
    str_for_checksum=b'\x02'+header_line+b'\x0d'+patient_line+b'\x0d'+order_line+ b'\x0d'+terminator_line+ b'\x0d\x03'
    checksum=self.get_checksum(str_for_checksum)
    print_to_log('Calculated checksum=: ',checksum)
    final_message=str_for_checksum+checksum+b'\x0d\x0a'
    print_to_log('Final message: ',final_message)
    return final_message
    
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
  
  
      
  def get_eid_for_sid_code(self,con,sid,ex_code):
    logging.debug(sid)
    prepared_sql='select examination_id from result where sample_id=%s'
    data_tpl=(sid,)
    logging.debug(prepared_sql)
    logging.debug(data_tpl)

    cur=self.run_query(con,prepared_sql,data_tpl)
    
    eid_tpl=()
    data=self.get_single_row(cur)
    while data:
      logging.debug(data)
      eid_tpl=eid_tpl+(data[0],)
      data=self.get_single_row(cur)
    logging.debug(eid_tpl)
    

    prepared_sqlc='select examination_id from host_code where code=%s and equipment=%s'
    data_tplc=(ex_code,self.equipment)
    logging.debug(prepared_sqlc)
    logging.debug(data_tplc)
    curc=self.run_query(con,prepared_sqlc,data_tplc)
    
    eid_tplc=()
    datac=self.get_single_row(curc)
    while datac:
      logging.debug(datac)
      eid_tplc=eid_tplc+(datac[0],)
      datac=self.get_single_row(curc)
    logging.debug(eid_tplc)

    ex_id=tuple(set(eid_tpl) & set(eid_tplc))
    logging.debug('final examination id:'+str(ex_id))
    if(len(ex_id)!=1):
      msg="Number of examination_id found is {}. only 1 is acceptable.".format(len(ex_id))
      logging.debug(msg)
      return False
    return ex_id[0]

def print_to_log(object1,object2):
  logging.debug('{} {}'.format(object1,object2))
  
#Main Code###############################
#use this to device your own script


if __name__=='__main__':
  logging.basicConfig(filename=conf.file2mysql_log_filename,level=logging.DEBUG)  

  #print('__name__ is ',__name__,',so running code')
  while True:
    m=astm_file_xl1000()
    if(m.get_first_inbox_file()):
      m.analyse_file()
      m.mk_tuple()
      m.manage_final_data() #specific for each equipment/lis
      m.archive_inbox_file() #comment, useful during debugging
    time.sleep(1)
    #break; #useful during debugging
  
    
