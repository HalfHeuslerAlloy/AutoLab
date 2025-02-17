from Instruments.Instrument_class import Instrument

class Keithley2400(Instrument):
    __channel = "15" #'+self.__channel+'
    __initOn = True
    
    def __init__(self, rm, channel):
        super().__init__(rm, channel)
    
        
    def outputOn(self):
        self.Write(":OUTP ON")
        
    def outputOff(self):
        self.Write(":OUTP OFF")
        
    def reset(self):
        self.Write("*RST")
        
    def setV(self,voltage):
        voltage=str(voltage)
        self.Write(":SOUR:VOLT " + voltage)
        
    def getV(self):
        voltage = self.Query(":MEAS:VOLT:DC?")
        voltage = voltage.split(",")
        return float(voltage[0])
    
    def readAll(self):
        #Query keithley for readings
        #should return comma delimter str of data
        #Voltage, Current, Resistance, Time, Status
        values = self.Query(":READ?")
        #split and float in 
        values = [float(i) for i in values.split(",")]
        return values
        
    def autoZero(self,isOn):
        if isOn:
            self.Write(":SYST:AZER ON")
        elif isOn != True:
            self.Write(":SYST:AZER OFF")
    
    def outputMode(self,mode):
        #voltage for volts and current for current output
        self.Write(":SOUR:FUNC: "+mode)
        
    def setIRange(self,iRange):
        self.Write(":SOUR:CURR:RANGE "+iRange)
        
    def setVoltRange(self,vRange):
        self.Write(":SOUR:VOLT:RANGE "+vRange)        
        
    def sense(self,function):
        # CURRent , VOLTage or RESistance
        self.Write(":SENS:FUNC "+function)        

    def setVcomp(self,compliance):
        self.Write(":SENS:VOLT:PROT"+compliance)        

    def setIcomp(self,compliance):
        self.Write(":SENS:CURR:PROT"+compliance)

    def senseVrange(self,rge):
        self.Write(":SENS:VOLT:RANG"+rge)

    def senseIrange(self,rge):
        self.Write(":SENS:CURR:RANG"+rge)
        
    def setVandMeasI(self,volts):
        volts=str(volts)
        self.Write(":SOUR:FUNC VOLT")
        self.Write(":SENS:FUNC 'CURR:DC'")
        self.Write(":SOUR:VOLT " + volts)
        curr = self.Query(":MEAS:CURR?")
        curr = curr.split(",")
        return float(curr[1])
        
    def startVBuffer(self,buffSize):
        self.Write("*RST")
        self.Write(":TRAC:CLE")
        self.Write(":TRAC:FEED SENS")
        self.Write(":TRAC:POIN "+buffSize)
        self.Write(":TRAC:FEED:CONT NEXT")
