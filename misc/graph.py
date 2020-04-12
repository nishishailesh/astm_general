#!/usr/bin/python3

# importing the required module 
import matplotlib.pyplot as plt 
import io, sys


#print(dir(plt))  
# x axis values 
x = [1,2,3] 
# corresponding y axis values 
y = [2,4,1] 
  
# plotting the points  
plt.plot(x, y) 
  
# naming the x axis 
plt.xlabel('x - axis') 
# naming the y axis 
plt.ylabel('y - axis') 
  
# giving a title to my graph 
plt.title('My first graph!') 
 
f = io.BytesIO() 
plt.savefig(f, format='png')

#x=open('x.png','wb')
#f.seek(0)
#x.write(f.read())
#x.close()

f.seek(0)
data=f.read()
#print(data)
sys.stdout.buffer.write(data) #good method to write binary data
#plt.show() 
