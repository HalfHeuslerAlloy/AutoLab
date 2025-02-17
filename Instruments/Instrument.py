# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 11:35:57 2025
Generic Class for Instruments. Generic instrument terms (Read/Write/Query) should be defined here so that code
Errors can be processed easier.
Note; This cements self.VI as the syntax for direct write to instruments.

@author: eencsk
"""
import inspect
from pyvisa.constants import StopBits, Parity

class Instrument:
    
    def __init__(self,rm,channel,GPIB=True, Baud_Rate=9600, Data_Bits=8, Parity=Parity.none, Stop_bits=StopBits.one):
        """
        

        Parameters
        ----------
        rm : pyvisa.resource_manager
            the resource manage used to connect to the instruments
        channel : int or Str, optional
            Address of device.
            If int, just the GPIB address, if Str, the full address, as pulled from
            RM.List_Resources
        GPIB : Bool, optional, default is True
            Whether to use GPIB (T) or COM (F) to connect to the instrument.
        Baud_Rate,Data_Bits,Parity and stop_bits are the 
        COM parameters for serial connections


        """
        
        if GPIB ==True:
            if type(channel) != type(" "):
                self.VI = rm.open_resource('GPIB0::' + str(channel) + '::INSTR')
            else:
                self.VI = rm.open_resource(channel)
                
        else:
            if channel == type(" "): #If the address is not a string the slice in next line dont work!
                
                if channel[:3] == "ASRL":
                    self.VI=rm.open_resource(channel,baud_rate=Baud_Rate,data_bits=Data_Bits,
                                             parity=Parity,stop_bits=Stop_bits)
                else:
                    raise Exception("Invalid COM Address, Expected an Int or String Beginning ASRL, got {}".format(channel))
            else:
                try:
                    self.VI=rm.open_resource('COM'+str(channel),baud_rate=Baud_Rate,data_bits=Data_Bits,
                                             parity=Parity,stop_bits=Stop_bits)
                except ValueError:
                    raise Exception("Invalid COM Address. Expected an Int or a string beginning ASRL, got {}".format(channel))
            
        