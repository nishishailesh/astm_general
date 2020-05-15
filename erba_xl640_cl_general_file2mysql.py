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
my_db='cl_general'

#Step:3 Create inbox and archived folders as follows
inbox='/root/xl640.data/'
archived='/root/xl640.arch/'
log_filename='/var/log/xl640.out.log'
equipment='XL_640'	#for host_code to examination_id translation from tost_code table

#Step:4
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



class new_LIS(astmg.astm_file):
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
    data_tplc=(ex_code,equipment)
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
     
  def send_to_mysql(self):
    con=self.get_link(my_host,my_user,my_pass,my_db)
    
    #Ashish comment this line    
    #prepared_sql='update primary_result set result=%s where sample_id=%s and examination_id=%s'
    #following is to be done
    
    prepared_sql='insert into primary_result \
                             (sample_id,examination_id,result,uniq) \
                             values \
                             (%s,%s,%s,%s) \
                             ON DUPLICATE KEY UPDATE result=%s'

    
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
          
          #Ashish uniqueness require date and time of different results
          uniq=each_record[12]
          examination_id=self.get_eid_for_sid_code(con,sample_id,ex_code)
          if(examination_id==False):
            msg="Skipping the while loop once"
            logging.warning(msg)
            continue
          msg='{}={}'.format(examination_id,ex_result)
          logging.debug(msg)
          
          #Ashish following is commented
          #data_tpl=(ex_result,sample_id,examination_id)
          #data_tpl will be as follows
          
          data_tpl=(sample_id,examination_id,ex_result,uniq,ex_result)
          
          try:          
            cur=self.run_query(con,prepared_sql,data_tpl)
 
            msg=prepared_sql
            logging.debug(msg)
            msg=data_tpl
            logging.debug(msg)
            logging.debug(cur)
            
            self.close_cursor(cur)
          except Exception as my_ex:
            msg=prepared_sql
            logging.debug(msg)
            msg=data_tpl
            logging.debug(msg)
            logging.critical(msg)
            logging.critical(my_ex)
    self.close_link(con)
while True:
  m=new_LIS(inbox,archived)
  if(m.get_first_file()):
    m.analyse_file()
    logging.debug(m.relevant_data)
    m.mk_tuple()
    m.send_to_mysql()
    m.archive_file()
  time.sleep(1)
  
