# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 14:32:51 2026

@author: csk42

Driver for the ancient Princeton 5210 lockin.
As always, similar syntax makes for happy code.

NB: This lockin does NOT return a voltage when the Channels are queried, instead returning a PERCENTAGE of the full-range
Okay, fine. Does make the post-processing a bit more complex, but not a thing that I'm doing here in driverland'
"""

from Instruments.Instrument_class import Instrument
import numpy as np 
from math import ceil, floor
import re
root_two=np.sqrt(2)

class Princeton5210(Instrument):
    
    def __init__(self, rm, Com):
        """
        Initialises the Princeton5210. Assumes you're using GPIB comms. 
        Yell at Craig if you want RS232 communications enabled

        Parameters
        ----------
        rm : pyvisa.resource manager
            the resource manager that'll actually do the talkin'
        Com : Str or int
            Comms address for GPIB or Com-port communications
            If Str, pass the full string to the resource manager (from rm.list_resources()), 
            if int,its assumed to be a GPIB add

        """
        super.__init__(rm, Com)#call the Instrument.__init__ function.
        self.VI.write_termination = self.VI.CRLF
        self.VI.read_termination = self.VI.CRLF#set Term. characters, by default a CR
        self.Write("REMOTE 0")#unlocks the front panel
        
    def __chkFloat(self, s):
        """
        Trims the EOL character (if present) from the as-read string and returns it as a float
        """
        if s[-2:] == r"\n":
            s = s[:-2]
        return float(s)
    
    def __chkFloatList(self, s):
        """
        Trims the EOL character (if present) from the as-read string and returns it as a list of floats
        for when you're querying multiple things in one command.'
        """
        if s[-2:] == r"\n":
            s = s[:-2]
        s = np.array([float(i) for i in s.split(",")])
    def __del__(self):
        self.VI.close()
        
    def setTC(self, TC):
        """
        Sets the filter time-constant

        Parameters
        ----------
        TC : Int
            Index of the following array:
            0   1 ms
            1   3 ms
            2   10 ms
            3   30 ms
            4   100 ms
            5   300 ms
            6   1 s
            7   3 s
            8   10 s
            9   30 s
            10  100 s
            11  300 s
            12  1000 s
            13  3000 s
        """
        
        if int(TC) in range (0,14):
            self.Write("TC"+str(int(TC)))
        else:
            raise ValueError("Invalid P5210 Time Constant, Expected a String containing an int between 1 and 13, got {}".format(TC))
    
    def getTCons(self):
        return(self.Query("TC"))
    
    def setSEN(self, Sens):
        """
        Sets the sensitivity/gain of the lockin.

        Parameters
        ----------
        Sens : Int the index of the following array:
            0   100 nV
            1   300 nV
            2   1 uV
            3   3 uV
            4   10 uV
            5   30 uV
            6   100 uV
            7   300 uV
            8   1 mV
            9   3 mV
            10  10 mV
            11  30 mV
            12  100 mV
            13  300 mV
            14  1 V
            15  3 V
        """
        
        if int(Sens) in range(0,16):
            self.Write("SEN"+ str(int(Sens)))
            
        else:
            raise ValueError("Invalid Princeton5210 set sensitivity value, expected an int-like between 0 and 15, got {}".format(Sens))
            
    def getSens(self):
        self.Query("SEN")
        
    def setReserve(self, Res):
        """
        Sets the lockin Reserve
        
        Parameters
        ----------
        Res : Str
            Lockin Reserve 
            "0"= Low Noise 
            "1"= Normal
            "2"= High Reserve

        """
        if Res in ['0','1','2']:
            self.Write("DR"+Res)
        else:
            raise ValueError("Invalid Princeton5210 Reserve Value")
    
    def getReserve(self):
        return(self.Query("DR"))
    
    def setRefPhase(self, ph):
        """Set the phase reference in Deg.
        
        Parameters
        ----------
        ph : float or string
            Phase to be applied.
        """
        phas=float(ph)
        if  0<= phas < 90:
            self.Write("P 0,"+str(phas*1000))#looking for phase in milidegrees
        elif 90 <= phas <= 180:
            self.Write("P 1,"+str((phas-90)*1000))
        elif (-90)<=phas<0:#translate this to 270-360 range.
            self.Write("P 3,"+str((90+phas)*1000))
        elif (-180)<=phas<(-90):
            self.Write("P 2,"+str((180+phas)*1000))
        else:
            raise ValueError("Invalid Reference phase, expected a number between -180 and 180, got {}".format(ph))
        #THIS IS STUPID
        
    def getRefPhase(self):
        message=self.Query("P")
        message=message.split("\r")#two parameters, separated by CRs
        return((message[1]/1000)+message[0]*90)#AGAIN! STUPID
    
    def setNotchFilters(self,mode):
        """
        Sets the Notch filter modes

        Parameters
        ----------
        mode : int
            Index of the following array:
                
                0   Filters Off
                1   100 Hz Doubleline Filters
                2   50 Hz Line Filters
                3   Both Filters
        """
    
        if mode in [0,1,2,3]:
            self.Write("LF "+str(int(mode)))
        else:
            raise ValueError("Invalid P5210 Line Filter option! Expected a number between 0-3, got {}".format(mode))
        
    def getNotchFilters(self):
        return(self.Query("LF"))
    
    def setHarm (self, Harmonic=1):
       """
       Sets the Harmonic of the reference.

       Parameters
       ----------
       Harmonic : Int, optional
           Harmonic to use. The default is 1.

       """         
       if int(Harmonic) ==1:
           self.Write("F2F 0")
       elif int(Harmonic) ==2:
           self.Write("F2F 1")
       else:
           raise ValueError("Invalid Set Harmonic Value, Expected 1 or 2 got {}".format(Harmonic))
    
    def getHarm(self):
        return(self.Query("M"))
        
    def setFilterSlope(self, sl):
        """
        Sets the slope of the output filters.

        Parameters
        ----------
        sl : int 0-1
            0   6 db/oct
            1   12 db/oct
        """
        if sl in [0,1]:
            self.Write("XDB "+str(int(sl)))
        else:
            raise ValueError("Invalid P5210 Filter slope! Expected either 0 or 1, got {}".format(sl))
    
    def getFilterSlope(self):
        return(self.Query("XDB"))
    
    def isInternalRef(self, ref=False):
        """
        Sets the P5210 to use the internal or external reference,
        Default External

        Parameters
        ----------
        ref : Bool
            Sets the reference source. True=Internal Reference, False=External Reference
            The default is False.
        """
        if ref==False:
            self.Write("IE 0")
        elif ref==True:
            self.Write("IE 1")
        else:
            raise ValueError("Invalid Reference Mode Input. Expected Bool got {}".format(ref))
    
    def getInternalRef(self):
        return(bool(self.Query("IE")))
    
    def setInternalFreq(self, Freq):
        """
        Sets the internal reference frequency

        Parameters
        ----------
        Freq : float
            Reference frequceny in Hz

        """
        Freq=float(Freq)
        if 0.5 <= Freq <= 120000:#in case some clown doesnt sanitise their utility inputs. 
            option=ceil(np.log10(Freq/2))
            #OKay, the thing has frequency bands from 2-20 in a given power of 10, except at the lower (0.5-2) and upper limits (20k-120K)
            #Option should give a quick way of setting that without resulting to massive case-statements.
            freq_to_send=(Freq/(10**option))*10000#use this to scale the frequency between 0.2 and 2 then multiply to be broadcast
            #TODO: Test this. Typo in the manual means I dont quite beleive this
            self.Write("OF "+ str(int(freq_to_send))+" "+str(option))
            
        else:
            raise ValueError("Invalid P5210 Oscillator Frequency. Expected a number between 0.5 and 120000, got {}".format(Freq))
            
            
    def getInternalFreq(self):
        values=re.split(" ",self.Query("OF"))
        #TODO:Test this. Hope it works, but may not. If not, the last character of the string should be the option
        return((float(values)[0]/10000)*(10**float(values[1])))
    
    def setOscAmp(self,Amp):
        """
        Sets the amplitude of the internal oscillator

        Parameters
        ----------
        Amp : Float
            Rms amplitude of the oscillator in V. 0-2 permitted, or 5
        """
        if 0 <= float(Amp) <= 2 or float(Amp)==5.0:
            self.Write("OA "+str(float(Amp)*1000))
        else:
            raise ValueError("Invalid P5210 Oscillator amplitude! Expected a number between 0-2 or 5 exactly, got {}".format(Amp))
    
    def getOscAmp(self):
        return(float(self.Query("OA"))/1000)
    
    def setFilterFrequency(self, Freq):
        """
        Sets the filter frequency. Dont imagine this being used much, but its there!

        Parameters
        ----------
        Freq : Float
            Frequency to be sent to the instrument in Hz. Between 0.5 and 120,000
        """
        
        
        if 1 <= Freq < 100000:#handle the vast majority of cases
            option=floor(np.log10(Freq))
            freq_to_send=(Freq/(10**option))*100
            self.Write("FF "+ str(int(freq_to_send))+" "+str(option))
        elif 100000 <= Freq <= 120000:#high frequency breaks the option function
            freq_to_send=(Freq/1E4)*100
            self.Write("FF "+str(int(freq_to_send)+" 4"))
        elif 0.5 <= Freq < 1: #low frequency does the same.
            self.Write("FF "+str(int(Freq)*100)+ " 0")
        else:
            raise ValueError("Invalid P5210 Filter Frequency! Expected a number between 0.5 and 120,000 Hz, got {}".format(Freq))
            
    def setFilterAutoMode(self, isAuto=True):
        """
        Sets whether the filter frequency is set by the user or drawn from the ref channel

        Parameters
        ----------
        isAuto : Bool, optional
            Whether the filter is set from the ref channel (T) or not (F). The default is True.

        """
        self.Write("ATC "+str(int(isAuto)))
        
    def getFilterAutoMode(self):
        return(bool(self.Query("ATC")))
    
    def setFilterMode(self,mode=2):
        """
        Sets the operating mode of the signal filter

        Parameters
        ----------
        mode : Int, optional
            INdex of the following Array;
            0 No Filter
            1 Notch Filter
            2 Low Pass Filter
            3 Band-Pass Filter
            The default is 2.
        """
        if int(mode) in [0,1,2,3]:
            self.Write("FLT "+str(int(mode)))
        else:
            raise ValueError("Invalid P5210 set filter mode! Expected an int between 0 and 3 got {}".format(mode))
        
    def getFilterMode(self):
        self.Query("FLT")
            
    def setXoff(self, Offset, Enable):
        """Sets the Offset in % on the X channel and toggles with Enable"""
        off_to_send=int(Offset*10)#rounds the offset in % to the integer to send
        if abs(off_to_send) > 1500:
            raise ValueError("Offset out of 300% max range")
        elif Enable == True:
            self.Write('XOF 1 ,'+off_to_send)
        elif Enable == False:
            self.Write('XOF 0 ,'+off_to_send)
    
    def setYoff(self, Offset, Enable):
        """Sets the Offset in % on the Y channel and toggles with Enable"""
        off_to_send=int(Offset*10)#rounds the offset in % to the integer to send
        if abs(off_to_send) > 1500:
            raise ValueError("Offset out of 300% max range")
        elif Enable == True:
            self.Write('YOF 1 '+off_to_send)
        elif Enable == False:
            self.Write('YOF 0 '+off_to_send)
            
    def getXOff(self):
        """

        Returns
        -------
        A tuple of values n1,n2. n1= 0 or 1, whether or not the X-offset is enabled
        n2- the value of the offset in %*100

        """
        string_Off=self.Query('XOF')
        list_Off=re.split(",",string_Off)
        #has to be done beforehand because string comprehension is hard
        return(tuple(float(i) for i in list_Off))#Test this.
    
    def getYOff(self):
        """

        Returns
        -------
        A tuple of values n1,n2. n1= 0 or 1, whether or not the y-offset is enabled
        n2- the value of the offset in %*100

        """
        string_Off=self.Query('YOF')
        list_Off=re.split(",",string_Off)
        #has to be done beforehand because string comprehension is hard
        return(tuple(float(i) for i in list_Off))     
   
    def getAnalog(self, channel):
        """
        Gets the value of the voltage on one of the analog in ports on the lockin

        Parameters
        ----------
        channel : Int(1-4)
            The analog-in port to be queried
            
        Returns
        -------
        The value of the selected input in volts
        """
        if int(channel) in [1,2,3,4]:
            return(self.__chkFloat(self.Query("ADC "+str(int(channel)))))
        else:
            raise ValueError("Invalid Aux-In channel for P5210! Expected a number between 1-4, got {}".format(channel))
            
    def setOutput(self, Voltage):
        """
        Sets the output on the analog outputs on the rear panel
        for voltage control

        Parameters
        ----------
        Voltage : float
            Voltage to be output. Limits between pm 15

        """
        if abs(float(Voltage)) < 15:
            self.Write("DAC "+(str(float(Voltage)*1000)))
            
        else:
            raise ValueError("Invalid P5210 Output voltage! Expected a float between +/-15, got {}".format(Voltage))
            
    def getOutput(self):
        return(self.Query("DAC"))
    
    @property
    def clear(self):
        #clears the Buffer
        self.VI.clear()
    
    @property
    def X(self):
        """Returns X component of lock-in measure AS A FRACTION OF FULL-RANGE."""
        return self.__chkFloat(self.Query('X'))/10000
    @property
    def Y(self):
        """Returns Y component of lock-in measure AS A Fraction OF FULL-RANGE."""
        return self.__chkFloat(self.Query('Y'))/10000
    
    @property
    def XY(self):
        """Returns XY component of lock-in measure."""
        return self.__chkFloatList(self.Query('XY'))/10000
    @property
    def Magnitude(self):
        """Returns Magnitude of lock-in measure."""
        return self.__chkFloat(self.Query('MAG'))/10000
    
    @property
    def Phase(self):
        """
        Returns the Phase-lag of the signal in Degrees
        """
        return self.__chkFloat(self.Query('PHA'))/1000
    
    @property
    def MagPhas(self):
        """
        Returns both the magnitude(as a fraction of full-range) and the phase (in Deg) of the lockin measurement
        """
        MPList=self.__chkFloatList(self.Query('MP'))
        return(MPList[0]/10000,MPList[1]/1000)