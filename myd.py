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

