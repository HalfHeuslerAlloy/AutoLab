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

        self.inst.write_termination = self.inst.LF
        self.inst.read_termination = self.inst.LF

        ID_Check=self.inst.query("*IDN?")
        list_ID=re.split(",",ID_Check)
        if re.search("MODEL350",list_ID[1]) == None:
            #check that the IDN comes back with the expected IDN respense
            self.inst.close()
            raise Exception("Address {} is not a Lakeshore 350!".format(str(channel))) 
    
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
        
        

        Temp=re.sub(r"\n","",Temp)
        Temp=re.sub(r"\r","",Temp)#.replace doesnt work!!!
        
        return float(Temp)
    
    def getTempAll(self):
        """
        Gets the Temperature Reading in Kelvin for all channels
        CURRENTLY BROKEN?

        Returns
        -------
        A tuple of all the read temperatures

        """
        String_Temps=self.inst.query("KRDG? 0")
        print(String_Temps)
        String_Temps.replace("\n","")
        String_Temps.replace("\r","")
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
        
        Temp=re.sub(r"\n","",Temp)
        Temp=re.sub(r"\r","",Temp)#.replace doesnt work!!!

        
        return float(Temp)
    
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
            
    def setRange(self,N,PRange):
        """
        Sets the Heater Range for a given output. Pg 154 in Manual

        Parameters
        ----------
        N : Int-castable
            Heater Channel to configure. int from 1-4
        PRange : Int
            Power Range to use. If channel 1 or 2,
            0=Off
            1=Range 1
            2=Range 2
            3=Range 3
            4=Range 4
            5=Range 5
            
            elif channel 3 or 4
            0=Off
            1=On

        """
        if int(N) in range (1,5):
            if int(N)==1 or int(N)==2:
                if int(PRange) in range (0,6):
                    self.inst.write("RANGE {0},{1}".format(int(N),int(PRange)))
                else:
                    raise ValueError("Invalid Power Range for channel {}".format(N))
            elif int(N)==3 or int(N)==4:
                if int(PRange) in range (0,2):
                    self.inst.write("RANGE {0},{1}".format(int(N),int(PRange)))
                else:
                    raise ValueError("Invalid Power Range for channel {}".format(N))
            else:
                raise Exception("HOW DID YOU GET HERE? Heater Range config. Channel input {}, Range Input {}".format(N,PRange))
            
        else:
            raise ValueError("Invalid Heater Channel to Config")
            
    def getRange(self,N):
        """
        Gets the current heater range for a given output

        Parameters
        ----------
        N : int, 1-4. Which chanel you're polling
            DESCRIPTION.

        Returns
        -------
        Int from 0-5. As PRange in setRange

        """        
        if int(N) in range(1,5):
            Vals = self.inst.query("RANGE? "+ str( int(N) ) )
            Vals = Vals.replace("\n","")
            Vals = Vals.replace("\r","")
            return(int(Vals[0]))
        else:
            raise ValueError("Invalid Heater Channel to Get Range")
            return False
            
    def setPID(self,N,P,I,D):
        """
        Sets the PID Parameters for the Lakeshore 350.
        P=Gain. Applied as a scaling factor to the proportional difference and
        the other PID parameters. Higher=More agressive
        I=The integral time constant in 1000/I seconds. Higher=More Agressive
        D=The derivative time constant as a PERCENTAGE OF 1/4th OF I. Higher=More Agressive

        Parameters
        ----------
        N : Int, 1-4
            Channel to Configure
        P : Float
            P-Value, 0.1 to 1000
        I : Float
            I-Value, 0.1 to 1000
        D : Float
            D-Value, 0 to 200

        """
        if int(N) in range(1,5):
            if 0.1<= float(P) <= 1000 and 0.1<= float(I) <= 1000 and 0 <= float(D) <=200:
                self.inst.write("PID {0},{1},{2},{3}".format(int(N),float(P),float(I),float(D)))
            else:
                raise Exception("Invalid PID values for Input {0}. P={1}, I={2}, D={3}".format(int(N),float(P),float(I),float(D)))
                
        else:
            raise ValueError("Invalid Heater Channel to Config PID")
            
    def getPID(self,N):
        """
        Gets the PID values for a certain heater loop

        Parameters
        ----------
        N : Int 1-4
            Heater loop to query

        Returns
        -------
        P, I and D
        Limits and definitions in setPID

        """
        if int(N) in range(1,5):
            Vals=self.inst.query("PID?"+str(int(N)))
            Vals = Vals.replace("\n","")
            Vals = Vals.replace("\r","")
            
            P = float(Vals[0])
            I = float(Vals[1])
            D = float(Vals[2])
            Vals = Vals.split(",")
            return(P,I,D)
        else:
            raise ValueError("Invalid Heater Channel to query PID")
            return False
        
    def setRampRate(self,N,toggle,Rate):
        """
        Sets the Ramp Rate for the setpoint. Can be between 0.001 and 100 K/min
        NB: This is applied to a HEATER output, not a sensor input.

        Parameters
        ----------
        N : Int
            Heater Loop to configure
        toggle : int
            0=Off
            1=On
        Rate : Float
            Ramp rate in K/min. Max 100 K/min

        """
        if int(N) in range(1,5):
            if int(toggle) in (0,1):
                if float(Rate) <=100:
                    self.inst.write("RAMP {0},{1},{2}".format(int(N),int(toggle),float(Rate)))
                else:
                    raise Exception("Ramp Rate too High! Max 100K/min")
            else:
                raise Exception("Invalid Toggle command to setRampRate, must be either 0 or 1")
        
        else:
            raise ValueError("Invalid Heater Channel to Set Ramp rate")

    def getRampRate(self,N):
        """
        Gets Whether the ramp is active and the ramp rate for a given control loop

        Parameters
        ----------
        N : Int 1-4
            Heater Loop to Poll

        Returns
        -------
        toggle : int
            0=Off
            1=On
        Rate : Float
            Ramp rate in K/min. Max 100 K/min

        """
        if int(N) in range(1,5):
            Vals=self.inst.query("RAMP?"+str(int(N)))
            Vals = Vals.replace("\n","")
            Vals = Vals.replace("\r","")
            Vals = Vals.split(",")
            toggle=int(Vals[0])
            Rate=float(Vals[1])
            return(toggle,Rate)
        else:
            raise ValueError("Invalid Heater Channel to Get Ramp rate")
            
    def rampStatus(self,N):
        """
        Gets the Ramp Status of Control loop N

        Parameters
        ----------
        N : Int 1-4
            Heater Loop to Poll

        Returns
        -------
        isRamping: Bool
            True if Ramping, False if not currently ramping

        """
        if int(N) in range(1,5):
            Vals=self.inst.query("RAMPST?"+str(int(N)))
            Vals = Vals.replace("\n","")
            Vals = Vals.replace("\r","")

            if int(Vals[0])==0:
                return(False)
            elif int(Vals[1])==1:
                return(True)
            else:
                raise Exception("Ramp Status returned something that wasnt 0 or 1!")
        else:
            raise ValueError("Invalid Heater Channel to Get Ramp status")
                
    
    def ManOut(self,N,power):
        """
        Sets the Manual Output power for input N

        Parameters
        ----------
        N : Int 1-4
            Heater Loop to Poll
        power : Float
            % Power to apply of currently selected range


        """
        if int(N) in range(1,5):
            if 0<= float(power) <= 100:
                self.inst.write("MOUT {0},{1}".format(int(N),float(power)))
            else:
                self.inst.write("MOUT {},0".format(int(N)))
                raise Exception("Invalid Mout Power Given, set MOUT to 0 as a precaution")
        else:
            raise ValueError("Invalid Heater Channel to Set Manual Output")
            
    def readMout(self,N):
        """
        Queries the current manual heater power

        N : Int 1-4
            Heater Loop to Poll

        Returns
        -------
        power : Float
            % Power to apply of currently selected range

        """
        if int(N) in range(1,5):
            Vals=self.inst.query("MOUT?"+str(int(N)))
            Vals = Vals.replace("\n","")
            Vals = Vals.replace("\r","")
            return(float(Vals))
        else:
            raise ValueError("Invalid Heater Channel to QueryManual Output")
            return False
            