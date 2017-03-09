import re
import numpy
import time
import usbtmc

debug = 1

class Instrument:
    def __init__(self,regexp):
        self.handle = self.find(regexp)

    def ask(self,command):
        if (debug): print "Instrument.ask('%s')" % (command)
        return (self.handle.ask(command))

    def write(self,command):
        if (debug): print "Instrument.write('%s')" % (command)
        self.handle.write (command)
        time.sleep(0.01)
        return

    def read(self):
        data = self.handle.read_raw (9000)
        if (debug): print "Instrument.read() read %d bytes" % (len(data))
        return data

    def find(self,idProduct):
        deviceList = usbtmc.list_devices()
        while 0:
            device = deviceList.next()
            if idProduct == device.idProduct:
                return usbtmc.Instrument(device)
                
        if (debug): print "deviceList = ", deviceList
        deviceCount = len(deviceList)
        if (deviceCount == 0):
            print "There are no USBTMC devices attached or there is a driver problem"
            raise
        for device in deviceList:
            if idProduct == device.idProduct:
                return usbtmc.Instrument(device)
            continue
            try:
                if (debug): print "trying ", device
                handle = usbtmc.Instrument(device)
                reply = handle.ask("*IDN?")
                if (debug): print "Reply = ", reply
                if (pe.match(reply)):
                    if (debug): print "Found match"
                    return handle
                if (debug): print reply, " doesn't match ", regexp
            except OSError:
                if (debug): print "DEBUG: Unable to open ", device
        raise
        
class Generator(Instrument):
    def __init__(self):
        Instrument.__init__(self,0x0400)
        #Instrument.__init__(self,"[^,]*,DG1022U,.*")

    def sine(self,channel=1,frequency=1000,amplitude=1,offset=0):
        command = "APPL:SIN"
        if (channel > 1): command = command + ":CH2"
        command = command + " %f,%f,%f" % (frequency,amplitude,offset)
        self.write(command)

    def square(self,channel=1,frequency=1000,amplitude=1,offset=0):
        command = "APPL:SQU"
        if (channel > 1): command = command + ":CH2"
        command = command + " %f,%f,%f" % (frequency,amplitude,offset)
        self.write(command)

    def ramp(self,channel=1,frequency=1000,amplitude=1,offset=0):
        command = "APPL:RAMP"
        if (channel > 1): command = command + ":CH2"
        command = command + " %f,%f,%f" % (frequency,amplitude,offset)
        self.write(command)

    def local(self):
        self.write("SYST:LOC")

class Scope(Instrument):
    def __init__(self):
        Instrument.__init__(self,0x0588)
        #Instrument.__init__(self,"[^,]*,DS1102E,.*")

    def getTimebase(self):
        return float(self.ask(":TIM:SCAL?"))
        
    def setTimebase(self,secondsPerDiv):
        command = ":TIM:SCAL %11.9f" % (secondsPerDiv)
        self.write(command)
        return self.getTimebase()

    def getVerticalGain(self,channel):
        command = ":CHAN%d:SCAL?" % (channel)
        self.write(command)
        return float(self.read())
        
    def setVerticalGain(self,channel,voltsPerDiv):
        command = ":CHAN%d:SCAL %11.9f" % (channel,voltsPerDiv)
        self.write(command)
        return self.getVerticalGain(channel)

    def getVerticalOffset(self,channel):
        command = ":CHAN%d:OFFS?" % (channel)
        self.write(command)
        return float(self.read())
        
    def setVerticalOffset(self,channel,volts):
        command = ":CHAN%d:OFFS %11.9f" % (channel,volts)
        self.write(command)
        return self.getVerticalOffset(channel)

    def getSamples(self,channel):
        command = ":WAV:DATA? CHAN%d" % (channel)
        self.write(command)
        data = self.read()
        return numpy.frombuffer(data, 'B')[10:]

    def local(self):
        self.write(":KEY:FORCE")
        
