from pyvisa.constants import StopBits, Parity
import re

class lakeshore350(object):
    
    def __init__(self, rm, channel):
        super(lakeshore350,self).__init__()
        self.inst = rm.open_resource('COM'+str(channel),
                                      baud_rate=57600,
                                      data_bits=7,
                                      parity=Parity.odd,
                                      stop_bits=StopBits.one
                                      )

        
    
    def __del__(self):
        self.inst.close()
    
    def close(self):
        self.inst.close()
    
        
    def getTempN(self,N):
        """
        Parameters:
            str N: channel (A,B,C,D) to get temperature from in kelvin

        Returns:
            float Temp : temperature of channel N in kelvin
        
        desc:
            from page 150 of lakeshore manual
        """

        if N not in "ABCD":
            raise Exception()
        Temp = self.inst.query("KRDG? "+ N )
        
        Temp.replace("\n","")
        Temp.replace("\r","")
        Temp = float(Temp)
        
        return Temp
    
    def getTempAll(self):
        """
        Gets the Temperature Reading in Kelvin for all channels

        Returns
        -------
        A tuple of all the read temperatures

        """
        String_Temps=self.inst.query("KRDG? 0")
        if String_Temps[-2:] == r"\n" or String_Temps[-2:] == r"\r":
            String_Temps = String_Temps[:-2]
        list_Temps=re.split(",",String_Temps)
        return(tuple(float(i) for i in list_Temps))
    
    def getSensN(self,N):
        """
        Parameters:
            str N: channel (A,B,C,D) to get Sensor Reading in Ohms

        Returns:
            float Temp : Sensor reading of channel N in Ohms
        
        desc:
            from page 150 of lakeshore manual
        """

        if N not in "ABCD":
            raise Exception()
        Temp = self.inst.query("SRDG? "+ N )
        
        Temp.replace("\n","")
        Temp.replace("\r","")
        Temp = float(Temp)
        
        return Temp
    
    def getSensAll(self):
        """
        Gets the Sensor Reading in ohms for all channels

        Returns
        -------
        A tuple of all the read resistances

        """
        String_Temps=self.inst.query("SRDG? 0")
        if String_Temps[-2:] == r"\n" or String_Temps[-2:] == r"\r":
            String_Temps = String_Temps[:-2]
        list_Temps=re.split(",",String_Temps)
        return(tuple(float(i) for i in list_Temps))
    
    def getTempSetpointN(self,N):
        """
        Parameters:
            str N: loop (1,2,3,4) to get temperature setpoint

        Returns:
            float Temp: Setpoint of loop N. In whatever units its using at the time. 
        
        desc:
            from page 156 of lakeshore manual
        """

        if N not in "ABCD":
            raise Exception()
        Temp = self.inst.query("SETP? "+ N )
        Temp = Temp.replace("\n","")
        Temp = Temp.replace("\r","")

        Temp = float(Temp)
        
        return Temp
    
    def setTempSetpointN(self,N,Temp):
        """
        Parameters:
            int N: Loop to set the setpoint to. NOTE; DOES NOT CHECK IF ITS KELVIN OR NOT.
        
        desc:
            from page 156 of lakeshore manual
        """
        self.inst.write("SETP "+ str( int(N) ) + "," + str(round(Temp,5)) )
        
    def getOutputMode(self,N):
        """

        Parameters:
            int N: output loop to get status
        Returns:
            int Mode: mode of channel:
                0 = off
                1 = closed loop PID
                2 = Zone
                3 = Open Loop
                4 = Monitor Out
                5 = Warmup Supply
            int Input: source of intput:
                0 = None
                1 = A
                2 = B
                3 = C
                4 = D
            int Powerup: output enable after power cycle:
                0 = powerup enable off
                1 = powerup enable on
        
        desc:
            from page 153 of lakeshore manual
        """
        
        Vals = self.inst.query("OUTMODE? "+ str( int(N) ) )
        Vals = Vals.replace("\n","")
        Vals = Vals.replace("\r","")
        
        Vals = Vals.split(",")

        Mode = int(Vals[0])
        Input = int(Vals[1])
        Powerup = int(Vals[2])
        
        return Mode,Input,Powerup
    
    def setOutputMode(self,N,Mode,Input,Powerup):
        """

        Parameters:
            int N: output channel to get status
            int Mode: mode of channel:
                0 = off
                1 = closed loop PID
                2 = Zone
                3 = Open Loop
                4 = Monitor Out
                5 = Warmup Supply
            int Input: source of intput:
                0 = None
                1 = A
                2 = B
                3 = C
                4 = D
            int Powerup: output enable after power cycle:
                0 = powerup enable off
                1 = powerup enable on
        
        desc:
            from page 153 of lakeshore manual
        """
        

        self.inst.write("OUTMODE {0:0.0f},{1:0.0f},{2:0.0f},{3:0.0f}".format(N,Mode,Input,Powerup))
        
    def allOff(self):
        """
        Parameters:
            None
        desc:
            Uses getOutput mode to get all parameters of all channels then sets the output mode to 
            0, turning all heaters off.
        """
        for N in range (0,1):
            Mode,Input,Powerup=self.getOutputMode(N)
            self.setOutputMode(N, 0, Input, Powerup)
            

