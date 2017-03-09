# -*- coding: utf-8 -*-
"""
Created on Thu Mar 09 12:33:21 2017

@author: aspiel
"""

import serial.tools.list_ports

def serial_ports():
    ports = list(serial.tools.list_ports.comports())
    for port_no,description, address in ports:
        return port_no
        
serial_ports()