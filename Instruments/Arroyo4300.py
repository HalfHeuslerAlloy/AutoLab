from Instruments.Instrument_class import Instrument

class Arroyo4300(Instrument):
    
    def __init__(self, rm, channel):
        super().__init__(rm, channel, GPIB=False, Baud_Rate=38400)

        self.Write("TERM 0\n")
    
    def __del__(self):
        self.VI.close()
        
    def OutputOn(self):
        self.Write("LAS:OUT 1\n")
        
    def OutputOff(self):
        self.Write("LAS:OUT 0\n")
    
    def IsOutputOn(self):
        mess = self.Query("LAS:OUT?\n")
        
        if "1" in mess:
            return True
        else:
            return False
    
    def SetCurrent(self, mA):
        """Set the output current in mA
        """
        self.Write("LAS:LDI " + str(mA)+"\n")
    
    def GetCurrent(self):
        """Set the output current in mA
        """
        mess = self.Query("LAS:LDI?\n")
        mA = float(mess.replace("\n",""))
        return mA
    
    def GetVoltage(self):
        """Gets the current output voltage (V)
        """
        mess = self.Query("LAS:LDV?"+"\n")
        mess.replace("\n","")
        V = float(mess)
        return V
    
    def SetFreq(self, Hz):
        """Set the frequency in pulse mode, keeps pulse width constant, changes duty cycle
        """
        self.Write("LAS:F "+str(Hz)+"\n")
    
    def GetFreq(self):
        """Get the frequency in pulse mode
        """
        mess = self.Query("LAS:F?\n")
        mess = mess.replace("\n","")
        Hz = float(mess)
        return Hz
        
    def SetPulseWidth_ConstF(self,ms):
        """Set the pulse width (ms) but keep frequency constant, changes duty cycle
        """
        self.Write("LAS:PWF "+str(ms)+"\n")
        
    def SetPulseWidth_ConstP(self,ms):
        """Set the pulse width (ms) but keep duty cycle constant, change the frequency
        """
        self.Write("LAS:PWF "+str(ms)+"\n")
        
    def GetPulseWidth(self):
        """Gets the current pulse width (ms)
        """
        mess = self.Query("LAS:PW?"+"\n")
        mess.replace("\n","")
        ms = float(mess)
        return ms
    
    def GetDutyCycle(self):
        """Get the current Duty Cycle in %
        """
        mess  = self.Query("LAS:DC?\n")
        mess.replace("\n","")
        perc = float(mess)
        return perc
    
    