#!/usr/bin/python3

import sys, io
import logging
import time
import zlib
import astm_file2mysql_general as astmg
import zlib
import base64
import struct

#apt search python3-matplotlib
#apt install python3-matplotlib
#import matplotlib.pyplot as plt 
#import numpy as np 
import datetime

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

sys.path.append('/var/gmcs_config')
import astm_var
#print(dir(astm_var))


#Globals for configuration################
#used by parent class astm_file (so be careful, they are must)

log=1
my_host='127.0.0.1'
my_user=astm_var.my_user
my_pass=astm_var.my_pass
my_db='cl_general'

inbox='/root/yumizen_h500.data/'
archived='/root/yumizen_h500.arch/'
log_filename='/var/log/yumizen_h500.log'

logging.basicConfig(filename=log_filename,level=logging.DEBUG)
if log==0:
  logging.disable(logging.CRITICAL)


#sub-class for yumizen H500 ASTM#########
#zlib.decompress(data, wbits=MAX_WBITS, bufsize=DEF_BUF_SIZE)
#https://docs.python.org/3/library/zlib.html
#Read docs for -15, for no header
def decode_base64_and_inflate( b64string ):
    decoded_data = base64.b64decode( b64string )
    return zlib.decompress( decoded_data , -15)

#not used in this project
def deflate_and_base64_encode( string_val ):
    zlibbed_str = zlib.compress( string_val )
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode( compressed_string )


def mk_num_tuple_from_def_base_byte_str(def_base_byte_str):
  non_base_inflated_str=decode_base64_and_inflate(def_base_byte_str)
  length=len(non_base_inflated_str)
  num_tuple=()
  count=0
  while count<length:
    x=non_base_inflated_str[count:count+4]
    #FLOATLE Little Enedian Float
    #https://docs.python.org/2/library/struct.html#format-characters
    num_value=struct.unpack('f',x)
    num_tuple=num_tuple + (num_value)
    count=count+4
  return num_tuple

def mk_histogram_from_tuple(xy,heading,x_axis,y_axis,axis_range_tuple):
  #print(x)
  #print(y)
  plt.plot(xy[0], xy[1]) 
  plt.xlabel(x_axis) 
  plt.ylabel(y_axis)
  plt.axis(axis_range_tuple) 
  plt.title('HISTOGRAM: '+heading) 
  f = io.BytesIO()
  plt.savefig(f, format='png')
  f.seek(0)
  data=f.read()
  f.close()
  plt.close()	#otherwise graphs will be overwritten, in next loop
  return data

def mk_matrix_from_tuple(xy,heading,x_axis,y_axis,axis_range_tuple):
  #print(x)
  #print(y)
  '''
  0 for LYM box
  1 for MON box
  2 for NEU box
  3 for EOS box
  4 for LIC box
  5 for ALY box
  6 for LL box
  7 for RN box
  8 for RM box
  '''
  colors=('blue','green','red','cyan','#8B6914','#FB00EF','#1E90FF','#FFA500','#95FC01')
  plt.text(0,axis_range_tuple[3]-axis_range_tuple[1]*0.05,' LYM',color=colors[0])
  plt.text(0,axis_range_tuple[3]-axis_range_tuple[1]*0.10,' MON',color=colors[1])
  plt.text(0,axis_range_tuple[3]-axis_range_tuple[1]*0.15,' NEU',color=colors[2])
  plt.text(0,axis_range_tuple[3]-axis_range_tuple[1]*0.20,' EOS',color=colors[3])
  plt.text(0,axis_range_tuple[3]-axis_range_tuple[1]*0.25,' LIC',color=colors[4])
  plt.text(0,axis_range_tuple[3]-axis_range_tuple[1]*0.30,' ALY',color=colors[5])
  plt.text(0,axis_range_tuple[3]-axis_range_tuple[1]*0.35,' LL',color=colors[6])
  plt.text(0,axis_range_tuple[3]-axis_range_tuple[1]*0.40,' RN',color=colors[7])
  plt.text(0,axis_range_tuple[3]-axis_range_tuple[1]*0.45,' RM',color=colors[8])
  

  for i in range(0,len(xy[0])):
    try:
      color=colors[int(xy[3][i])]
    except Exception as my_ex:
      color='black'
    plt.plot(xy[0][i], xy[1][i],'ro',markersize=1,color=color) 
    
  plt.xlabel(x_axis) 
  plt.ylabel(y_axis)
  plt.axis(axis_range_tuple) 
  plt.title('MATRIX: '+heading) 
  f = io.BytesIO()
  plt.savefig(f, format='png')
  f.seek(0)
  data=f.read()
  f.close()
  plt.close()	#otherwise graphs will be overwritten, in next loop
  return data

class yumizenp500(astmg.astm_file):

  #"yumizon_code":(lis_num,multiplication factor)
  
  yumizon_to_lis={
        "MCV":(5,1),
        "NEU%":(39,1),
        "RDW-CV":(8,1),
        "RBC":(2,1),
        "WBC":(1,1000),
        "PLT":(9,1000),
        "MON%":(42,1),
        "HGB":(3,1),
        "LYM%":(40,1),
        "BAS%":(43,1),
        "MCH":(6,1),
        "MCHC":(7,1),
        "HCT":(4,1),
        "EOS%":(41,1),
        "RbcAlongRes":(22,1),
        "PltAlongRes":(23,1),
        "LMNEResAbs":(24,1)
    }
  def mk_sql(self):
    con=self.get_link(my_host,my_user,my_pass,my_db)                              
    for each_sample in self.final_data:
      msg='sample_id is {}'.format(each_sample[0])
      sample_id=each_sample[0]
      logging.debug(msg)

      if(sample_id.rstrip(' ').isnumeric() == False):
        logging.debug('sample_id is not number')
        return False;
      
      ####main sql edit as per your need####
      #reuse sql
      prepared_sql='insert into primary_result \
                             (sample_id,examination_id,result,uniq) \
                             values \
                             (%s,%s,%s,%s) \
                             ON DUPLICATE KEY UPDATE result=%s'

      prepared_sql_blob='insert into primary_result_blob \
                             (sample_id,examination_id,result,uniq) \
                             values \
                             (%s,%s,%s,%s) \
                             ON DUPLICATE KEY UPDATE result=%s'
      
      #56, remark, once only, no uniq value      
      data_tpl=(
                       sample_id,\
                       56,\
                       'Done on automated Yumizen H500',\
                       '',\
                       'Done on automated Yumizen H500'
                     )
                     
      cur=self.run_query(con,prepared_sql,data_tpl) 
      self.close_cursor(cur)
      
      for each_result in each_sample[1]:
        if(each_result[0]=='R'):
          msg='Examination: {} --> Result  {}'.format(each_result[2],each_result[3])
          logging.debug(msg)
          examination_name_tuple=each_result[2].split(self.s3)
          msg='Examination tuple: {} '.format(examination_name_tuple)
          logging.debug(msg)
          ex_name=examination_name_tuple[3]
          ex_result=each_result[3]
          uniq=each_result[11]
          uniq_for_M=uniq
          msg='(sid,eid,res,uniq)= ({} , {} , {}, {})'.format(sample_id,ex_name,ex_result,uniq)
          logging.debug(msg)

          try:
            if(ex_name in self.yumizon_to_lis):
              data_tpl=(
                       sample_id,\
                       self.yumizon_to_lis[ex_name][0],\
                       float(ex_result)*self.yumizon_to_lis[ex_name][1],\
                       uniq,\
                       float(ex_result)*self.yumizon_to_lis[ex_name][1]
                     )
            
              cur=self.run_query(con,prepared_sql,data_tpl) 
              self.close_cursor(cur)
          except Exception as my_ex:
            logging.debug(my_ex)
            logging.debug('\033[0;31mresult of ('+ex_result+') can not be converted to float for multiplication?\033[0m')
            continue

    self.close_link(con)        
          
#Main Code###############################
if __name__=='__main__':
  #print('__name__ is ',__name__,',so running code')
  while True:
    m=yumizenp500(inbox,archived)
    if(m.get_first_file()):
      m.analyse_file()
      m.mk_tuple()
      m.mk_sql()
      m.archive_file()
    time.sleep(1)
    #break; #useful during debugging
 
    
