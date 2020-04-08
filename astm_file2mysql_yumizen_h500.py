#!/usr/bin/python3

import sys
import logging
import time
import zlib
import astm_file2mysql_general as astmg

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

inbox='/root/yumizenp500.data/'
archived='/root/yumizenp500.arch/'
log_filename='/var/log/yumizenp500.log'

logging.basicConfig(filename=log_filename,level=logging.DEBUG)
if log==0:
  logging.disable(logging.CRITICAL)



'''
yumizen H500 test codes
========================
DEBUG:root:sample_id is 2021676
DEBUG:root:(sid,eid,res)= (2021676 , PCT , 0.26, 20200407152036),  
DEBUG:root:(sid,eid,res)= (2021676 , NEU# , 1.84, 20200407152036)  
DEBUG:root:(sid,eid,res)= (2021676 , MCV , 83.6, 20200407152036)   MCV
DEBUG:root:(sid,eid,res)= (2021676 , P-LCR , 52.0, 20200407152036)
DEBUG:root:(sid,eid,res)= (2021676 , NEU% , 51.2, 20200407152036)  Neutrophils%
DEBUG:root:(sid,eid,res)= (2021676 , RDW-CV , 14.0, 20200407152036)RDW
DEBUG:root:(sid,eid,res)= (2021676 , MPV , 12.3, 20200407152036)
DEBUG:root:(sid,eid,res)= (2021676 , RBC , 3.63, 20200407152036)   RBC
DEBUG:root:(sid,eid,res)= (2021676 , P-LCC , 109, 20200407152036)
DEBUG:root:(sid,eid,res)= (2021676 , MON# , 0.38, 20200407152036)
DEBUG:root:(sid,eid,res)= (2021676 , WBC , 3.60, 20200407152036)   WBC , 1000
DEBUG:root:(sid,eid,res)= (2021676 , PLT , 209, 20200407152036)    Platelet, 1000
DEBUG:root:(sid,eid,res)= (2021676 , LIC% , 0.2, 20200407152036)
DEBUG:root:(sid,eid,res)= (2021676 , MON% , 10.6, 20200407152036)  Monocyte%
DEBUG:root:(sid,eid,res)= (2021676 , LIC# , 0.01, 20200407152036)
DEBUG:root:(sid,eid,res)= (2021676 , LYM# , 1.24, 20200407152036)  
DEBUG:root:(sid,eid,res)= (2021676 , PDW , 22.9, 20200407152036)
DEBUG:root:(sid,eid,res)= (2021676 , HGB , 10.3, 20200407152036)   Hb
DEBUG:root:(sid,eid,res)= (2021676 , LYM% , 34.4, 20200407152036)  Lymphocyte%
DEBUG:root:(sid,eid,res)= (2021676 , RDW-SD , 50.2, 20200407152036)
DEBUG:root:(sid,eid,res)= (2021676 , BAS% , 1.2, 20200407152036)   Basophil%
DEBUG:root:(sid,eid,res)= (2021676 , BAS# , 0.04, 20200407152036)  
DEBUG:root:(sid,eid,res)= (2021676 , MCH , 28.3, 20200407152036)   MCH
DEBUG:root:(sid,eid,res)= (2021676 , MCHC , 33.9, 20200407152036)  MCHC
DEBUG:root:(sid,eid,res)= (2021676 , HCT , 30.3, 20200407152036)   PCV
DEBUG:root:(sid,eid,res)= (2021676 , EOS# , 0.09, 20200407152036)
DEBUG:root:(sid,eid,res)= (2021676 , EOS% , 2.6, 20200407152036)   Eosinophil%
'''
#sub-class for yumizen H500 ASTM#########

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
          
          
          ####main sql edit as per your need####
          #reuse sql
          prepared_sql='insert into primary_result \
                             (sample_id,examination_id,result,uniq) \
                             values \
                             (%s,%s,%s,%s) \
                             ON DUPLICATE KEY UPDATE result=%s'

          if(ex_name in self.yumizon_to_lis):

            '''
            #how to view sql , for troubleshooting
            pr_prepared_sql="insert into primary_result \
                             (sample_id,examination_id,result,uniq) \
                             values \
                             ('{}','{}','{}','{}') \
                             ON DUPLICATE KEY UPDATE result='{}'".format(\
                             sample_id,self.yumizon_to_lis[ex_name][0], ex_result*self.yumizon_to_lis[ex_name][1] ,uniq,ex_result)
            print(pr_prepared_sql)
            '''

            data_tpl=(
                       sample_id,\
                       self.yumizon_to_lis[ex_name][0],\
                       float(ex_result)*self.yumizon_to_lis[ex_name][1],\
                       uniq,\
                       float(ex_result)*self.yumizon_to_lis[ex_name][1]
                     )
            
            self.run_query(my_host,my_user,my_pass,my_db,prepared_sql,data_tpl)
            
            
          #56, remark
          data_tpl=(
                       sample_id,\
                       56,\
                       'Done on Yumizen H500',\
                       uniq,\
                       'Done on Yumizen H500'
                     )
            
          self.run_query(my_host,my_user,my_pass,my_db,prepared_sql,data_tpl)            
          
          
        '''
        elif(each_result[0]=='M'):
          #print(each_result)
          msg_type=each_result[2]
          if(msg_type=='HISTOGRAM' or  msg_type=='MATRIX' ):
            points=each_result[6].split(self.s3)
            print(points[1])
            msg='Msg_type: {} MsType: {} Name: {} --> Thresold  {}'.format(msg_type, each_result[3],each_result[4],each_result[5])
            logging.debug(msg) 
            #print (zlib.decompress(points[1].encode()))
            f = open(each_result[4], "w")
            f.write(points[1])
            f.close()
         '''   
            
        
  
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
  
    
