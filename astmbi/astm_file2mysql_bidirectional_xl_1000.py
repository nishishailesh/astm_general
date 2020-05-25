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

#classes#################################
class astm_file_xl1000(astm_file):
  pass


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
      print_to_log('final_data',m.final_data)
      m.send_to_mysql() #specific for each equipment/lis
      m.archive_inbox_file() #comment, useful during debugging
    time.sleep(1)
    #break; #useful during debugging
  
    
