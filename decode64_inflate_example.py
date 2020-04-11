#!/usr/bin/python3
#import base64, gzip, sys
import zlib
import base64
import sys
import struct

def decode_base64_and_inflate( b64string ):
    decoded_data = base64.b64decode( b64string )
    return zlib.decompress( decoded_data , -15)

def deflate_and_base64_encode( string_val ):
    zlibbed_str = zlib.compress( string_val )
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode( compressed_string )

#x=open("start","rb")
#x=open("pla","rb")
x=open("mm","rb")

encoded_data=x.read(30000)
#decoded_data = base64.b64decode(encoded_data)
final=decode_base64_and_inflate(encoded_data)
x.close()
#y=open("start.base.deflate","wb")
#y.write(final)
#y.close()

length=len(final)
#print(length)
#print(final)
count=0
while count<length:
    x=bytes(final[count:count+4])
    print(struct.unpack('f',x))
    count=count+4

'''
See difference between str and byte-str

root@debian:~# python3
Python 3.8.2 (default, Apr  1 2020, 15:52:55) 
[GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> x='abcde'
>>> print(x[0])
a
>>> print(x[1])
b
>>> y=b'abcde'
>>> print(y[0])
97
>>> print(y[1])
98
>>> subx=x[0]+x[1]
>>> print(subx)
ab
>>> suby=y[0]+y[1]
>>> print(suby)
195
>>> suby=bytes(x[0])
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: string argument without an encoding
>>> suby=bytes(y[0])
>>> print(suby)
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
>>> suby=bytes(y[0:1])
>>> print(suby)
b'a'
>>> suby=bytes(y[0:2])
>>> print(suby)
b'ab'
>>> 
'''
