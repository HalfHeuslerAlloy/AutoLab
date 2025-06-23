# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 15:26:51 2025

@author: csk42
Driver for the Oxford instruments 2XX(?)ILM.
Assumes that the User is using this as a Passive instrument, so we dont need to 
Do anything other than Read channels and examine the status.
Pages 37-42 of the ILM 200 series manual.
"""
import re
from Instruments.Instrument_Class import Instrument
import time
import numpy as np

class Oxford_ILM(Instrument):
    
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
        
    def __chkFloat(self, s):
        """
        Trims a LF character from a string S.
        Thanks to Nic Hunter

        """
        if s[-2:] == r"\r":#\n for LineFeed, \r for carriage return
            s = s[:-2]
        return float(s)
    
    def getLevelN (self,N):
        """
        Queries the Level for channel N.

        Parameters
        ----------
        N : Int 
            Channel to probe. Should be 1-3.

        Returns
        -------
        The level in % of Full range.

        """
        try:
            N=int(N)
            
        except ValueError:
            raise Exception("Invalid Channel Selection for ILM; Could not be Cast as Int")
        
        if N in range (1,4):
            return(self.Query("R"+str(N)))
        else:
            raise Exception("Invalid Channel Number for ILM, expected an Int between 1 and 3, got {}".format(N))
            
    def Query_Channels(self):
        """
        Query what the ILM channels are detecting through the Examine Command

        Returns
        -------
        List of Len 3. Each element of the list will correspond to a channel, with the following Values;
        OFF=Not in Use
        He=Liquid Helium
        N2=Liquid Nitrogen
        FAULT=Faulty Channel or Probe Not connected
        """
        result=[]
        readback=self.Query("X")
        if readback[-2:]==r"\r":
            readback=readback[:-2]#trim TERM characters if present
        split_readback=re.split(r"\D",readback)#splits the incoming string along the non-numeric characters
        #first element should be blank. 2nd element should be the one we want
        for char in split_readback[1]:
            if re.search("0", char)!=None:
                result.append("OFF")
            elif re.search("1",char)!=None:
                result.append("N2")
            elif re.search("2",char)!=None or re.search("3",char)!=None:#2 is normal Pulsed, 3 is Continuous. 
                result.append("He")
            elif re.search("9",char)!=None:
                result.append("FAULT")
            else:
                raise Exception("INVALID CHARACTER RETURNED! CRAIG DIDNT DO THEIR REGEX PROPERLY!")
        return(result)
    
    def QueryAlarm(self):
        """
        Queries the status of the Relays and so the Alarm.
        Note: I've set this up to query the Alarm state, not whether the Alarm is sounding.
        If you are using this for interlocks/ect, Silencing the Alarm will not clear the
        Alarm Bool.
        
        Returns
        -------
        Tuple of 2 Bools. 
        0=Is the System Alarming
        1=Is the System In a Shut-Down State

        """
        readback=self.Query("X")
        if readback[-2:]==r"\r":
            readback=readback[:-2]#trim TERM characters if present
        split_readback=re.split("R",readback)#Split the incoming string at the "R" point, where the data we want Lives.
        result=split_readback[-1] #TODO:Test that this does return a HEX value and what Prefixes are used.
        #Okay. This will now give a 2-digit HEX value, 
        #which can then be decomposed into a BIN number, 
        #the Value of which is then tied to the status of the Instrument. 
        #I GUESS its efficient but MAN is it DUMB.
        result=bin(int(result,16))#convert to int then binary. 16 for Base 16, i.e Hex
        #BUT! Will have 0b as a prefix.
        result=result[2:]#SLice off prefix.
        if int(result[0])==1:
            Shut_Down=True
        else:
            Shut_Down=False
        
        if int(result[2])==1:
            Alarm=True
        else:
            Alarm=False
        
        return(Alarm,Shut_Down)
        
        
            