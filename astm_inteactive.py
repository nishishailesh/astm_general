#!/usr/bin/python3
import astm_interactive_conf as conf
import time, logging, socket, select


class astmi(object):
  read_msg=b''
  write_msg=b''

  read_set=set()
  write_set=set()
  error_set=set()
  
  readable=set()
  writable=set()
  exceptional=set()
  
  def print_to_log(self,my_object,special_message):
    self.logger.debug('Start=========')
    self.logger.debug(my_object)
    self.logger.debug(special_message)   
    self.logger.debug('End=========')

  ###################################
  #override this function in subclass
  ###################################
  def manage_read(self,data):
    self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
    self.error_set=self.read_set.union(self.write_set)    #update error set
    if(data==b'pineapple\n'):
      self.write_msg=b'Demo manage_read() override me. pinapple is yellow\n'  
    if(data==b'apple\n'):
      self.write_msg=b'Demo manage_read() override me. apple is Red\n' 
  
  def manage_write(self):      
    #Send message in response to write_set->select->writable initiated by manage_read() and initiate_write()
    self.conn[0].send(self.write_msg)                     
    self.write_set.remove(self.conn[0])                   #now no message pending, so remove it from write set
    self.error_set=self.read_set.union(self.write_set)    #update error set
  
  ###################################
  #override this function in subclass
  ###################################
  def initiate_write(self):
    self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
    self.error_set=self.read_set.union(self.write_set)    #update error set
    self.write_msg=b'Demo initiate_write() override me. send apple, pineapple \n' #set message
          
  def __init__(self):
    logging.basicConfig(filename=conf.log_filename,level=logging.DEBUG)
    self.logger = logging.getLogger('astm_interactive')
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.s.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE, 1) 
    self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
    self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
    self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)  
    self.select_timeout=conf.select_timeoutt #second  
    try:
      self.s.bind((conf.host_address,int(conf.host_port)))	#it is a tuple
    except Exception as my_exception:      
      self.print_to_log(my_exception,'bind() failed, ip/port correct??Quitting')
      quit()      
    self.s.listen(2)

    self.print_to_log(self.s,'select() is waiting..') 
    self.readable, self.writable, self.exceptional = select.select((self.s,),(self.s,),(self.s,))
    self.print_to_log(self.s,'select() detected activity')
    if(self.s in self.exceptional):
      self.print_to_log(self.s,'some error on socket s. quitting')
      quit() 
    if(self.s in self.writable):
      self.print_to_log(self.s,'Can not understand why s is writting')
      quit() 
    if(self.s in self.readable):
      self.conn = self.s.accept()
      self.print_to_log(self.s,'Connection request is read')  
      self.conn[0].setblocking(0)    
      
  def astmi_loop(self):
    #First set
    #not tuple it is unmutable
    #not list, we need uniq values in error list which is sum of read and write
    
    
    self.read_set={self.s,self.conn[0]}
    self.write_set=set()  #must be managed when send is required, otherwise use 100% CPU to check writable buffer
    self.error_set=self.read_set.union(self.write_set)
    
    while True:      
      #self.print_to_log('','before select')
      self.readable, self.writable, self.exceptional = select.select(self.read_set,self.write_set,self.error_set,self.select_timeout)
      #self.print_to_log('','after select')
      
      ###if anybody else try to connect, reject it
      if(self.s in self.exceptional):
        self.print_to_log(self.s,'some error on socket s. quitting')
        quit() 
      if(self.s in self.writable):
        self.print_to_log(self.s,'Can not understand why s is writting')
        quit() 
      if(self.s in self.readable):
        dummy_conn = self.s.accept()
        self.print_to_log(self.s,'Connection request is read, This is second connection. We do not want it. shutdown, distroy')
        dummy_conn[0].shutdown(socket.SHUT_RDWR)
        dummy_conn[0].close()
        
      ###For client do work
      if(self.conn[0] in self.exceptional):
        self.print_to_log(self.conn[0],'some error on socket conn. quitting')
        quit() 
      if(self.conn[0] in self.writable):
        #sending message (somewhere else conn[0] was added in writable and self.write_msg was given value
        self.print_to_log(self.conn[0],'conn is writable. using send')
        self.manage_write()               
      if(self.conn[0] in self.readable):
        self.print_to_log(self.conn[0],'Conn have sent some data')
        data=self.conn[0].recv(1024)
        self.print_to_log(self.conn[0],data)  
        self.manage_read(data)
          
          
        #if EOF 1)close socket 2)remove from list 3)accept new
        if(data==b''):
          self.print_to_log(self.conn[0],'Conn have closed, accepting new connection')
          
          #1) close socket
          self.conn[0].shutdown(socket.SHUT_RDWR)
          self.conn[0].close()
          
          #2)remove from read list
          
          #no if:() for read_set because, we reached here due to its present in read_set
          self.read_set.remove(self.conn[0])
          #write list with if exist
          if(self.conn[0] in self.write_set):
            self.write_set.remove(self.conn[0])
          #error list is union
          #so, no need to manage
          #finally error_set
          self.error_set=self.read_set.union(self.write_set)
          
          #3) Accept new, add to read set
          self.conn = self.s.accept()
          self.print_to_log(self.s,'New Connection request is read')  
          self.conn[0].setblocking(0)
          self.read_set.add(self.conn[0])
          self.error_set=self.read_set.union(self.write_set)
       
      #If select return due to timeout -> all three tuples are empty
      #probably there is no nagging from client
      #This is ideal time to start nagging client
        
      #print('lenghts:', len(self.readable), len(self.writable), len(self.exceptional))  
      if(len(self.readable)==0 and len(self.writable)==0 and len(self.exceptional)==0):
        self.print_to_log('readable, writable,exceptional are silent','Let me do somethin else')
        self.initiate_write()  
          
         
#Main Code###############################
#use this to device your own script
if __name__=='__main__':
  #print('__name__ is ',__name__,',so running code')
  while True:
    m=astmi()
    m.astmi_loop()
    #break; #useful during debugging  
    
