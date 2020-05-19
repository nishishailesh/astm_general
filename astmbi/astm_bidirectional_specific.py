#!/usr/bin/python3
import astm_bidirectional_specific_conf as confs
import astm_bidirectional_general as astmg
class astms(astmg.astmg):

  ###################################
  #override this function in subclass
  ###################################
  def manage_read(self,data):
    self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
    self.error_set=self.read_set.union(self.write_set)    #update error set
    if(data==b'\x05'):
      self.write_msg=b'\x06'  
    if(data==b'\x0a'):
      self.write_msg=b'\x06'
  
  
  ###################################
  #override this function in subclass
  ###################################
  def initiate_write(self):
    self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
    self.error_set=self.read_set.union(self.write_set)    #update error set
    self.write_msg=b'REAL initiate_write() override me. send apple, pineapple \n' #set message
          
         
#Main Code###############################
#use this to device your own script
if __name__=='__main__':
  #print('__name__ is ',__name__,',so running code')
  while True:
    m=astms()
    m.astmg_loop()
    #break; #useful during debugging  
    
