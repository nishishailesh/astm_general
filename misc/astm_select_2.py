#!/usr/bin/python3


def print_fd(caption,list_of_sockets):
  print(caption)
  for s in list_of_sockets:
    if s != None:
      print(s.fileno())
    
#With Explanation

#Previous Queue is now queue in debian (small q)
import select, socket, sys, queue, time

#socket.AF_INET6 for ipv6
#socket.SOCK_STREAM for TCP (SOCK_DGRAM fro UDP)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#to prevent following  error when program break and restarted immediately
#OSError: [Errno 98] Address already in use
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE, 1)
   
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
#not-blocking for recv(), will not wait, and can do something for a while
server.setblocking(0)

#bind to an ip and port and start listening
server.bind(('0.0.0.0', 2222))

#just make socket 'accepting' mode for a connection
server.listen(5)

#server and connection are both sockets
#We need to maintain a list which needs to be monitored
#listening socket CAN receives request for connection so input list have it
#other sockets are added in the list after calling accept()
inputs = [server]
outputs = []
errors=[]

#Need explanation
#{} means it is a set, no duplicate, not ordered (not tuple,not list,not dictionary)
message_queues = {}


#inputs is not empty, so, enter the loop
#for any reason, server-input is to be closed, while loop will exit
while inputs:
  #select blocks untill there is activity in one of the fd passed to it
  print('Just before select()')

  print('monitoring....')
  print_fd('inputs:',inputs);
  print_fd('outputs:',outputs);
  print_fd('errors:',errors);
  
  readable, writable, exceptional = select.select(inputs, outputs, errors)
  
  #if server-socket receive any request, it is readable
  print('Just exited select()')
  
  #php foreach-as-key-value type of loop

  #print('Monitoring:\nInputs{}\nOutputs{}\n'.format(inputs,outputs))
  
  print('Actions occured in....')
  print_fd('readable:',readable);
  print_fd('writable:',writable);
  print_fd('exceptional:',exceptional);
  #print('Actions occured in:\nreadable{}\nwritable{}\nexceptional{}\n'.format(inputs,outputs,exceptional))
  
  for s in readable:
    if s is server:
      connection, client_address = s.accept()
      connection.setblocking(0)
      
      inputs.append(connection)
      outputs.append(connection)
      errors.append(connection)
      
      message_queues[connection] = queue.Queue()
      #print('message_queues:',message_queues)
      print('New Connection made######....')
      print('Now monitoring....')
      print_fd('inputs:',inputs);
      print_fd('outputs:',outputs);
      print_fd('errors:',errors);

    else:
      data = s.recv(1024)

      if data:
        print('Received {}\nFrom:fd={}:'.format(data,s.fileno()))        #put data 
        message_queues[s].put(data)
        #print('message_queues:',message_queues)
       
        if s not in outputs:
          outputs.append(s)
      else:
        #select says that it is readable and nothing EOF is obtained, so client have closed
        if s in outputs:
          outputs.remove(s)
        if s in errors:
          errors.remove(s)
        inputs.remove(s)
        s.close()
        del message_queues[s]

  
  for s in writable:
    try:
      next_msg = message_queues[s].get_nowait()
      print("Writable",next_msg)
    except queue.Empty:
      outputs.remove(s)
    else:
      s.send(next_msg)

  for s in exceptional:
    inputs.remove(s)
    if s in outputs:
      outputs.remove(s)
    s.close()
    del message_queues[s]
