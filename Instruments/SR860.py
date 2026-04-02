# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 13:28:52 2023

@author: eencsk - edited by eenmv for the SR860
Driver for the infinitely superior SR860 lockin. 
Where possible, the code names is kept as close as possible to the DSP lockins, to make copy+pasting code
easier. One thing of note is that rather than printing an error message to the terminal, This driver raises 
ValueErrors when things arent right. Needs testing but it should provide better feedback to the AutoLab terminal.

TODO: Impliment the Auto-Modes (Auto Phase, Auto Gain, Auto Offset, Auto Reserve)
"""
from Instruments.Instrument_class import Instrument
import numpy as np 
root_two=np.sqrt(2)

class SR860 (Instrument):
    def __init__(self,rm,Comm_Address):
        """
        Initialises the object as a Stanford SR860 Lockin
        Currently assumes you're using GPIB interface.
        Change the OUTX to 0 if you're using RS232.

        Parameters
        ----------
        rm : 
            PyVisa resource manager
        Comm_Address : Str or Int
            Comms address for GPIB or Com-port communications
            If Str, pass the full string to the resource manager (from rm.list_resources()), 
            if int,its assumed to be a GPIB add

        """
        super().__init__(rm, Comm_Address)
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF 
        #linefeed termination required for GPIB, and also works with RS232 comms
        self.Write("OUTX 1")#sets the output mode to GPIB
        self.Write("OVRM 1")#Prevents the Local Lockout of the Lockin
        
        
    def __del__(self):
        self.VI.close()
    
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
        return s
    
    def setTC(self, TC):
        """
        Sets the Filter time constant

        Parameters
        ----------
        TC : Str
            Index of an array with the following values:
                0:  1 us
                1:  3 us
                2:  10 us
                3:  30 us
                4:  100 us
                5:  300 us
                6:  1 ms
                7:  3 ms
                8:  10 ms
                9:  30 ms
                10:  100 ms
                11:  300 ms
                12:  1 s
                13:  3 s
                14:  10 s
                15:  30 s
                16:  100 s
                17:  300 s
                18:  1 ks
                19:  3 ks
                20:  10ks
                21:  30ks

        """
        int_check=int(TC)
        if int_check in range(0,20):
            self.Write("OFLT"+TC)
        else:
            raise ValueError("Invalid SR860 Time Constant, Expected a String containing an int between 0 and 21, got {}".format(TC))
            
    def getTCons (self):
        """
        Returns
        -------
        The Value of the SR860 Time contstant as a string representing the index of the array in setTC.

        """
        return(self.Query('OFLT?'))
    
    def setSEN(self, vSen):
        """
        Sets the full-scale sensitivity.

        Parameters
        ----------
        vSen : Str
            setTC(Value or Code)
                Codes : ISRC=0/1 ISRC=2/3
                 '0'  = 1 V    1 uA
                 '1'  = 500 mV    500 nA
                 '2'  = 200 mV    200 nA
                 '3'  = 100 mV    100 nA
                 '4'  = 50 mV    50nA
                 '5'  = 20mV    20nA
                 '6'  = 10mV    10nA
                 '7'  = 5mV    5nA
                 '8'  = 2mV    2nA
                 '9'  = 1mV    1nA
                 '10' = 500uV    500pA
                 '11' = 200uV    200pA
                 '12' = 100uV    100pA
                 '13' = 50uV    50pA
                 '14' = 20uV    20pA
                 '15' = 10uV    10pA
                 '16' = 5uV    5pA
                 '17' = 2uV    2pA
                 '18' = 1uV    1pA
                 '19' = 500nV    500fA
                 '20' = 200nV    200fA
                 '21' = 100nV    100fA
                 '22' = 50nV    50fA
                 '23' = 20nV    20fA
                 '24' = 10nV    10fA
                 '25' = 5nV    5fA
                 '26' = 2nV    2fA
                 '27' = 1nV    1fA
            

        """
        int_check=int(vSen)
        if int_check in range(0,27):
            self.Write("SCAL"+vSen)
        else:
            raise ValueError("Invalid SR860 Sensitivity, Expected a String containing an int between 0 and 27, got {}".format(vSen))
            
    def getSens(self):
        return(self.Query('SCAL?'))
        #for easier meshing with Lockins across different input modes. 
    
    def setReserve(self, Res):
        """
        Sets the lockin Reserve
        
        Parameters
        ----------
        Res : Str
            Lockin Reserve 
            "0"= High Reserve
            "1"= Normal
            "2"= Low Noise

        """
        if Res in ['0','1','2']:
            self.Write("RMOD"+Res)
        else:
            raise ValueError("Invalid Reserve Value")
        
    def getReserve(self):
        return(self.Query("RMOD?"))
    
    def FilterSlope(self, sl):
        """Set the output filter slope.
        
        Usage :
            FilterSlope(Code)
                Codes :
                 '0' = 6 dB/octave
                 '1' = 12 dB/octave
                 '2' = 18 dB/octave
                 '3' = 24 dB/octave
        
        Parameters
        ----------
        sl : string
            String for code.
        """
        if sl in ['0', '1', '2', '3']:
            self.Write('OFSL' + sl)
        else:
            raise ValueError('SR830 Lock-In Wrong Slope Code')
        
    def getFilterSlope(self):
        return(self.Query('OFSL?'))
    
    def isInternalRef(self, ref=False):
        """
        Sets the SR830 to use the internal or external reference,
        Default External

        Parameters
        ----------
        ref : Bool
            Sets the reference source. True=Internal Reference, False=External Reference
            The default is False.
        """
        if ref==False:
            self.Write("FMOD0")
        elif ref==True:
            self.Write("FMOD1")
        else:
            raise ValueError("Invalid Reference Mode Input. Expected Bool got {}".format(ref))
    
    def setRefPhase(self, ph):
        """Set the phase reference in Deg.
        
        Parameters
        ----------
        ph : float or string
            Phase.
        """
        P = str(ph)
        self.Write('PHAS'+ P)
        
    def getRefPhase(self):
        """Get the programed phase reference."""
        return self.__chkFloat(self.Query('PHAS?'))
    
    def setOscilatorAmp(self, amp):
        """Set the internal Oscilator Amplitude.
        
        Parameters
        ----------
        amp : float
            Amplitude in volts.
        """
        A = str(int(amp))
        if 0.004 <= amp <= 5.0 :
            self.Write('SLVL'+ A)
        else:
            raise ValueError("Invalid SR830 Oscillator Amplitude. Expected a number between 0.004 and 5, got {}".format(amp))
    
    def getOscillatorAmp(self):
        return self.__chkFloat(self.Query("SLVL?"))
    
    def setInternalFreq(self, Freq):
        """
        Sets the internal reference frequency

        Parameters
        ----------
        Freq : float
            Reference frequceny in Hz

        """
        if 0.001 <= float(Freq) <= 102000:#in case some clown doesnt sanitise their utility inputs. 
            self.Write("FREQ"+str(Freq))
        else:
            raise ValueError("Invalid SR830 Oscillator Frequency. Expected a number between 0.001 and 102000, got {}".format(Freq))

    def ConfigureReference(self, Internal=False,Frequency=119.77, Amp=0.05, Phase=0.0, Edge_Trigger='Falling Edge', Harmonic=1):
        """
        Function to configure the reference channel. Combination of Individual utilities, and a way to set
        Neg Edge Trigger and input Harmonic. Will only config the frequency and Amp settings on Internal=True
        And the edge Trigger on Edge=False
        Parameters
        ----------
        Internal : Bool, optional
            Sets whether the reference is Internally or externally Supplied. T=Internal,
            F=External. The default is False.
        Frequency : Float, optional
            Sets the Internal OSc. Frequency in Hz. The default is 119.77.
        Amp : Float, optional
            Sets the Internal oscillator amplitude in Volts. The default is 0.05.
        Phase : Float, optional
            Sets the phase lag. The default is 0.0.
        Edge_Trigger : Str, optional
            Sets whether the Oscillator is triggered off the rising, falling or 0 crossing. The default is 'Falling Edge'.
        Harmonic : Int, optional
            Detection Harmonic. The default is 1.
        """
        if Internal==True:
            self.isInternalRef(Internal)
            self.setOscilatorAmp(Amp)
            self.setInternalFreq(Frequency)
        elif Internal==False:
            self.isInternalRef(Internal)
            Edge=2
            #variable to change, rather than writing out 3 VI.write statements
            #Default:2 Falling Edge
            if Edge_Trigger=="Falling Edge":
                Edge=2
            elif Edge_Trigger=="Rising Edge":
                Edge=1
            elif Edge_Trigger=="Zero Crossing":
                Edge=0
            else:
                raise ValueError("Invalid Edge Trigger String")
            self.Write("RSLP"+str(Edge))
        else:
            raise ValueError("Invalid Internal/External Reference Status. Expected a Bool, got {}".format(Internal))
            
        self.setRefPhase(Phase)
        if 1 <= Harmonic <=19999:
            self.Write("HARM"+str(Harmonic))
        else:
            raise ValueError("Invalid Harmonic. You're Crazy!")
            
    def ConfigureInput(self, Input_Mode,Shield_Grounded=False,Coupling="AC",Notch_Filters=0,Sync=False,Filter=3,Reserve=2):
        """
        Configures the input mode, coupling and Filters. Fair Warning, its a Hell of Elifs. 

        Parameters
        ----------
        Input_Mode : Int. Selects the input mode of the lockin
            0=Voltage A
            1=Voltage A-B
            2=Current, 1 MOhm gain
            3=Current, 100 MOhm gain
        Shield_Grounded : Bool, optional
            Selects whether the shield is Grounded (T) or floating (F). The default is False.
        Coupling : Str, optional
            Lockin coupling mode. The default is "AC".
        Notch_Filters : Int, optional
            Selects wheter the line filters are on
            0=No Line Filters
            1=50 Hz Line Filter
            2=100 Hz Line Filter
            3=Both Filters on. The default is 0.
        Sync : Bool, optional
            Selects whether the sync filters are on (T) or not (F). The default is False.
        Filter : Int, optional
            passthrough to setFilterSlope. The default is 3.
        Reserve : TYPE, optional
            passthrough to setReserve. The default is 2.
        """
        if int(Input_Mode) in range (0,4):
            self.Write("ISRC"+str(Input_Mode))
        else:
            raise ValueError("Invalid Input Signal Status. Expected an int between 0 and 3, got {}".format(Input_Mode))
        if Shield_Grounded==False:
            self.Write("IGND0")
        elif Shield_Grounded==True:
            self.Write("IGND1")
        else:
            raise ValueError("Invalid Shield grounded Status. Expected a Bool, got {}".format(Shield_Grounded))
        
        if Coupling  == "DC":
            self.Write('ICPL1')
        elif Coupling  == 'AC':
            self.Write('ICPL0')
        else:
            raise ValueError("Invalid Coupling Status. Expected \"AC\" or \"DC\", got {}".format(Coupling))
        
        if int(Notch_Filters) in range (0,4):#requires casting as int incase a float or string gets in.
            self.Write("ILIN"+str(Notch_Filters))
        else:
            raise ValueError("Invalid Notch Filter Status. Expected a number between 0 and 3, got {}".format(Notch_Filters))
            
        if Sync==False:
            self.Write("SYNC0")
        elif Sync==True:
            self.Write("SYNC1")
        else:
            raise ValueError("Invalid sync Filter Status. Expected a Bool, got {}".format(Sync))
            
        self.FilterSlope(Filter)
        self.setReserve(Reserve)
    
    def setX_OffExp(self,Offset,Expand=0):
        """
        Sets and applies the Offset and Expand for Just the X channel. Major Diversion from the DSP lockins, as there 
        Is no way to set an offset that is not applied.

        Parameters
        ----------
        Offset : Float
            Offset in percent for the X Channel. Limit of pm105%
        Expand : Int, optional.
            Whether to enable the Expand for the X Channel
            0= No expand
            1= x10 expand
            2= x100 expand.The Default is 0

        """
        if -105.0 <= Offset <= 105.0 and int(Expand) in range (0,3):
            self.Write("OEXP1,"+str(Offset)+","+str(Expand))
        else:
            raise ValueError("Invalid X Offset and Expand Status")
    
    def setY_OffExp(self,Offset,Expand=0):
        """
        Sets and applies the Offset and Expand for Just the Y channel. Major Diversion from the DSP lockins, as there 
        Is no way to set an offset that is not applied.

        Parameters
        ----------
        Offset : Float
            Offset in percent for the X Channel. Limit of pm105%
        Expand : Int, optional.
            Whether to enable the Expand for the X Channel
            0= No expand
            1= x10 expand
            2= x100 expand.The Default is 0

        """
        if -105.0 <= Offset <= 105.0 and int(Expand) in range (0,3):
            self.Write("OEXP2,"+str(Offset)+","+str(Expand))
        else:
            raise ValueError("Invalid Y Offset and Expand Status")
            
    def getX_OffExp(self):
        """
        Querys the X offset and Expand

        Returns
        -------
        List of size 2
            Element 0 will be the offset in %. Element 1 will be the status of the expand, as in setX_OffExp

        """
        return self.__chkFloatList(self.Query('OEXP?1'))
    
    def getY_OffExp(self):
        """
        Querys the Y offset and Expand

        Returns
        -------
        List of size 2
            Element 0 will be the offset in %. Element 1 will be the status of the expand, as in setX_OffExp

        """
        return self.__chkFloatList(self.Query('OEXP?2'))
        
    @property
    def clear(self):
        #clears the Buffer
        self.VI.clear()
    @property
    def X(self):
        """Returns X component of lock-in measure."""
        return self.__chkFloat(self.Query('OUTP? 0'))
    @property
    def Y(self):
        """Returns Y component of lock-in measure."""
        return self.__chkFloat(self.Query('OUTP? 1'))
    @property
    def XY(self):
        """Returns XY component of lock-in measure."""
        return self.__chkFloatList(self.Query('SNAP? 0,1'))
    @property
    def Magnitude(self):
        """Returns Magnitude of lock-in measure."""
        return self.__chkFloat(self.Query('OUTP? 2'))
    @property
    def X_PP(self):
        """Returns peak-peak X component of lock-in measure."""
        return (self.__chkFloat(self.Query('OUTP? 0')))*root_two
    @property
    def Y_PP(self):
        """Returns peak-peak Y component of lock-in measure."""
        return (self.__chkFloat(self.Query('OUTP? 1')))*root_two
    @property
    def XY_PP(self):
        """Returns peak-peak XY component of lock-in measure."""
        return (self.__chkFloatList(self.Query('SNAP? 0,1')))*root_two#most likely to fall over
    @property
    def Magnitude_PP(self):
        """Returns peak-peak Magnitude of lock-in measure."""
        return (self.__chkFloat(self.Query('OUTP? 2')))*root_two
    @property
    def Phase(self):
        """Returns Phase of lock-in measure."""
        return self.__chkFloat(self.Query('PHAS?'))
    @property
    def Freq(self):
        """Returns Frequency of lock-in device."""
        return self.__chkFloat(self.Query('FREQ?'))