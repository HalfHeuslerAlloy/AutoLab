# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 11:14:18 2023

@author: eencsk
"""
import re

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
        if Address[:3] == "ASRL":
            self.VI=rm.open_resource(Address)
        else:
            try:
                int(Address)
                self.VI=rm.open_resource('COM'+str(Address))
            except ValueError:
                raise Exception("Invalid Lakeshore218 Address. Expected an Int or a string beginning ASRL, got {}".format(Address))
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF        #set up command terminators
        
    
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
        
        try:
            channel=int(channel)
            Unit=int(Unit)
        except ValueError:
            print("Invalid Channal or Unit casting. Must be able to be cast as int")
        
        if channel in range(1,9) and Unit in range(1,5):
            self.VI.write("ALARM {0}, {1}, {2}, {3}, {4}, {5}, {6}".format(channel,Enable,Unit,HighV,LowV,Soft_Latch,Hard_Latch))
        else:
            print("Invalid Channel/Unit in Alarm Settings.")
            
    def get_Alarm_settings(self):
        """
        Returns the alarm settings as given in Set_alarm in the order
        Channel, Enabled?,Unit,High Value, Low Value, Deadband, Latch
        """
        String_settings=self.VI.query("ALARM?")
        list_settings=re.split(",",String_Settings)
        return(tuple(float(i) for i in list_settings)
               
    def get_Alarm_status(self):
        
        
        
        
    