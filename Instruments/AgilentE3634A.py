from Instruments.Instrument_class import Instrument

class AgilentE3634A(Instrument):
    
    def __init__(self, rm, channel):
        super().__init__(rm, channel, GPIB=True)
    
    def __del__(self):
        self.VI.close()
        
    def OutputOn(self):
        self.Write("OUTPut ON")
        
    def OutputOff(self):
        self.Write("OUTPut OFF")
    
    def IsOutputOn(self):
        
        mess = self.Query("OUTPut?")
        
        if "1" in mess:
            return True
        else:
            return False
    
    def SetCurrent(self, A):
        """Set the output current in mA
        """
        self.Write("CURR " + str(A))
    
    def GetCurrent(self):
        """Set the output current in mA
        """
        mess = self.Query("MEASure:CURRent?")
        mA = float(mess.replace("\n",""))
        return mA
    
    def SetVoltage(self, V):
        """Set the output Voltage in V
        """
        self.Write("VOLT " + str(V))
    
    def GetVoltage(self):
        """Gets the current output voltage (V)
        """
        mess = self.Query("MEASure:VOLTage?")
        mess.replace("\n","")
        V = float(mess)
        return V
    
    