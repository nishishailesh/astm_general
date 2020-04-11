#!/usr/bin/python3
import sys, socket
global s 
host_address='127.0.0.1'
host_port=25750


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#socket.setblocking(False)
s.bind((host_address,int(host_port)))	#it is a tuple
s.listen(1)
s.settimeout(6)
conn_tuple = s.accept()	#This waits till connected
print(conn_tuple)


conn_tuple[0].recv(1)
conn_tuple[0].send(b'\x06')
conn_tuple[0].send(b'\x26')



#while True:

  
