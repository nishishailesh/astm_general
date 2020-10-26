#!/usr/bin/python3
import os
import sys
import time
import logging
import json

import astm_bidirectional_conf as conf
from astm_file2mssql_bidirectional_general import astm_file
from astm_bidirectional_common import my_hub 

#For mysql password
#see astm_var.py_example
sys.path.append('/var/')
import astm_var
  
#Main Code###############################

if __name__=='__main__':
  logging.basicConfig(filename=conf.file2mssql_log_filename,level=logging.DEBUG,format='%(asctime)s : %(message)s')  
  h=my_hub(astm_var.CONNECTION_STRING)

  #print('__name__ is ',__name__,',so running code')
  while True:
    m=astm_file()
    if(m.get_first_inbox_file()):
      m.analyse_file()
      m.mk_tuple()
      work_done=False
      for each_sample in m.final_data:
        o_order_id=each_sample[0]      
        h_equipment_id=each_sample[1]
        astm_msg=json.dumps(each_sample[2])
        for_send="{{'o_order_id':'{}','h_equipment_id':'{}','astm':'{}'}}".format(each_sample[0],each_sample[1],astm_msg)
        if(h.send_to_hub(for_send)):
          work_done=True
      if(work_done):
        m.archive_inbox_file() 
    time.sleep(1)
