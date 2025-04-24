# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 10:04:37 2025

@author: csk42
Driver for the Oxford instruments 503 Temperature Controller
"""

import re
from Instruments.Instrument_Class import Instrument
import time

class Oxford_503(Instrument):
    def __init__(self,rm,address):
        """
        Initialise the OI 503

        Parameters
        ----------
        rm : pyvisa.resource manager
            the resource manager object used to connect to the instrument
        address : String or Int
            Comms address to connect to the Temperature Controller
            Int will parse as a GPIB adress, or String as an address from
            pyvisa.list_resources


        """
        super.__init__(rm,address)
        #connects to the instrument using the Instrument_class init parameters
        self.VI.write_termination=self.VI.CR
        self.VI.read_termination=self.VI.CR #read/write termination
        
        self.Write("C3") 
        #when initialising instrument, force Remote Enable.
        #if this causes issues, put into dedicated "Remote Enable" function
    
    def __chkFloat(self, s):
        """
        Trims a LF character from a string S.
        Thanks to Nic Hunter

        """
        if s[-2:] == r"\r":#\n for LineFeed, \r for carriage return
            s = s[:-2]
        return float(s)
    
    def setRemote(self,C):
        """
        Sets the Remote/Local Mode of the instrument

        Parameters
        ----------
        C : INT
            0=Local+Locked (Cannot be Comms with Except to Switch mode. Powerup default)
            1=Remote+Locked(No front Panel)
            2=Local+Unlocked
            3=Remote+Unlocked (Personal Default)

        """
        try:
            if int(C) not in range (0,4):
                raise Exception("Invalid Remote Mode Selection. Expected an Int Between 0-3, got {}".format(C))
                return
        except ValueError:
            raise Exception("Remote Mode could not be parsed as Int, check input")
            return
        self.Write("C"+str(int(C)))
        return
    
    def getTempN(self,N):
        """
        Query the Temperature in Kelvin for a given channel N

        Parameters
        ----------
        N : Int-like
            Channel 1-3 for which to query

        Returns
        -------
        The temperature for the given channel.

        """
        
        try:
            if int(N) not in range(1,4):
                raise Exception("Invalid Channel Selection, Expected an int between 1-3, got {}".format(N))
                return()
        except ValueError:
            raise Exception("Channel ID could not be cast as Int. Check inputs")
            return()
        return(self.__chkFloat(self.Query("R"+str(N))))
    
    def getTempAll(self):
        """
        Return the temperature in Kelvin for all 3 channels

        Returns
        -------
        A tuple of 3 temperatures 

        """
        One=self.__chkFloat(self.Query("R1"))
        time.sleep(0.01)#todo:Test this. Old OI kit locks up if you talk to it too fast
        Two=self.__chkFloat(self.Query("R2"))
        time.sleep(0.01)
        Three=self.__chkFloat(self.Query("R3"))
        return((One,Two,Three))
    
    def examine(self):
        """
        Examines the system Status. As pg 51 of the ITC 503 Manual

        Returns
        -------
        a Length 5 Tuple; in the order ACSHL
        A=Auto/Man Mode;
        0=Heater+Gas Open Loop
        1=Heater Zone, Gas Open Loop
        2=Heater Open Loop, Gas PID (why???)
        3= Heater+Gas PID
        
        C=Local/Remote Mode
        0=Local+Locked
        1=Remote+Locked(No front Panel)
        2=Local+Unlocked
        3=Remote+Unlocked (Personal Default)
        
        S=Sweep Status
        0=No Sweep
        2P-1=Sweeping to Sweep Step P
        2P=Holding at Step P
        
        H=Control Sensor
        1=Sensor 1
        2=Sensor 2
        3=Sensor 3
        
        L=PID Mode
        0=Static PID
        1=Zone Table Lookup
        """
        readback=self.Query("X")
        if readback[-2:]==r"\r":
            readback=readback[:-2]#trim TERM characters if present
        split_readback=re.split(r"\D",readback)#splits the incoming string along the non-numeric characters
        return(tuple(split_readback[2::]))
    #the first element will be blank, the second will be the X character, which should be 0
    
    def setOutputMode(self,Mode):
        """
        Sets the Heater/Gas Output Mode

        Parameters
        ----------
        Mode : Int in range 0-3
        0=Heater+Gas Open Loop
        1=Heater PID, Gas Open Loop (Should be the Standard)
        2=Heater Open Loop, Gas PID (why???????)
        3= Heater+Gas PID

        Returns
        -------
        None.

        """
        try:
           intMode=int(Mode)#cant do comparisons on strings
        except ValueError:
            raise Exception("Heater Mode Could Not Be Parsed as Int!")
            return
        if intMode not in range (0,4):
            raise Exception("Heater Mode Expected to be an int between 0 and 3, got {}".format(Mode))
        else:
            self.Write("A"+str(Mode))
        return
    
    def setPIDMode(self,L):
        """
        Sets whether the PID mode is Static PID or Zone.
        

        Parameters
        ----------
        L : Int
            0=Static PID
            1=Zone Table Lookup

        Returns
        -------
        None.

        """
        try:
           intL=int(L)#cant do comparisons on strings
        except ValueError:
            raise Exception("Heater PID Mode Could Not Be Parsed as Int!")
            return
        if intL not in range (0,2):
            raise Exception("Heater PID Mode Expected to be an int between 0 and 3, got {}".format(L))
        else:
            self.Write("L"+str(L))
        return
    
    def getTempSetpoint(self):
        """
        Returns the value of the current temperature setpoint

        """
        return(self.__chkFloat(self.Query("R0")))
    
    def setTempSetpoint(self,setpoint):
        """
        Sets the setpoint

        Parameters
        ----------
        setpoint : Float
            Setpoint to send.

        Returns
        -------
        None.

        """
        try:
            setpoint=float(setpoint)
        except ValueError:
            raise Exception("Expected OI503 Setpoint to be a Float, received {}".format(setpoint))
            return
        if setpoint>300:
            raise Exception("Invalid Setpoint, Value must be Less than 300 K, received {}".format(setpoint))
            return
        elif setpoint<0:
            print("Invalid Setpoint, value must be positive")
            return
        else:
            self.Write("T"+str(round(setpoint, 4)))#round to 4 DP. Assume this is as far as it goes
            return
        
    def ManOut(self,power):
        """
        Sets the heater output power in Open Loop control

        Parameters
        ----------
        power : Float
            Float between 0 and 99.9

        Returns
        -------
        None.

        """
        try:
            power=float(power)
        except ValueError:
            raise Exception("Expected Heater Power to be a Float, received {}".format(power))
            return
        
        if power==100:
            power=99.9
            #handle the case where a power of 100% is entered. You can't go over 99.9 for some reason.
        if power>99.9 or power <0:
            self.Write("O0")
            raise Exception("Invalid Power detected, Power should be between 0 and 99.9, got {}. Set power to 0 for saftey".format(power))
            return
        else:
            self.Write("O"+str(round(power,1)))
            return
        
    def getHeaterPower(self):
        """
        Returns the Heater power as a % of fullrange. Unlike the Lakeshore this works even when using PID controls

        """
        return(self.__chkFloat(self.Query("R5")))
    
    def setGasFlow(self,flow):
        """
        Sets the Needle Valve Position in Open Loop control

        Parameters
        ----------
        flow : Float
            Float between 0 and 99.9

        Returns
        -------
        None.

        """
        try:
            flow=float(flow)
        except ValueError:
            raise Exception("Expected Gas Flow to be a Float, received {}".format(flow))
            return
        
        if flow==100:
            flow=99.9
            #handle the case where a power of 100% is entered. You can't go over 99.9 for some reason.
        if flow>99.9 or flow <0:
            self.Write("G0")
            raise Exception("Invalid Gas Flow detected, Flow should be between 0 and 99.9, got {}. Set flow to 0 for saftey".format(flow))
            return
        else:
            self.Write("G"+str(round(flow,1)))
            return
        
    def setHeaterSensor(self, N):
        """
        Set the Heater Sensor Used For PID control.

        Parameters
        ----------
        N : Int
            Channel ID between 1-3

        """
        try:
            if int(N) not in range(1,4):
                raise Exception("Invalid Channel Selection, Expected an int between 1-3, got {}".format(N))
                return()
        except ValueError:
            raise Exception("Channel ID could not be cast as Int. Check inputs")
            return()
        
        self.Write("H"+str(int(N)))
        return
    
    