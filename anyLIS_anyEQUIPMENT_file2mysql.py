#!/usr/bin/python3

#basic class will be imported from here
import astm_file2mysql_general as astmg

import sys, logging, time

#For mysql password
sys.path.append('/var/gmcs_config')
import astm_var


log=1
my_host='127.0.0.1'
my_user=astm_var.my_user
my_pass=astm_var.my_pass
my_db='biochemistry'

inbox='/root/ashish.data/'
archived='/root/ashish.arch/'
log_filename='/var/log/ashish.log'

logging.basicConfig(filename=log_filename,level=logging.DEBUG)
if log==0:
  logging.disable(logging.CRITICAL)



class old_LIS(astmg.astm_file):
  def send_to_mysql(self):
    print(m.final_data)



while True:
  m=old_LIS(inbox,archived)
  if(m.get_first_file()):
    m.analyse_file()
    #print(m.relevant_data)
    m.mk_tuple()
    m.send_to_mysql()
  time.sleep(1)
  
