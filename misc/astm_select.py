#!/usr/bin/python3
import sys
import fcntl
import socket
import datetime
import select
import time

def do_send():
  pass
  

def do_receive(conn):
  byte_array=[]
  while True:
    byte=conn.recv(1)
    if(byte==b''):
      break    
    else:
      byte_array=byte_array+[chr(ord(byte))]
      
    if(byte==b'\x05'):
      byte_array=[]
      byte_array=byte_array+[chr(ord(byte))]
      conn.send(b'\x06');
      cur_file=get_filename() 
      x=open(cur_file,'w')
      fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)
    elif(byte==b'\x0a'):
      conn.send(b'\x06');
      x.write(''.join(byte_array))
      byte_array=[]
    elif(byte==b'\x04'):
      x.write(''.join(byte_array))
      x.close()   
      byte_array=[]
      break;
    
def get_socket():
  host_address='11.207.1.1'
  host_port='2576'
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE, 1)
   
  s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
  s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
  s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
    
  s.bind((host_address,int(host_port)))	#it is a tuple
  s.listen(1)
  return s

def get_connection(s):
  conn_tuple = s.accept()
  return conn_tuple[0]  


def get_filename():
  dt=datetime.datetime.now()
  return '/root/bastm.read/'+dt.strftime("%Y-%m-%d-%H-%M-%S-%f")

'''
s=get_socket()

while True:
  conn=get_connection(s)
  while True:
    do_receive(conn)
'''



# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

# Bind the socket to the port
server_address = ('11.207.1.1', 2576)
print('starting up on {}'.format(server_address))
server.bind(server_address)

# Listen for incoming connections
server.listen(5)
inputs = [ server ]
outputs = [ server ]
errors = [ server ]


while True:
  ready_to_read, ready_to_write, in_error = select.select(inputs,outputs,errors)
  print(ready_to_read, ready_to_write, in_error)
  time.sleep(2)

