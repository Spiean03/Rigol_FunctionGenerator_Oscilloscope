# -*- coding: utf-8 -*-
"""
Find USB Port_no
"""

import serial.tools.list_ports

def serial_ports():
    ports = list(serial.tools.list_ports.comports())
    for port_no,description, address in ports:
        return port_no
        
serial_ports()
