#!/usr/bin/python3
import os, fcntl,shutil,datetime
import astm_bidirectional_conf as conf

class my_sql(object):
  def get_link(self,my_host,my_user,my_pass,my_db):
    con=MySQLdb.connect(my_host,my_user,my_pass,my_db)
    logging.debug(con)
    if(con==None):
      if(debug==1): logging.debug("Can't connect to database")
    else:
      pass
      logging.debug('connected')
      return con

  def run_query(self,con,prepared_sql,data_tpl):
    cur=con.cursor()
    cur.execute(prepared_sql,data_tpl)
    con.commit()
    msg="rows affected: {}".format(cur.rowcount)
    logging.debug(msg)
    return cur

  def get_single_row(self,cur):
    return cur.fetchone()

  def close_cursor(self,cur):
    cur.close()

  def close_link(self,con):
    con.close()


class file_mgmt(object):
  def __init__(self):
    #logging.basicConfig(filename=conf.log_filename,level=logging.DEBUG)
    #self.logger = logging.getLogger('astm_bidirectional_common')
    pass
    
  def print_to_log(self,my_object,special_message):
    #self.logger.debug('Start=========')
    #self.logger.debug(my_object)
    #self.logger.debug(special_message)
    #self.logger.debug('End=========')
    pass
    
  def set_inbox(self,inbox_data,inbox_arch):
    self.inbox_data=inbox_data
    self.inbox=inbox_arch

  def set_outbox(self,outbox_data,outbox_arch):
    self.outbox_data=outbox_data
    self.outbox_arch=outbox_arch

  def get_first_inbox_file(self):
    self.current_inbox_file=''
    inbox_files=os.listdir(self.inbox_data)
    for each_file in inbox_files:
      if(os.path.isfile(self.inbox_data+each_file)):
        self.current_inbox_file=self.inbox_data+each_file
        self.print_to_log('current inbox  file:',self.current_inbox_file)
        try:
          fh=open(self.current_inbox_file,'rb')
          fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
          return True
        except Exception as my_ex:
         msg="{} is locked. trying next..".format(self.current_inbox_file)
         self.print_to_log(my_ex,msg)
    return False  #no file to read


  def get_first_outbox_file(self):
    self.current_outbox_file=''
    outbox_files=os.listdir(self.outbox_data)
    for each_file in outbox_files:
      if(os.path.isfile(self.outbox_data+each_file)):
        self.current_outbox_file=self.outbox_data+each_file
        self.print_to_log('current outbox  file:',self.current_outbox_file)
        try:
          fh=open(self.current_outbox_file,'rb')
          fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
          return True
        except Exception as my_ex:
         msg="{} is locked. trying next..".format(self.current_outbox_file)
         self.print_to_log(my_ex,msg)
    return False  #no file to read

  def get_inbox_filename(self):
    dt=datetime.datetime.now()
    return inbox_data+dt.strftime("%Y-%m-%d-%H-%M-%S-%f")

  def get_outbox_filename(self):
    dt=datetime.datetime.now()
    return self.outbox_data+dt.strftime("%Y-%m-%d-%H-%M-%S-%f")


  def archive_outbox_file(self):
    shutil.move(self.current_outbox_file, self.outbox_arch)
    #pass #useful during debugging

  def archive_inbox_file(self):
    shutil.move(self.current_inbox_file, self.inbox.arch)
