#!/usr/bin/python3.7
import os
import MySQLdb
import time
import logging

#Globals for configuration################
debug=0

my_host='127.0.0.1'
my_user='root'
my_pass=''
my_db='cl_general'

inbox='/root/inbox0/'
archived='/root/archived0/'

##########MYSQL##
def show_results():
  cur=con.cursor()
  cur.execute('select * from result;')
  while True:
    row = cur.fetchone()
    if row == None:
      print(row)
      break
    else:
      print(row)

def run_query(prepared_sql,data_tpl):
  #con=MySQLdb.connect('127.0.0.1','root','nishiiilu','cl_general')
  con=MySQLdb.connect(my_host,my_user,my_pass,my_db)
  if(debug==1): print(con)
  if(con==None):
     if(debug==1): print("Can't connect to database")
  else:
    pass
    #print('connected')
  cur=con.cursor()
  cur.execute(prepared_sql,data_tpl)
  con.commit()
  return cur

def get_single_row(cur):
    return cur.fetchone()

#classes#################################
class micros(object):
  #inbox='/root/inbox2/'
  #archived='/root/archived2/'
  abx={
	"\xff":(22,0,0), #"RecordType"],0,0),
	"p":(23,0,0), #"AnalyserNumber"],0,0),
	"q":(24,0,0), #"AnalysisDateTime"],0,0),
	"p":(25,0,0), #"AnalyserNumber"],0,0),
	"q":(26,0,0), #"DateTime"],0,0),
	"s":(27,0,0), #"AnalyzerSequence"],0,0),
	"t":(28,0,0), #"SamplingMode"],0,0),
	"u":(29,0,0), #"SampleIDbyAnalyser"],0,0),
	"v":(30,0,0), #"sample_id"],0,0),
	"\x80":(31,0,0), #"AnalyserMode"],0,0),
	"!":(1,5,1000), #"WBC"],0,1000),
	"2":(2,5,0), #"RBC"],0,0),
	"3":(3,5,0), #"Hemoglobin"],0,0),
	"4":(4,5,0), #"Hematocrit"],0,0),
	"5":(5,5,0), #"MCV"],0,0),
	"6":(6,5,0), #"MCH"],0,0),
	"7":(7,5,0), #"MCHC"],0,0),
	"8":(8,5,0), #"RDW"],0,0),
	"@":(9,5,1000), #"Platelet"],0,1000),
	"A":(10,5,0), #"MPV"],0,0),
	"B":(11,5,0), #"THT"],0,0),
	"C":(12,5,0), #"PWD"],0,0),
	"#":(13,5,0), #"Lymphocyte%"],0,0),
	"%":(14,5,0), #"Monocyte%"],0,0),
	"'":(15,5,0), #"Granulocyte%"],0,0),
	"\"":(16,5,0), #"LymphocyteCount"],0,0),
	"$":(17,5,0), #"MonocyteCount"],0,0),
	"&":(18,5,0), #"GranulocyteCount"],0,0),
	"X":(19,0,0), #"RDWGraph"],0,0),
	"W":(20,0,0), #"WBCWGraph"],0,0),
	"Y":(21,0,0), #"PlateletWGraph"],0,0),
	"S":(32,0,0), #"PlateletIdentifier?"],0,0),
	"_":(33,0,0), #"PlateletThresold"],0,0),
	"P":(34,0,0), #"WBCIdentifier?"],0,0),
	"]":(35,0,0), #"WBCThresold"],0,0),
	"\xfb":(36,0,0), #"AnalyserName"],0,0),
	"\xfe":(37,0,0), #"Version"],0,0),
	"\xfd":(38,0,0), #"Checksum"],0,0),
     }

  


  def __init__(self,inbox_folder,archived_folder):
    self.inbox=inbox_folder
    self.archived=archived_folder
    self.abx_result={}
    self.current_file=''    
  def get_first_file(self):
    inbox_files=os.listdir(self.inbox)
    for each_file in inbox_files:
      if(os.path.isfile(self.inbox+each_file)):
        self.current_file=each_file
        return True
    return False  #no file to read
    
  def get_abx_result(self):
    fh=open(self.inbox+self.current_file,'r')
    while True:
      data=fh.readline().rstrip('\n')
      if data=='':
        break
        
      token=data.split(' ',1)
      
      try:
        analyser_code=token[0]
      except Exception as analyser_code_error:
        logging.debug(analyser_code_error)
        continue
        
      if(analyser_code in self.abx):
        try:
          analyser_result=token[1]
        except Exception as analyser_code_error:
          logging.debug(analyser_code_error)
          continue
        
        db_code=self.abx[analyser_code][0]
        field_size=self.abx[analyser_code][1]
        multiplication_factor=self.abx[analyser_code][2]
        if(field_size>0):
          db_result=(analyser_result[:field_size])
        else:
          db_result=analyser_result

        if(multiplication_factor>0):
          try:			
            db_result=round(float(db_result)*multiplication_factor)
          except Exception as my_ex:
            logging.debug(my_ex)
            logging.debug('\033[0;31mresult of ('+analyser_code+') can not be converted to float for multiplication?\033[0m')
            continue			  
        else:
          db_result= db_result
        self.abx_result[db_code]=db_result
        
  def send_to_mysql(self):
    if(30 in self.abx_result and 26 in self.abx_result):
      if(debug==1):print('sample_id='+self.abx_result[30].rstrip(' '));
    else:
      if(debug==1):print('\033[0;31msample_id / datetime not found. not ABX? is it ARGOS?\033[0m')
      logging.debug('\033[0;31msample_id / datetime not found. not ABX? is it ARGOS?\033[0m')
      return False;

    if(self.abx_result[30].rstrip(' ').isnumeric() == False):
      if(debug==1):print('\033[0;31msample_id is not number\033[0m')
      logging.debug('\033[0;31msample_id is not number\033[0m')
      return False;

    for key in self.abx_result.keys():
      if(key in [19,20,21]):
        if(debug==1):print(key)		
        sql='insert into primary_result_blob (sample_id,examination_id,result,uniq) values (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE result=%s'
      else:
        sql='insert into primary_result (sample_id,examination_id,result,uniq) values (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE result=%s'
      data_tpl=(self.abx_result[30].rstrip(' '),key,self.abx_result[key],self.abx_result[26],self.abx_result[key])
      run_query(sql,data_tpl)
      
  def archive_file(self):
    os.rename(self.inbox+self.current_file,self.archived+self.current_file)
    if(30 in self.abx_result):
      sid='Sample_ID:'+self.abx_result[30].rstrip(' ')
    else:
      sid='Sample_ID can not be found in file but,'
    logging.debug('--- '+sid+' Data moved to '+str(self.archived+self.current_file))
    current_file='';

logging.basicConfig(filename='/root/micros.log',level=logging.DEBUG)
      
#Main Code###############################
if __name__=='__main__':
  #print('__name__ is ',__name__,',so running code')
  while True:
    m=micros(inbox,archived)
    if(debug==1): print(m.abx_result)
    if(m.get_first_file()):
      m.get_abx_result()
      m.send_to_mysql()
      m.archive_file()
    if(debug==1):print(m.abx_result)
    time.sleep(1)
  
