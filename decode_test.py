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
for i in range (0,4):
    data, server = client_socket.recvfrom(9000)

    seq_no = struct.unpack_from('>Q',data,offset=0)
    print (seq_no)

    spec_val        = struct.unpack_from('>2048I',data,offset=8)
    full_spec.append(spec_val)

specA = full_spec[0] + full_spec[1] + full_spec[2] + full_spec[3]
print (specA[0:100])
plt.plot(specA)
plt.show()

