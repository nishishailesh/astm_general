#!/usr/bin/python3

import sys, io
import logging
import time
import zlib
import astm_file2mysql_general as astmg
import zlib
import base64
import struct
import matplotlib.pyplot as plt 

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

def mk_graph_from_tuple(x,y,heading,x_axis,y_axis,type_of_chart,axis_range_tuple):
  print(x)
  print(y)
  if(type_of_chart=='HISTOGRAM'):
    plt.plot(x, y) 
  elif(type_of_chart=='MATRIX'):
    plt.plot(x, y,'bo',markersize=1) 
  plt.xlabel(x_axis) 
  plt.ylabel(y_axis)
  plt.axis(axis_range_tuple) 
  plt.title(type_of_chart+':'+heading) 
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
        "EOS%":(41,1)
    }
  def mk_sql(self):
    for each_sample in self.final_data:
      msg='sample_id is {}'.format(each_sample[0])
      sample_id=each_sample[0]
      logging.debug(msg)

      ####main sql edit as per your need####
      #reuse sql
      prepared_sql='insert into primary_result \
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
      self.run_query(my_host,my_user,my_pass,my_db,prepared_sql,data_tpl) 
              
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
          msg='(sid,eid,res,uniq)= ({} , {} , {}, {})'.format(sample_id,ex_name,ex_result,uniq)
          logging.debug(msg)

          if(ex_name in self.yumizon_to_lis):
            data_tpl=(
                       sample_id,\
                       self.yumizon_to_lis[ex_name][0],\
                       float(ex_result)*self.yumizon_to_lis[ex_name][1],\
                       uniq,\
                       float(ex_result)*self.yumizon_to_lis[ex_name][1]
                     )
            
            self.run_query(my_host,my_user,my_pass,my_db,prepared_sql,data_tpl)
                      
        
        elif(each_result[0]=='M'):
          #print(each_result)
          msg_type=each_result[2]
          if(msg_type=='HISTOGRAM' or msg_type=='MATRIX'):
            points=each_result[6].split(self.s3)
            num_tuple=mk_num_tuple_from_def_base_byte_str(points[1])
            #print(num_tuple)
            print('Histogram details'+each_result[4])
            x_display_min=num_tuple[0]
            print('x_display_min=' , x_display_min)
            x_display_max=num_tuple[1]
            print('x_display_max=' , x_display_max)
            y_display_min=num_tuple[2]
            print('y_display_min=' , y_display_min)
            y_display_max=num_tuple[3]
            print('y_display_max=' , y_display_max)
            x_tick_num=int(num_tuple[4])
            print('x_tick_num=' , x_tick_num)
            
            start_cur=5
            end_cur=start_cur + x_tick_num
            xtk=()
            
            #for range(5,5) it does nothing
            for cur in range(start_cur,end_cur):           
              xtk=xtk+(num_tuple[cur],)
            print('xtk values=' , xtk)


            y_tick_num=int(num_tuple[end_cur])
            print('y_tick_num=' , y_tick_num)
            
            start_cur=end_cur+1
            end_cur=start_cur + y_tick_num
            ytk=()
            
            #for range(5,5) it does nothing
            for cur in range(start_cur,end_cur):           
              ytk=ytk+(num_tuple[cur],)
            print('ytk values=' , ytk)

            num_of_list=int(num_tuple[end_cur])
            print('num_of_list=' , num_of_list)

            list_length=int(num_tuple[end_cur+1])
            print('list_length=' , list_length)
            
            start_list=end_cur+2
            xy_list=()
            
            for list_index in range(0,num_of_list):
              end_list=start_list+list_length
              xy_list=xy_list + ( (num_tuple[start_list:end_list]), )
              start_list=start_list+list_length
            #print('xy_list=', xy_list)
            print('making graph...')
            png=b''
            print('length of png=' , len(png))
            axis_range_tuple=(x_display_min,x_display_max,y_display_min,y_display_max)
            png=mk_graph_from_tuple(xy_list[0],xy_list[1],each_result[4],
                                'Cell volume (fL)','Cell Count(x10^3)',msg_type,
                                axis_range_tuple)
            print('length of png=' , len(png))
            fl=open(each_result[4]+'_hg.png','wb')
            fl.write(png)
            fl.close()
            #for pair in range(0,list_length):
            #  print(xy_list[0][pair], xy_list[1][pair])
          
#Main Code###############################
if __name__=='__main__':
  #print('__name__ is ',__name__,',so running code')
  while True:
    m=yumizenp500(inbox,archived)
    if(m.get_first_file()):
      m.analyse_file()
      m.mk_tuple()
      m.mk_sql()
      m.send_to_mysql()
      m.archive_file()
    time.sleep(1)
    #break; #useful during debugging
 
    
