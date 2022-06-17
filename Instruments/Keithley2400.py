

class Keithley2400(object):
    __channel = "15" #'+self.__channel+'
    __initOn = True
    
    def __init__(self, rm, channel):
        super(Keithley2400,self).__init__()
        self.inst = rm.open_resource('GPIB0::'+str(channel)+'::INSTR')
        #self.inst.write("*RST")
    
    def __del__(self):
        self.inst.close()
        
    def outputOn(self):
        self.inst.write(":OUTP ON")
        
    def outputOff(self):
        self.inst.write(":OUTP OFF")
        
    def reset(self):
        self.inst.write("*RST")
        
    def setV(self,voltage):
        voltage=str(voltage)
        self.inst.write(":SOUR:VOLT " + voltage)
        
    def getV(self):
        voltage = self.inst.query(":MEAS:VOLT:DC?")
        voltage = voltage.split(",")
        return float(voltage[0])
    
    def readAll(self):
        #Query keithley for readings
        #should return comma delimter str of data
        #Voltage, Current, Resistance, Time, Status
        values = self.inst.query(":READ?")
        #split and float in 
        values = [float(i) for i in values.split(",")]
        return values
        
    def autoZero(self,isOn):
        if isOn:
            self.inst.write(":SYST:AZER ON")
        elif isOn != True:
            self.inst.write(":SYST:AZER OFF")
    
    def outputMode(self,mode):
        #voltage for volts and current for current output
        self.inst.write(":SOUR:FUNC: "+mode)
        
    def setIRange(self,iRange):
        self.inst.write(":SOUR:CURR:RANGE "+iRange)
        
    def setVoltRange(self,vRange):
        self.inst.write(":SOUR:VOLT:RANGE "+vRange)        
        
    def sense(self,function):
        # CURRent , VOLTage or RESistance
        self.inst.write(":SENS:FUNC "+function)        

    def setVcomp(self,compliance):
        self.inst.write(":SENS:VOLT:PROT"+compliance)        

    def setIcomp(self,compliance):
        self.inst.write(":SENS:CURR:PROT"+compliance)

    def senseVrange(self,rge):
        self.inst.write(":SENS:VOLT:RANG"+rge)

    def senseIrange(self,rge):
        self.inst.write(":SENS:CURR:RANG"+rge)
        
    def setVandMeasI(self,volts):
        volts=str(volts)
        self.inst.write(":SOUR:FUNC VOLT")
        self.inst.write(":SENS:FUNC 'CURR:DC'")
        self.inst.write(":SOUR:VOLT " + volts)
        curr = self.inst.query(":MEAS:CURR?")
        curr = curr.split(",")
        return float(curr[1])
        
    def startVBuffer(self,buffSize):
        self.inst.write("*RST")
        self.inst.write(":TRAC:CLE")
        self.inst.write(":TRAC:FEED SENS")
        self.inst.write(":TRAC:POIN "+buffSize)
        self.inst.write(":TRAC:FEED:CONT NEXT")
