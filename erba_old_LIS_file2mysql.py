#!/usr/bin/python3

#basic class will be imported from here
import astm_file2mysql_general as astmg

import sys, logging, time

#For mysql password
sys.path.append('/var/gmcs_config')
import astm_var

#--------------------------
######START FOR ASHISH###########
#--------------------------
#Step:1 make a file /var/gmcs_config/astm_var.py
#       it will have three lines shown below

'''
example /var/gmcs_config/astm_var.py
------------------------------------

#!/usr/bin/python3.7
my_user='uuu'
my_pass='ppp'
'''

#Step:2 Change my_host ip to server ip and my_db to your database name
my_host='127.0.0.1'
my_user=astm_var.my_user
my_pass=astm_var.my_pass
my_db='biochemistry'

#Step:2 Create inbox and archived folders as follows
inbox='/root/ashish.data/'
archived='/root/ashish.arch/'
log_filename='/var/log/ashish.log'

#Step:3
# run file ./elba_old_LIS_file2mysql.py
# see out put "tail -f /var/log/ashish.log
#see database updation in LIS

#--------------------------
######END FOR ASHISH###########
#--------------------------



#CRITICAL #application will not work in any case
#WARNING  #aplication will work with some case
#DEBUG    #just detail, not rquired if all is well
log=1
logging.basicConfig(filename=log_filename,level=logging.DEBUG)
#logging.basicConfig(filename=log_filename,level=logging.WARNING)
#logging.basicConfig(filename=log_filename,level=logging.CRITICAL)
if log==0:
  logging.disable(logging.CRITICAL)



class old_LIS(astmg.astm_file):
  def send_to_mysql(self):
    con=self.get_link(my_host,my_user,my_pass,my_db)
    prepared_sql='update examination set result=%s where sample_id=%s and code=%s'
    for each_sample in self.final_data:
      sample_id=each_sample[0]
      logging.debug(sample_id)

      if(sample_id.rstrip(' ').isnumeric() == False):
        logging.debug('sample_id is not number')
        return False;
              
      for each_record in each_sample[1]:
        logging.debug(each_record)
        if(each_record[0]=='R'):
          ex_code=each_record[2].split(self.s3)[3]
          ex_result=each_record[3]
          msg='{}={}'.format(ex_code,ex_result)
          logging.debug(msg)
          data_tpl=(ex_result,sample_id,ex_code)
          try:          
            cur=self.run_query(con,prepared_sql,data_tpl)
            msg='update examination set result="{}" where sample_id="{}" and code="{}"'.format(ex_result,sample_id,ex_code)
            logging.debug(msg)
            logging.debug(cur)
            self.close_cursor(cur)
          except:
            msg='update examination set result="{}" where sample_id="{}" and code="{}"'.format(ex_result,sample_id,ex_code)
            logging.critical(msg)
    self.close_link(con)
while True:
  m=old_LIS(inbox,archived)
  if(m.get_first_file()):
    m.analyse_file()
    logging.debug(m.relevant_data)
    m.mk_tuple()
    m.send_to_mysql()
    m.archive_file()
  time.sleep(1)
  
