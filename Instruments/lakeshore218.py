# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 11:14:18 2023

@author: eencsk
Driver for the Lakeshore 218 temperature controller.
TODO: Impliment Curve Import from PC, Relay Configuration and In-situ logging in case of PC failiure. 
I'm probably NOT going to do that, I dont need to do that for this controller, but here you go. 
"""
import re
from pyvisa.constants import StopBits, Parity

class lakeshore218(object):
    def __init__(self, rm, Address):
        """
        Initialise the LS218 Monitor
        
        Parameters
        ---
        rm pyvisa resource manader
        Address: String or Int: Either a int (will address as COM:Address)
        or a string from pyvisa.listresources

        """

        if Address == type(" "): #If the address is not a string the slice in next line dont work!
            
            if Address[:3] == "ASRL":
                self.VI=rm.open_resource(Address,baud_rate=9600,data_bits=7,parity=Parity.odd,stop_bits=StopBits.one)
            else:
                raise Exception("Invalid Lakeshore 218 Address, Expected an Int or String Beginning ASRL, got {}".format(Address))
        else:
            try:
                self.VI=rm.open_resource('COM'+str(Address),baud_rate=9600,data_bits=7,parity=Parity.odd,stop_bits=StopBits.one)
            except ValueError:
                raise Exception("Invalid Lakeshore218 Address. Expected an Int or a string beginning ASRL, got {}".format(Address))
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF        #set up command terminators
     
    def __chkFloat(self, s):
        """
        Trims a LF character from a string S.
        Thanks to Nic Hunter

        """
        if s[-2:] == r"\n":
            s = s[:-2]
        return float(s)
    
    def close(self):
        """
        Close the instrument
        """
        self.VI.close()
        
    def Clear_Buffer(self):
        """
        Clears the status byte register and Standard Event Status Register.
        """
        self.VI.write("QCLS")
        
    def Op_Com(self):
        """
        Generates an Operation Complete event in the register
        """
        self.VI.write("QOPC")
        
    def is_Op_Com(self):
        """
        Queries the presence of an Operation Complete Event
        """
        return(self.VI.query("QOPC?"))
    
    def set_Alarm(self,channel, Enable,Unit=1,HighV=310,LowV=0,Soft_Latch=5,Hard_Latch=False):
        """
        Sets the Alarm for a given input

        Parameters
        ----------
        channel : Int
            Channel to output on. Integer between 1 and 8.
        Enable : Bool
            Whether to Enable the alarm.
        Unit : Int, optional
            Unit to set the alarm against.
            1= Kelvin
            2= Celsius
            3= Sensor Units (Resistance)
            4= Linear Data (????)
            The default is 1.
        HighV : Float, optional
            If the queried value EXCEEDS this value, Activate the alarm. The default is 310.
        LowV : Float, optional
            If the queried value IS LESS THAN this value, Activate the alarm. The default is 0.
        Soft_Latch : Float, optional
            Also known as "deadband". If the value returns within normal operating range, keep the alarm ON
            until it has gone X units past the alarm limit. The default is 5.
        Hard_Latch : Bool, optional
            Overrides Soft_Latch. If this is True, keep the alarm on, regardless of the state the system returns to.
            The default is False.

        """
        try:
            Enable=int(Enable*1)
            Hard_Latch=int(Hard_Latch*1)
        except ValueError:
            print("Invalid Boolean in set_Alarm, did NOT enable alarm")
            Enable=0
            Hard_Latch=0
        
        try:
            channel=int(channel)
            Unit=int(Unit)
        except ValueError:
            print("Invalid Channal or Unit casting. Must be able to be cast as int")
        
        if channel in range(1,9) and Unit in range(1,5):
            self.VI.write("ALARM {0}, {1}, {2}, {3}, {4}, {5}, {6}".format(channel,Enable,Unit,HighV,LowV,Soft_Latch,Hard_Latch))
        else:
            print("Invalid Channel/Unit in Alarm Settings.")
            
    def get_Alarm_settings(self,channel):
        """
        Returns the alarm settings as given in Set_alarm in the order
        Channel, Enabled?,Unit,High Value, Low Value, Deadband, Latch
        """
        try:
            channel=int(channel)
        except ValueError:
            raise Exception("Channel must be able to be cast as Int")
        
        if channel in range(1,9):
            String_settings=self.VI.query("ALARM? {}".format(channel))
            if String_settings[-2:] == r"\n":
                String_settings = String_settings[:-2]
            list_settings=re.split(",",String_settings)
            return(tuple(float(i) for i in list_settings))
        else:
            raise Exception("Invalid Channel In Alarm Settings")
            return(False)
               
    def get_Alarm_status(self,channel):
        """
        Returns the Status of the alarm for a specific channel.
        Parameters
        ----------
        channel : int or Str castable as int
            Channel (1-8) to probe

        Returns
        -------
        A tuple of length 2. each value will be 1 or 0 (Active or Not active) 
        for High Status (Exceeded High Value) or Low Status (Went below Low value)

        """
        try:
            channel=int(channel)
        except ValueError:
            raise Exception("Channel must be able to be cast as Int")
        
        if channel in range(1,9):
            String_Alarm=self.VI.query("ALARMST? {}".format(channel))
            if String_Alarm[-2:] == r"\n":
                String_Alarm = String_Alarm[:-2]
            list_Alarm=re.split(",",String_Alarm)
            return(tuple(int(i)for i in list_Alarm))
        else:
            raise Exception("Invalid Channel In Alarm Status")
            return(False)
            
    def Clear_Alarm(self):
        """
        Resets Latched alarms for all inputs.
        """
        self.VI.write("ALMRST")
        
    def get_Time(self):
        """
        Get the internal time of the 218.
        Returns a string in the format Month,Day,Year,Hour,Minute,Second

        """
        return(str(self.VI.query("DATETIME?")))
    
    def set_Time(self,Month,Day,Year,Hour,Minute,Second):
        """
        Sets the internal clock of the 218.
        Year especially must be cast as string as 00 is a valid year (2000)

        Parameters
        ----------
        Month : Str
            Specifies month (1-12)
        Day : Str
            Specifies Day, (1-31)
        Year : Str
            Specifies Year (00-99)
        Hour : Str
            Specifies Hour in 24 hour format (0-23)
        Minute : Str
            Specifies time in mintues
        Second : Str
            Specifies seconds (0-59)


        """

        try:#catch cases where non-numeric values have been passed
            int(Month)
            int(Day)
            int(Year)
            int(Hour)
            int(Minute)
            int(Second)
            
        except ValueError:
            raise Exception("Invalid Date/Time entered. Values must be strings of numbers, castable as Int")
        
        self.VI.write("DATETIME "+str(Month)+","+str(Day)+","+str(Year)+","+str(Hour)+","+str(Minute)+","+str(Second))
        
    def query_GPIB(self):
        """
        Gets the GPIB parameters

        Returns
        -------
        A tuple of length 3. In the order Terminator,EOI,Address. Parameters are as Config_GPIB

        """
        String_GPIB=self.VI.query("IEEE?")
        if String_GPIB[-2:] == r"\n":
            String_GPIB = String_GPIB[:-2]
        list_GPIB=re.split(",",String_GPIB)
        return(tuple(int(i) for i in list_GPIB))
    
    def Config_GPIB(self,term,EOI, New_Address):
        """
        Configures the GPIB parameters.
        NOTE: AS YOU CHANGE THE GPIB ADRESS WITH THIS COMMAND, SENDING THIS COMMAND WILL CLOSE THE CURRENT
        INSTANCE OF THIS INSTRUMENT.

        Parameters
        ----------
        term : Int (0-3)
            Sets the Terminator.
            0=CR or LF
            1=LF or CR
            2=LF only
            3=None
        EOI : Int (0-1)
            Sets whether or not to use EOI mode (0=On,1=Off)
        New_Address : Int (1-30)
            Sets the new GPIB address to communicate with.

        """
        try:
            if int(term) not in range (0,4) or int(EOI) not in range(0,3) or int(New_Address) not in range(1-31):
                raise Exception("Invalid GPIB Configuration sent. Check that whats being sent can be cast as Int")
        
        except ValueError:
            raise Exception("Invalid Variable Types detected in GPIB configuration")
            
        self.VI.write("IEEE "+str(term)+","+str(EOI)+","+str(New_Address))
        self.close()
        print("Closed Connection to Lakeshore 218 Due to programmed GPIB change")
    
    def getTempN(self,N):
        """
        query the temperature in Kelvin for channel N

        Parameters
        ----------
        N : int/Str
            Int from 1-8 showing the channel to query

        Returns
        -------
        The reading in Kelvin as a Float

        """
        try:
            if int(N) not in range (1,9):
                raise Exception("Invalid Channel ID. Expected a number between 1 and 8 got {}".format(int(N)))
        except ValueError:
            raise Exception("Channel ID could not be cast as Int. Check inputs")
        
        return(self.__chkFloat(self.VI.query("KRDG? "+str(N))))
    
            
    def getTempAll(self):
        """
        Gets the Temperature Reading in Kelvin for all channels

        Returns
        -------
        A tuple of all the read temperatures

        """
        String_Temps=self.VI.query("KRDG? 0")
        if String_Temps[-2:] == r"\n":
            String_Temps = String_Temps[:-2]
        list_Temps=re.split(",",String_Temps)
        return(tuple(float(i) for i in list_Temps))
    
    def getSensN(self,N):
        """
        query the sensor reading in Ohms for channel N

        Parameters
        ----------
        N : int/Str
            Int from 1-8 showing the channel to query

        Returns
        -------
        The reading in Ohms as a Float

        """
        try:
            if int(N) not in range (1,9):
                raise Exception("Invalid Channel ID. Expected a number between 1 and 8 got {}".format(int(N)))
        except ValueError:
            raise Exception("Channel ID could not be cast as Int. Check inputs")
        
        return(self.__chkFloat(self.VI.query("SRDG? "+str(N))))
    
            
    def getSensAll(self):
        """
        Gets the sensor reading in Ohms for all channels

        Returns
        -------
        A tuple of all the read resistances

        """
        String_Temps=self.VI.query("SRDG? 0")
        if String_Temps[-2:] == r"\n":
            String_Temps = String_Temps[:-2]
        list_Temps=re.split(",",String_Temps)
        return(tuple(float(i) for i in list_Temps))
    
