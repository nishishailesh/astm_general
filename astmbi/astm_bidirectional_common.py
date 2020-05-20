#!/usr/bin/python3
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
    pass
    
  def set_inbox(self,inbox):
    self.inbox=inbox
  def set_outbox(self,outbox):  
    self.outbox=outbox
    
  def get_first_file(self):
    inbox_files=os.listdir(self.inbox)
    for each_file in inbox_files:
      if(os.path.isfile(self.inbox+each_file)):
        self.current_file=each_file
        msg='File in queue is: '+self.current_file
        logging.debug(msg)
        try:
          fh=open(self.inbox+self.current_file,'rb')
          fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
          return True
        except Exception as my_ex:
         logging.debug(my_ex)
         msg="{} is locked. trying next..".format(self.current_file)
         logging.debug(msg)
    return False  #no file to read
    
  def get_filename():
    dt=datetime.datetime.now()
    return output_folder+dt.strftime("%Y-%m-%d-%H-%M-%S-%f")    
