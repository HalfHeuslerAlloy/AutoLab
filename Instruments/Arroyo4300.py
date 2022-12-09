

class Arroyo4300(object):
    
    def __init__(self, rm, channel):
        super(Arroyo4300,self).__init__()
        self.inst = rm.open_resource("COM"+str(int(channel)))
        self.inst.baud_rate = 38400
        self.inst.write("TERM 0\n")
    
    def __del__(self):
        self.inst.close()
        
    def OutputOn(self):
        self.inst.write("LAS:OUT 1\n")
        
    def OutputOff(self):
        self.inst.write("LAS:OUT 0\n")
    
    def IsOutputOn(self):
        mess = self.inst.query("LAS:OUT?\n")
        
        if "1" in mess:
            return True
        else:
            return False
    
    def SetCurrent(self, mA):
        """Set the output current in mA
        """
        self.inst.write("LAS:LDI " + str(mA)+"\n")
    
    def GetCurrent(self):
        """Set the output current in mA
        """
        mess = self.inst.query("LAS:LDI?\n")
        mA = float(mess.replace("\n",""))
        return mA
    
    def GetVoltage(self):
        """Gets the current output voltage (V)
        """
        mess = self.inst.query("LAS:LDV?"+"\n")
        mess.replace("\n","")
        V = float(mess)
        return V
    
    def SetFreq(self, Hz):
        """Set the frequency in pulse mode, keeps pulse width constant, changes duty cycle
        """
        self.inst.write("LAS:F "+str(Hz)+"\n")
    
    def GetFreq(self):
        """Get the frequency in pulse mode
        """
        mess = self.inst.query("LAS:F?\n")
        mess = mess.replace("\n","")
        Hz = float(mess)
        return Hz
        
    def SetPulseWidth_ConstF(self,ms):
        """Set the pulse width (ms) but keep frequency constant, changes duty cycle
        """
        self.inst.write("LAS:PWF "+str(ms)+"\n")
        
    def SetPulseWidth_ConstP(self,ms):
        """Set the pulse width (ms) but keep duty cycle constant, change the frequency
        """
        self.inst.write("LAS:PWF "+str(ms)+"\n")
        
    def GetPulseWidth(self):
        """Gets the current pulse width (ms)
        """
        mess = self.inst.query("LAS:PW?"+"\n")
        mess.replace("\n","")
        ms = float(mess)
        return ms
    
    def GetDutyCycle(self,perc):
        """Get the current Duty Cycle in %
        """
        mess  = self.inst.query("LAS:DC?\n")
        mess.replace("\n","")
        perc = float(mess)
        return perc
    
    