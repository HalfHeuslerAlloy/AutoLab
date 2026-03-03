# -*- coding: utf-8 -*-
"""
Created on Thu Feb 26 13:23:38 2026

@author: csk42

Driver for the old-style SRS530 Lockin. Again, trying to keep a consistent syntax for lockin commands
"""

from Instruments.Instrument_class import Instrument
import numpy as np 
root_two=np.sqrt(2)

class SR530(Instrument):
    def __init__(self, rm, Com):
        """
        Initialises the SRS530. Assumes you're using GPIB comms. 
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
        
        self.IsExpand=False
        #As the expands dont effect the X/Y outputs, only the displayed channels, add a latch here that can be toggled to 
        #Prompt user to select the appropriate measurement.
        self.VI.write_termination = self.VI.CR
        self.VI.read_termination = self.VI.CR#set Term. characters, by default a CR
        self.Write("I0")#enable the Front panel if locked out
        
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
        
    def setTC(self, TC, mode=1):
        """
        Sets the filter time-constants

        Parameters
        ----------
        TC : Str
        string containing the following numbers:
            n Pre Time Constant (m=1)
                1   1 mS
                2   3 mS
                3   10 mS
                4   30 mS
                5   100 mS
                6   300 mS
                7   1 S
                8   3 S
                9   10 S
                10  30 S
                11  100 S
                
                n Post Time Constant (m=2)
                0 none
                1   0.1 S
                2   1 S
        
        mode : int, optional
            DESCRIPTION. The default is 1.
            Whether to set the pre-time constants (1) or post-time constants(2)
            Defaults to pre-TC because thats the one I would most mess with

        """
        int_check=int(TC)
        if int(mode) == 1:
            if int_check in range(1,12):
                self.Write("T 1,"+TC)
            else:
                raise ValueError("Invalid SR530 Time Constant, Expected a String containing an int between 1 and 11, got {}".format(TC))
        elif int(mode) ==2:
            if int_check in range (0,3):
                self.Write("T 2,"+TC)
            else:
                raise ValueError("Invalid SR530 Post-Time Constant, Expected a String containing an int between 0 and 2, got {}".format(TC))
        else:
            raise ValueError("Invalid 530 Time-constant Mode, expected an int-like of 1 or 2, got: {}".format(mode))
            
    def getTC(self,mode=1):
        if mode==1 or mode==2:
            return(self.Query(("T ")+str(mode)))
        else:
            raise ValueError("Invalid Get Timeconstant Mode, should be 1 or 2, got {}".format(mode))
    
    def setSEN(self, Sens):
        """
        Sets the sensitivity/gain of the lockin.

        Parameters
        ----------
        Sens : Str
            A string containing an index of this array:
                n   Sensitivity
                1   10 nV
                2   20 nV
                3   50 nV
                4   100 nV
                5   200 nV
                6   500 nV
                7   1 µV
                8   2 µV
                9   5 µV
                10  10 µV
                11  20 µV
                12  50 µV
                13  100µV
                14  200µV
                15  500µV
                16  1 mV
                17  2 mV
                18  5 mV
                19  10 mV
                20  20 mV
                21  50 mV
                22  100 mV
                23  200 mV
                24  500 mV

        Sensitivities below 100 nV will not work if there is no preamp. 
        TODO: Check if this will be acted on or if this will throw an error.
        """
        
        int_check=int(Sens)
        if int_check in range(1,25):
            self.Write("G "+str(Sens))
        else:
            raise ValueError("Invalid Set 530 Sensitivity command. Expected an int between 1 and 24, got {}".format(Sens))
        
    def getSens(self):
        return(self.Query("G"))
    
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
            self.Write("D"+Res)
        else:
            raise ValueError("Invalid Reserve Value")
    
    def getReserve(self):
        return(self.Query("D"))
    
    def setRefPhase(self, ph):
        """Set the phase reference in Deg.
        
        Parameters
        ----------
        ph : float or string
            Phase.
        """
        P = str(ph)
        self.Write('P '+ P)
    
    def getRefPhase(self):
        """Get the programed phase reference."""
        return self.__chkFloat(self.Query('P'))
    
    def setNotchFilters (self, lineF=False, Double_lineF=False):
        """
        Sets the line and doubleline filters

        Parameters
        ----------
        lineF : Bool, optional
            The status of the LineFilter On (T)/Off (F). The default is False.
        Double_lineF : Bool, optional
            The status of the 100 Hz doubleLineFilter On (T)/Off (F). The default is False.

        """
        if type(lineF) == bool and type(Double_lineF) == bool :
           self.Write("L 1,"+str(int(lineF))) 
           self.Write("L 2,"+str(int(Double_lineF)))
        else:
            raise Exception("Invalid Notch Filter values! Was expecting two bools, got {0},{1}".format(lineF,Double_lineF))
            
    def getNotchFilters (self, filter_select=1):
        """
        Gets the status of the Line Filters. 

        Parameters
        ----------
        filter_select : int, optional
            Which filter to examine
            1 = 50 Hz line filter
            2 = 100 Hz Doubleline filter. The default is 1.
            
        Returns
        -------
        The status of the filter selected. 1= On, 0= Off.

        """
        if int(filter_select)==1:
            return(self.Query("L 1"))
        elif int(filter_select)==2:
            return(self.Query("L 2"))
        else:
            raise ValueError("Invalid Get Notch filter Value. Expected 1 or 2, got {}".format(filter_select))
            
            
    def setHarm (self, Harmonic=1):
       """
       Sets the Harmonic of the reference.

       Parameters
       ----------
       Harmonic : Int, optional
           Harmonic to use. The default is 1.

       """         
       if int(Harmonic) ==1:
           self.Write("M 0")
       elif int(Harmonic) ==2:
           self.Write("M 1")
       else:
           raise ValueError("Invalid Set Harmonic Value, Expected 1 or 2 got {}".format(Harmonic))
    
    def getHarm(self):
        return(self.Query("M"))
    
    def setNoiseBW(self, NoiseBW=0):
        """
        Sets the ENBW (Filter Slope?)

        Parameters
        ----------
        NoiseBW : int, optional
            Pow of 10 that the NoiseBW is set to only 0 and 1 valid. The default is 0.
        """
        if int(NoiseBW) == 0:
            self.Write("N 0")
        elif int(NoiseBW) ==1:
            self.Write("N 1")
        else:
            raise ValueError("Invalid Set NoiseBW Value. Expected 0 or 1, got {}".format(NoiseBW))
    
    def getNoiseBW(self):
        return(self.Query("N"))
    
    def setTrigMode(self, TrigMode=2):
        """
        Sets the trigger slope for the Lockins

        Parameters
        ----------
        TrigMode : Int, optional
            The mode which the Trigger will be set from
            0 = Positive Edge
            1 = Symmetric
            2 = Negaitve Edge
            The default is 2.
        """
        
        if int(TrigMode) in ([0,1,2]):
            self.Write("R "+str(int(TrigMode)))
        else:
            raise ValueError("Invalid Set Trigger Mode Option")
            
    def getTrigMode(self):
        return(self.Write("R"))
    
    def setOutput(self, Voltage, port=6):
        """
        Sets the output on pins 5 or 6 on the Rear panel
        for voltage control

        Parameters
        ----------
        Voltage : float
            Voltage to be output. Limits between pm 10.238
        port : int, optional
            Port to activate. Valid are 5 or 6, but 5 defaults to the Ratio output. 
            The default is 6.

        """
        if abs(float(Voltage)) < 10.239:
            if int(port) in ([5,6]):
                self.Write("X"+str(int(port))+","+(str(float(Voltage))))
            else:
                raise ValueError("Invalid 530 output port! Expected 5 or 6, got {}".format(port))
        else:
            raise ValueError("Invalid 530 Output voltage! Expected a float between +/-10.238, got {}".format(Voltage))
    
    def getAnalog (self, port):
        """
        Gets the input/output value of one of the ports on the rear of the Lockin

        Parameters
        ----------
        port : int
            Port to be queried (1-5)

        Returns
        -------
        The voltage going into/out of that port

        """
        
        if int(port) in ([1,2,3,4,5]):
            return(self.Query("X "+str(int(port))))
        else:
            raise ValueError("Invalid 530 Get Analog in/out por! Expected 1-5, got {}".format(port))
            
    def XOffset (self, XOff=0.0):
        """
        Sets the offsets for the X, Channel
        If the value is 0, then the offset is turned off, if the value is non-0,
        the offset is activated
        
        Parameters
        ----------
        XOff : Float, optional
            The offset in volts for the X-Channel. The default is 0.0.

        """
        if XOff == 0:
            self.Write("OX 0")
        else:
            #first get sensitivity so offset can be checked
            sens=int(self.Query("G"))
            dev=sens//3
            mod=sens%3
            if mod == 1:
                fullsens=1*10**(-8+dev)
            elif mod ==2:
                fullsens=2*10**(-8+dev)
            else:
                fullsens=5*10**(-9+dev)#quick-n-dirty way of getting full-range sensitivity from the G-table
            
            if abs(XOff) < fullsens:
                self.Write("OX {}".format(XOff))
            else:
                raise ValueError("XOffset out of Range! Current Sensitivity={0}, Requested offset={1}".format(fullsens,XOff))
    
    def YOffset (self, YOff=0.0):
        """
        Sets the offsets for the Y, Channel
        If the value is 0, then the offset is turned off, if the value is non-0,
        the offset is activated
        
        Parameters
        ----------
        XOff : Float, optional
            The offset in volts for the X-Channel. The default is 0.0.

        """
        if YOff == 0:
            self.Write("OY 0")
        else:
            #first get sensitivity so offset can be checked
            sens=int(self.Query("G"))
            dev=sens//3
            mod=sens%3
            if mod == 1:
                fullsens=1*10**(-8+dev)
            elif mod ==2:
                fullsens=2*10**(-8+dev)
            else:
                fullsens=5*10**(-9+dev)#quick-n-dirty way of getting full-range sensitivity from the G-table
            
            if abs(YOff) < fullsens:
                self.Write("OX {}".format(YOff))
            else:
                raise ValueError("YOffset out of Range! Current Sensitivity={0}, Requested offset={1}".format(fullsens,YOff))
                
    def ROffset (self, ROff=0.0):
        """
        Sets the offsets for the R, Channel
        If the value is 0, then the offset is turned off, if the value is non-0,
        the offset is activated
        
        Parameters
        ----------
        XOff : Float, optional
            The offset in volts for the X-Channel. The default is 0.0.

        """
        if ROff == 0:
            self.Write("OR 0")
        else:
            #first get sensitivity so offset can be checked
            sens=int(self.Query("G"))
            dev=sens//3
            mod=sens%3
            if mod == 1:
                fullsens=1*10**(-8+dev)
            elif mod ==2:
                fullsens=2*10**(-8+dev)
            else:
                fullsens=5*10**(-9+dev)#quick-n-dirty way of getting full-range sensitivity from the G-table
            
            if abs(ROff) < fullsens:
                self.Write("OX {}".format(ROff))
            else:
                raise ValueError("ROffset out of Range! Current Sensitivity={0}, Requested offset={1}".format(fullsens,ROff))
                
    def setExpand (self, XPand=False, YPand=False):
        """
        Sets the Expands on Channel 1 and 2. NB: This doesnt effect the X and Y output,
        Just the Channel 1 and 2 output. Tis Jank.


        Parameters
        ----------
        XPand : Bool, optional
            Set the X-Expand. The default is False.
        YPand : Bool, optional
            Sets the Y-Expand. The default is False.

        """

        if XPand == True or YPand == True:
            self.IsExpand=True
            
        self.Write("E 1,"+str(int(XPand)))
        self.Write("E 2,"+str(int(YPand)))
        
    def getExpands(self):
        XPand=int(self.Query("E 1"))
        YPand=int(self.Query("E 2"))
        if XPand ==1 or YPand == 1:
            self.IsExpand=True#add way to set the IsExpand from a "read instrument" routine
            
    def AutoPhase(self):
        """
        Runs the Lockin's Built-in Autophase
        """
        self.Write("AP")
    def ZeroPhase(self):
        """
        Runs the Lockin's Zero Phase routine
        """
        self.Write("K 8")
        
    def AutoOffsetX(self):
        self.Write("AX")
    def AutoOffsetY(self):
        self.Write("AY")
    def AutoOffsetR(self):
        self.Write("AR")#Automatic Offset Routines
        
    def setDisplay(self, display_option):
        """
        Sets the parameter displayed on the 
        Front panel and returned from the output channels
        Parameters
        ----------
        display_option : Int
        index of the array:
            n   Channel 1 Channel 2
            0   X   Y
            1   X Offset Y Offset
            2   R Ø
            3   R Offset Ø
            4   X Noise Y Noise
            5   X5 (D/A) X6 (D/A)

        """
        if int(display_option) in ([0,1,2,3,4,5]):
            self.Write("S "+str(int(display_option)))
        else:
            raise ValueError("Invalid Channel Display selection, expected an int between 0 and 5, got {}".format(display_option))

    def reset (self):
        """
        Runs the Lockin Reboot Setting. Will reset channel 5 to be the ratio output, Resets settings to default value

        """
        self.Write("Z")
    
    def setBandPass(self, Bandpass=True):
        """
        Enables or Disables the Bandpass filters 

        Parameters
        ----------
        Bandpass : Bool, optional
            Whether the bandpass is enabled (T) or Disabled (F). The default is True.

        """
        if type(Bandpass)==bool:
            self.Write("B"+int(Bandpass))
        else:
            raise ValueError("Invalid 530 Bandpass set! Its a Bool you nerd! Not whatever this is! {}".format(Bandpass))
    
    def getBandPass(self):
        return(bool(self.Query("B")))
    
    @property
    def X(self):
        """
        Returns the X-component of the Lockin, Unexpanded
        """
        return(self.__chkFloat(self.Query("QX")))
    
    @property
    def Y(self):
        """
        Returns the Y-component of the Lockin, Unexpanded
        """
        return(self.__chkFloat(self.Query("QY")))
    @property
    def X_PP(self):
        """
        Returns the Peak-Peak X-component of the Lockin, Unexpanded
        """
        return(self.__chkFloat(self.Query("QX"))*root_two)
    
    @property
    def Y_PP(self):
        """
        Returns the Peak-Peak Y-component of the Lockin, Unexpanded
        """
        return(self.__chkFloat(self.Query("QY"))*root_two)  
    
    @property
    def XY(self):
        """
        Returns the X and Y components of the lockin
        """
        return(self.__chkFloat(self.Query("QX")),self.__chkFloat(self.Query("QY")))
    @property
    def XY_PP(self):
        """
        Returns the Peak-Peak X and Y components of the lockin
        """
        return(self.__chkFloat(self.Query("QX"))*root_two,self.__chkFloat(self.Query("QY"))*root_two)
    @property
    def Freq(self):
        return(self.__chkFloat(self.Query("F")))
    
    @property
    def Phase(self):
        return(self.__chkFloat(self.Query("P"))) 
    
    @property
    def Ch1(self):
        return(self.__chkFloat(self.Query("Q1")))
    
    @property
    def Ch2(self):
        return(self.__chkFloat(self.Query("Q2")))