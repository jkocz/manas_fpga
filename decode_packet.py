#!/usr/bin/env python

import time
import socket
import struct
import numpy as np
import matplotlib.pyplot as plt

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_IP = "192.168.11.4"
UDP_PORT = 4000
client_socket.bind((UDP_IP,UDP_PORT))


full_spec= []
packet_search = 0
while packet_search == 0:
    data, server = client_socket.recvfrom(9000)
    seq_no, = struct.unpack_from('>Q',data,offset=0)
    #print (type(seq_no))
    if seq_no % 8 == 0:
           print (seq_no)
           packet_search =1
           spec_val = struct.unpack_from('>8192b',data,offset=8)
           full_spec.append(spec_val)
           for i in range (0,7):
               data, server = client_socket.recvfrom(9000)
               seq_no = struct.unpack_from('>Q',data,offset=0)
               spec_val = struct.unpack_from('>8192b',data,offset=8)
               full_spec.append(spec_val)

spec1 = [x**2 for x in full_spec[0]] 
spec2 = [x**2 for x in full_spec[1]] 
spec3 = [x**2 for x in full_spec[2]] 
spec4 = [x**2 for x in full_spec[3]] 
spec5 = [x**2 for x in full_spec[4]] 
spec6 = [x**2 for x in full_spec[5]] 
spec7 = [x**2 for x in full_spec[6]] 
spec8 = [x**2 for x in full_spec[7]] 

z1 = zip(spec1[::2],spec1[1::2])
s1 = [a+b for a,b in z1]
z1 = zip(spec2[::2],spec2[1::2])
s2 = [a+b for a,b in z1]
z1 = zip(spec3[::2],spec3[1::2])
s3 = [a+b for a,b in z1]
z1 = zip(spec4[::2],spec4[1::2])
s4 = [a+b for a,b in z1]
z1 = zip(spec5[::2],spec5[1::2])
s5 = [a+b for a,b in z1]
z1 = zip(spec6[::2],spec6[1::2])
s6 = [a+b for a,b in z1]
z1 = zip(spec7[::2],spec7[1::2])
s7 = [a+b for a,b in z1]
z1 = zip(spec8[::2],spec8[1::2])
s8 = [a+b for a,b in z1]

specA = s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8
plt.plot(specA)
plt.show()

