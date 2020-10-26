#!/usr/bin/python3
import astm_bidirectional_conf as conf
import time, logging, socket, select


class astmg(object):
  read_msg=b''
  write_msg=b''

  read_set=set()
  write_set=set()
  error_set=set()

  readable=set()
  writable=set()
  exceptional=set()

  def list_wait(self):
    print_to_log('Listening to {} , {} , {} '.
                    format(
                            list(map(socket.socket.fileno,self.read_set)),
                            list(map(socket.socket.fileno,self.write_set)),
                            list(map(socket.socket.fileno,self.error_set))
                            ),
                      'Heard from for {} , {} , {} '.
                    format(
                            list(map(socket.socket.fileno,self.readable)),
                            list(map(socket.socket.fileno,self.writable)),
                            list(map(socket.socket.fileno,self.exceptional))
                            )
                      )
    #'Received for {} , {} , {} '.format(self.readable,self.writable,self.exceptional))
      
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
  
  ###################################
  #override this function in subclass
  ###################################
  def manage_write(self):      
    #Send message in response to write_set->select->writable initiated by manage_read() and initiate_write()
    print_to_log('Following will be sent',self.write_msg) 
    self.conn[0].send(self.write_msg)                     
    self.write_set.remove(self.conn[0])                   #now no message pending, so remove it from write set
    self.error_set=self.read_set.union(self.write_set)    #update error set

  
  ###################################
  #override this function in subclass , generally not required, unless status change needs to be monitored
  ###################################
  def initiate_write(self):
    self.write_set.add(self.conn[0])                      #Add in write set, for next select() to make it writable
    self.error_set=self.read_set.union(self.write_set)    #update error set
    self.write_msg=b'Demo initiate_write() override me. send apple, pineapple \n' #set message
          
  def __init__(self):
    #logging.basicConfig(filename=conf.log_filename,level=logging.CRITICAL)
    #logging.basicConfig(filename=conf.log_filename,level=logging.DEBUG)
    #self.logger = logging.getLogger('astm_bidirectional_general')
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.s.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE, 1) 
    self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
    self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
    self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)  
    self.select_timeout=conf.select_timeout #second  
    try:
      self.s.bind((conf.host_address,int(conf.host_port)))	#it is a tuple
    except Exception as my_exception:      
      print_to_log(my_exception,'bind() failed, ip/port correct??Quitting')
      quit()      
    self.s.listen(2)

    print_to_log(self.s,'select() is waiting..') 
    self.readable, self.writable, self.exceptional = select.select((self.s,),(self.s,),(self.s,))
    print_to_log(self.s,'select() detected activity')
    if(self.s in self.exceptional):
      print_to_log(self.s,'some error on socket s. quitting')
      quit() 
    if(self.s in self.writable):
      print_to_log(self.s,'Can not understand why s is writting')
      quit() 
    if(self.s in self.readable):
      self.conn = self.s.accept()
      print_to_log(self.s,'Connection request is read')  
      self.conn[0].setblocking(0)    
      
  def astmg_loop(self):
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
      self.list_wait()
      ###if anybody else try to connect, reject it

      if(self.s in self.exceptional):
        print_to_log(self.s,'some error on socket s. quitting')
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        break 

      if(self.s in self.writable):
        print_to_log(self.s,'Can not understand why s is writting')
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        break 

      if(self.s in self.readable):
        dummy_conn = self.s.accept()
        print_to_log(self.s,'Connection request is read, This is second connection. We do not want it. shutdown, close')
        dummy_conn[0].shutdown(socket.SHUT_RDWR)
        dummy_conn[0].close()
        
      ###For client do work
      if(self.conn[0] in self.exceptional):
        print_to_log(self.conn[0],'some error on socket conn. quitting')
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        break 

      if(self.conn[0] in self.writable):
        #sending message (somewhere else conn[0] was added in writable and self.write_msg was given value
        print_to_log(self.conn[0],'conn is writable. using manage_write()')
        self.manage_write() 
                       
      if(self.conn[0] in self.readable):
        print_to_log(self.conn[0],'Conn have sent some data. now using recv() and manage_read()')
        try:
          data=self.conn[0].recv(1024)
          print_to_log('Following is received:',data)  
          self.manage_read(data)
        except Exception as my_exception:      
          print_to_log(my_exception,'recv() failed. something sent and then connection closed') 
          self.s.shutdown(socket.SHUT_RDWR)
          self.s.close()
          '''to prevent: DEBUG:root:[Errno 110] Connection timed out recv() failed. something sent and then connection closed
          DEBUG:root:[Errno 98] Address already in use bind() failed, ip/port correct??Quitting'''
          break

        #only EOF is handled here, rest is handled in manage_read()
        #if EOF 1)close socket 2)remove from list 3)accept new
        if(data==b''):
          print_to_log(self.conn[0],'Conn have closed, accepting new connection')
          
          #1) close socket
          self.conn[0].shutdown(socket.SHUT_RDWR)
          self.conn[0].close()
          
          #2)remove from read list
          
          #no if:() for read_set because, we reached here due to its presence in read_set
          self.read_set.remove(self.conn[0])
          #write list with if exist
          if(self.conn[0] in self.write_set):
            self.write_set.remove(self.conn[0])
          #error list is union
          #so, no need to manage
          #finally error_set
          self.error_set=self.read_set.union(self.write_set)
          
          #3) Accept new, add to read set, this is blocking here. No need to go for initiate_write, because nothing to do
          self.conn = self.s.accept()
          print_to_log(self.s,'New Connection request is read')  
          self.conn[0].setblocking(0)
          self.read_set.add(self.conn[0])
          self.error_set=self.read_set.union(self.write_set)

      self.initiate_write()  

def print_to_log(object1,object2):
  logging.debug('{} {}'.format(object1,object2))
                     
#Main Code###############################
#use this to device your own script
if __name__=='__main__':
  logging.basicConfig(filename=conf.astm_log_filename,level=logging.DEBUG,format='%(asctime)s : %(message)s')  

  #print('__name__ is ',__name__,',so running code')
  while True:
    m=astmg()
    m.astmg_loop()
    #break; #useful during debugging  
    
