# -*- coding: utf-8 -*-
"""
Created on Fri May 13 10:55:39 2022

@author: eenmv
"""

import numpy as np
import re

root_two=np.sqrt(2)
class DSP_7280(object):
    def __init__(self,rm, GPIB_Address, RemoteOnly = False):
        """
        Initializes the object as the 7265 Lock-in Amplifier.
        
        This class controls the DSP Lock-In Amplifier:
        EG&G Instruments, Model 7280
        Should work with Signal Recovery 7280 DSP Lock-In
        
        Parameters
        ----------
        GPIB_Address : int, optional
            GPIB Address of device.
        RemoteOnly : bool, optional
            Control remotely (T) or not (F).
        """
        if type(GPIB_Address) != type(" "):
            self.VI = rm.open_resource('GPIB0::' + str(GPIB_Address) + '::INSTR')
        else:
            self.VI = rm.open_resource(GPIB_Address)
        self.VI.write_termination = self.VI.CR
        self.VI.read_termination = self.VI.CR
        #self.VI = visa.instrument('GPIB0::' + str(GPIB_Address))
        self.RemoteOnly(RemoteOnly)
    def __del__(self):
        self.VI.close()
        
    def __chkFloat(self, s):
        if s[-2:] == r"\r":
            s = s[:-2]
        return float(s)
    
    def __chkFloatList(self, s):
        if s[-2:] == r"\r":
            s = s[:-2]
        s = np.array([float(i) for i in s.split(",")])
        return s
        
    def RemoteOnly(self, rO = True):
        """
        Activate or deactivate Remote Only mode for device.
        
        Parameters
        ----------
        r0 : bool, optional
            Remote Only (T) or not (F).
        """
        if rO:
            self.VI.write('REMOTE 1')
        else:
            self.VI.write('REMOTE 0')
            
    def setTC(self, TC):
        """ Sets the Filter Time Constant.
        
        Usage :
            setTC(Value or Code)
                Codes :
                 '0'  = 1 us
                 '1'  = 2 us
                 '2'  = 5 us
                 '3'  = 10 us
                 '4'  = 20 us
                 '5'  = 50 us
                 '6'  = 100 us
                 '7'  = 200 us
                 '8'  = 500 us
                 '9'  = 1 ms
                 '10' = 2 ms
                 '11' = 5 ms
                 '12' = 10 ms
                 '13' = 20 ms
                 '14' = 50 ms
                 '15' = 100 ms
                 '16' = 200 ms
                 '17' = 500 ms
                 '18' = 1 s
                 '19' = 2 s
                 '20' = 5 s
                 '21' = 10 s
                 '22' = 20 s
                 '23' = 50 s
                 '24' = 100 s
                 '25' = 200 s
                 '26' = 500 s
                 '27' = 1 ks
                 '28' = 2 ks
                 '29' = 5 ks
                 '30' = 10 ks
                 '31' = 20 ks
                 '32' = 50 ks
                 '33' = 100 ks
                Values are rounded to corresponding code.
        
        Parameters
        ----------
        TC : float or string
            Float for time value or string for code.
        """
        if type(TC) != type(' '):
            TC = np.abs(TC) - 1E-9
            TC = np.clip(TC, 0, 199E3)
            bins = np.array([1E-6, 2E-6, 5E-6, 10E-6, 20E-6, 50E-6,
                                100E-6, 200E-6, 500E-6,
                                1E-3,2E-3,5E-3,
                                10E-3, 20E-3, 50E-3,
                                100E-3, 200E-3, 500E-3,
                                1, 2, 5, 10, 20, 50,
                                100, 200, 500,
                                1E3, 2E3, 5E3, 10E3, 20E3, 50E3,
                                100E3])
            TC = str(len(bins[bins <= TC]))
        if TC in map(str, range(31)):
            self.VI.write('TC ' + TC)
        else:
            print('EG&G 7265 Lock-In Wrong Time Constant Code')
    def __getTC(self):
        return float(self.VI.query('TC.'))
    TC = property(__getTC, setTC, None, "Filter Time Constant.")
    def getTCons (self):
        return(self.VI.query('TC'))#gets the code for easier meshing with formatting. 
    #Basically, if somoene sets a 1Ks TC, writing that as 1000 will be nasty.
    
    def setSEN(self, vSen):
        """ Sets the Full Scale Sensitivity.
        
        Usage :
            setTC(Value or Code)
                Codes : IMODE=0 IMODE=1 IMODE=2
                 '3'  = 10 nV   10 fA   n/a
                 '4'  = 20 nV   20 fA   n/a
                 '5'  = 50 nV   50 fA   n/a
                 '6'  = 100 nV  100 fA  n/a
                 '7'  = 200 nV  200 fA  2 fA
                 '8'  = 500 nV  500 fA  5 fA
                 '9'  = 1 uV    1 pA    10 fA
                 '10' = 2 uV    2 pA    20 fA
                 '11' = 5 uV    5 pA    50 fA
                 '12' = 10 uV   10 pA   100 fA
                 '13' = 20 uV   20 pA   200 fA
                 '14' = 50 uV   50 pA   500 fA
                 '15' = 100 uV  100 pA  1 pA
                 '16' = 200 uV  200 pA  2 pA
                 '17' = 500 uV  500 pA  5 pA
                 '18' = 1 mV    1 nA    10 pA
                 '19' = 2 mV    2 nA    20 pA
                 '20' = 5 mV    5 nA    50 pA
                 '21' = 10 mV   10 nA   100 pA
                 '22' = 20 mV   20 nA   200 pA
                 '23' = 50 mV   50 nA   500 pA
                 '24' = 100 mV  100 nA  1 nA
                 '25' = 200 mV  200 nA  2 nA
                 '26' = 500 mV  500 nA  5 nA
                 '27' = 1V      1 uA    10 nA
                Values are rounded to corresponding code.
        
        Parameters
        ----------
        vSen : float or string
            Float for sensitivity value or string for code.
        """
        InputMode = self.VI.query('IMODE')
        if type(vSen) != type(' '):
            if InputMode == '0':
                vSen = vSen * 1.0E-6 
            vSen = np.abs(vSen) - 1E-18
            vSen = np.clip(vSen, 0, 0.99E-6)
            bins = np.array([0, 10E-15, 20E-15, 
                                50E-15, 100E-15, 200E-15, 500E-15,
                                1E-12, 2E-12, 5E-12, 10E-12, 20E-12, 
                                50E-12, 100E-12, 200E-12, 500E-12,
                                1E-9, 2E-9, 5E-9, 10E-9, 20E-9, 
                                50E-9, 100E-9, 200E-9, 500E-9,
                                1E-6])
            vSen = len(bins[bins <= vSen])
            if InputMode == '2':
                vSen = vSen + 6
                vSen = np.clip(vSen, 7, 27)
            vSen = str(vSen)
        if vSen in map(str, range(1,28)):
            self.VI.write('SEN ' + vSen)
        else:
            print('EG&G 7265 Lock-In Wrong Scale Sensitivity Code')
    def __getSEN(self):
        return float(self.VI.query('SEN.'))
    SEN = property(__getSEN, setSEN, None, "Full Scale Sensitivity.")
    def getSens(self):
        return(self.VI.query('SEN'))
    #for easier meshing with Lockins across different input modes. 
    
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
            self.VI.write('SLOPE ' + sl)
        else:
            print('EG&G 7265 Lock-In Wrong Slope Code')
    
    def InputMode(self, imode):
        """Current/Voltage mode Input Selector.
        
        Usage :
            InputMode(Code)
                Codes :
                 '0' = Voltage Mode
                 '1' = Current Mode High bandwidth
                 '2' = Current Mode Low noise
        
        Parameters
        ----------
        imode : string
            String for code.
        """
        if imode in ['0', '1', '2']:
            self.VI.write('IMODE ' + imode)
        else:
            print('EG&G 7265 Lock-In Wrong Input Mode Code')
            
    def VoltageInputMode(self, vmode):
        """Voltage Input Configuration
        Usage :
            VoltageInputMode(Code)
                Codes :
                 '0' = Grounded
                 '1' = A Input only
                 '2' = -B Input only
                 '3' = A-B diferential mode
        
        Parameters
        ----------
        vmode : string
            String for code.
        """
        self.VI.write('VMODE 0')
        if vmode in ['0', '1', '2', '3']:
            self.VI.write('VMODE ' + vmode)
        else:
            print('EG&G 7265 Lock-In Wrong Voltage Configuration Code')
    
    def Sync(self, Sy = True):
        """Enable or disable Synchronous time constant.
        
        Parameters
        ----------
        Sy : bool, optional
            Enable (T) or disable (F).
        """
        if Sy:
            self.VI.write('SYNC 1')
        else:
            self.VI.write('SYNC 0')
            
    def setOscilatorFreq(self, freq):
        """Set the internal Oscilator Frequency.
        
        Parameters
        ----------
        freq : float
            Frequency.
        """
        fq = str(int(freq*1E3))
        self.VI.write('OF '+ fq)
        
    def setOscilatorAmp(self, amp):
        """Set the internal Oscilator Amplitude.
        
        Parameters
        ----------
        amp : float
            Amplitude.
        """
        A = str(int(amp*1E6))
        self.VI.write('OA '+ A)
        
    def setRefPhase(self, ph):
        """Set the phase reference.
        
        Parameters
        ----------
        ph : float
            Phase.
        """
        P = str(int(ph*1E3))
        self.VI.write('REFP '+ P)
        
    def getRefPhase(self):
        """Get the programed phase reference."""
        return self.__chkFloat(self.VI.query('REFP.'))
        
    def ConfigureInput(self, InDev = 'FET', Coupling = 'AC', Ground = 'GND', AcGain = 'Auto'):
        """
        Configure input parameters of device.
        
        Parameters
        ----------
        InDev : string, optional
            'FET', by default, or 'Bipolar'.
        Coupling : string, optional
            'AC', by default, or 'DC'.
        Ground : string, optional
            'GND', by default, or 'Float'.
        AcGain : string, optional
            'Auto', by default, or from '0' to '9'.
        """
        if InDev  == 'FET':
            self.VI.write('FET 1')
        elif InDev  == 'Bipolar':
            self.VI.write('FET 0')
        else:
            print('EG&G 7265 Lock-In Wrong Input device control Code')

        if Coupling  == 'DC':
            self.VI.write('CP 1')
        elif Coupling  == 'AC':
            self.VI.write('CP 0')
        else:
            print('EG&G 7265 Lock-In Wrong Input Coupling Code')

        if Ground  == 'GND':
            self.VI.write('FLOAT 0')
        elif Ground  == 'Float':
            self.VI.write('FLOAT 1')
        else:
            print('EG&G 7265 Lock-In Wrong Input Coupling Code')
            
        if AcGain == 'Auto':
            self.VI.write('AUTOMATIC 1')
        elif AcGain in map(str, range(10)):
            self.VI.write('AUTOMATIC 0')
            self.VI.write('ACGAIN ' + AcGain)
        else:
            print('EG&G 7265 Lock-In Wrong AcGain Code')
            
    def setXoff(self, Offset, Enable):
        """Sets the Offset in % on the X channel and toggles with Enable"""
        off_to_send=int(Offset*100)#rounds the offset in % to the integer to send
        if abs(off_to_send) > 300:
            raise ValueError("Offset out of 300% max range")
        elif Enable == True:
            self.VI.write('XOF 1 '+off_to_send)
        elif Enable == False:
            self.VI.write('XOF 0 '+off_to_send)
    
    def setYoff(self, Offset, Enable):
        """Sets the Offset in % on the Y channel and toggles with Enable"""
        off_to_send=int(Offset*100)#rounds the offset in % to the integer to send
        if abs(off_to_send) > 30000:
            raise ValueError("Offset out of 300% max range")
        elif Enable == True:
            self.VI.write('YOF 1 '+off_to_send)
        elif Enable == False:
            self.VI.write('YOF 0 '+off_to_send)
            
    def getXOff(self):
        """

        Returns
        -------
        A tuple of values n1,n2. n1= 0 or 1, whether or not the X-offset is enabled
        n2- the value of the offset in %*100

        """
        string_Off=self.VI.query('XOF')
        return(tuple(float(re.split(string_Off, ","))))#Test this.
    
    def getYOff(self):
        """

        Returns
        -------
        A tuple of values n1,n2. n1= 0 or 1, whether or not the y-offset is enabled
        n2- the value of the offset in %*100

        """
        string_Off=self.VI.query('YOF')
        return(tuple(float(re.split(string_Off, ","))))#Test this. 
    
    def Toggle_Offset(self, Toggle):
        """
        Toggle The Offsets on/off

        Parameters
        ----------
        Toggle : INT
            Offsets to turn on. Code:
                0 - Offset off
                1 - Offset X Channel
                2 - Offset Y Channel
                3 - Offset both X and Y


        """
        if abs(int(Toggle)) > 3:
            raise ValueError("Not a Valid Offset Input")
        else:
            if Toggle==0:
                self.VI.write('XOF 0')
                self.VI.write('YOF 0')
            elif Toggle==1:
                self.VI.write('XOF 1')
                self.VI.write('YOF 0')
                
            elif Toggle==2:
                self.VI.write('XOF 0')
                self.VI.write('YOF 1')
                
            elif Toggle==3:
                self.VI.write('XOF 1')
                self.VI.write('YOF 1')

   
        def setExp(self, Exp):
            """
            Set the expand of the lockin. Always x10.

            Parameters
            ----------
            Exp : INT
                Expand to turn on. Code:
                    0 - Expand off
                    1 - Expand X Channel
                    2 - Expand Y Channel
                    3 - Expand both X and Y


            """
            if abs(int(Exp)) > 3:
                raise ValueError("Not a Valid Expand Input")
            else:
                self.VI.write('EX '+abs(int(Exp)))
                
        def getExp(self):
            return(float(self.VI.query('EX')))
    @property
    def clear(self):
        #clears the Buffer
        self.VI.clear()        
    @property
    def X(self):
        """Returns X component of lock-in measure."""
        return self.__chkFloat(self.VI.query('X.'))
    @property
    def Y(self):
        """Returns Y component of lock-in measure."""
        return self.__chkFloat(self.VI.query('Y.'))
    @property
    def XY(self):
        """Returns XY component of lock-in measure."""
        return self.__chkFloatList(self.VI.query('XY.'))
    @property
    def Magnitude(self):
        """Returns Magnitude of lock-in measure."""
        return self.__chkFloat(self.VI.query('MAG.'))
    @property
    def X_PP(self):
        """Returns peak-peak X component of lock-in measure."""
        return (self.__chkFloat(self.VI.query('X.')))*root_two
    @property
    def Y_PP(self):
        """Returns peak-peak Y component of lock-in measure."""
        return (self.__chkFloat(self.VI.query('Y.')))*root_two
    @property
    def XY_PP(self):
        """Returns peak-peak XY component of lock-in measure."""
        return (self.__chkFloatList(self.VI.query('XY.')))*root_two#most likely to fall over
    @property
    def Magnitude_PP(self):
        """Returns peak-peak Magnitude of lock-in measure."""
        return (self.__chkFloat(self.VI.query('MAG.')))*root_two
    @property
    def Phase(self):
        """Returns Phase of lock-in measure."""
        return self.__chkFloat(self.VI.query('PHA.'))
    @property
    def Freq(self):
        """Returns Frequency of lock-in device."""
        return self.__chkFloat(self.VI.query('FRQ.'))