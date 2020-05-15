#!/usr/bin/python3

#With Explanation

#Previous Queue is now queue in debian (small q)
import select, socket, sys, queue, time

#socket.AF_INET6 for ipv6
#socket.SOCK_STREAM for TCP (SOCK_DGRAM fro UDP)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#to prevent following  error when program break and restarted immediately
#OSError: [Errno 98] Address already in use
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#not-blocking for recv(), will not wait, and can do something for a while
server.setblocking(0)

#bind to an ip and port and start listening
server.bind(('', 2222))

#just make socket 'accepting' mode for a connection
server.listen(5)

inputs = [server]
outputs = []
exceptions=[]
#Need explanation
message_queues = {}

readable, writable, exceptional = select.select(inputs, outputs, exceptions)
print (readable, writable, exceptional)
