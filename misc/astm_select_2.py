#!/usr/bin/python3

#With Explanation

#Previous Queue is now queue in debian (small q)
import select, socket, sys, queue, time, pprint

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
#Need explanation
message_queues = {}

pp = pprint.PrettyPrinter(indent=2)

#inputs is not empty, so, enter the loop
#for any reason, server-input is to be closed, while loop will exit
while inputs:
  #prevent anything else in this main loop except following line
  #Rest of the things in for loop
  #Otherwise lots of stdout activity will be seen, each time select is called non-blockinh-ly
  readable, writable, exceptional = select.select(inputs, outputs, inputs+outputs)
  
  #if server-socket receive any request, it is readable
  #print('Just exited select()')
  
  #php foreach-as-key-value type of loop
  for s in readable:
    print('Monitoring:')
    pp.pprint(inputs)
    pp.pprint(outputs)
    #inputs+outputs)
    print('Attn:')
    pp.pprint(readable)
    pp.pprint(writable)
    pp.pprint(exceptional)
    if s is server:
      connection, client_address = s.accept()
      connection.setblocking(0)
      inputs.append(connection)
      message_queues[connection] = queue.Queue()
      print('Now Monitoring....')
      pp.pprint(inputs)
      pp.pprint(outputs)
    else:
      data = s.recv(1024)
      print('Received:', data)
      if data:
        message_queues[s].put(data)
        if s not in outputs:
          outputs.append(s)
      else:
        if s in outputs:
          outputs.remove(s)
        inputs.remove(s)
        s.close()
        del message_queues[s]

  
  for s in writable:
    try:
      next_msg = message_queues[s].get_nowait()
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
  
