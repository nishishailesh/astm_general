#!/usr/bin/python3

import sys
import logging
import time

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

#sub-class for yumizen H500 ASTM#########
class yumizenp500(astmg.astm_file):
  def mk_sql(self):
    for each_sample in self.final_data:
      msg='sample_id is {}'.format(each_sample[0])
      logging.debug(msg)
      for each_result in each_sample[1]:
        msg='Examination: {} --> Result  {}'.format(each_result[2],each_result[3])
        logging.debug(msg)
  
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
  
    
