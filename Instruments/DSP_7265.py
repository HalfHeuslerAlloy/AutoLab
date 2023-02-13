import numpy as np

class DSP_7265(object):
    def __init__(self,rm, GPIB_Address, RemoteOnly = False):
        """
        Initializes the object as the 7265 Lock-in Amplifier.
        
        This class controls the DSP Lock-In Amplifier:
        EG&G Instruments, Model 7265 
        Should work with Signal Recovery 7265 DSP Lock-In
        
        Parameters
        ----------
        GPIB_Address : int, optional
            GPIB Address of device.
        RemoteOnly : bool, optional
            Control remotely (T) or not (F).
        """
        self.VI = rm.open_resource('GPIB0::' + str(GPIB_Address) + '::INSTR')
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
        s = [float(i) for i in s.split(",")]
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
                 '0'  = 10 us
                 '1'  = 20 us
                 '2'  = 40 us
                 '3'  = 80 us
                 '4'  = 160 us
                 '5'  = 320 us
                 '6'  = 640 us
                 '7'  = 5 ms
                 '8'  = 10 ms
                 '9'  = 20 ms
                 '10' = 50 ms
                 '11' = 100 ms
                 '12' = 200 ms
                 '13' = 500 ms
                 '14' = 1 s
                 '15' = 2 s
                 '16' = 5 s
                 '17' = 10 s
                 '18' = 20 s
                 '19' = 50 s
                 '20' = 100 s
                 '21' = 200 s
                 '22' = 500 s
                 '23' = 1 ks
                 '24' = 2 ks
                 '25' = 5 ks
                 '26' = 10 ks
                 '27' = 20 ks
                 '28' = 50 ks
                 '29' = 100 ks
                 '30' = 200 ks
                Values are rounded to corresponding code.
        
        Parameters
        ----------
        TC : float or string
            Float for time value or string for code.
        """
        if type(TC) != type(' '):
            TC = np.abs(TC) - 1E-9
            TC = np.clip(TC, 0, 199E3)
            bins = np.array([10E-6, 20E-6, 40E-6, 80E-6,
                                160E-6, 320E-6, 640E-6,
                                5E-3, 10E-3, 20E-3, 50E-3,
                                100E-3, 200E-3, 500E-3,
                                1, 2, 5, 10, 20, 50,
                                100, 200, 500,
                                1E3, 2E3, 5E3, 10E3, 20E3, 50E3,
                                100E3, 200E3])
            TC = str(len(bins[bins <= TC]))
        if TC in map(str, range(31)):
            self.VI.write('TC ' + TC)
        else:
            print('EG&G 7265 Lock-In Wrong Time Constant Code')
    def __getTC(self):
        return float(self.VI.query('TC.'))
    #TC. reads the time constant in seconds TC (no full stop) reads the corresponding code
    TC = property(__getTC, setTC, None, "Filter Time Constant.")
    
    def setSEN(self, vSen):
        """ Sets the Full Scale Sensitivity.
        
        Usage :
            setTC(Value or Code)
                Codes : IMODE=0 IMODE=1 IMODE=2
                 '1'  = 2 nV    2 fA    n/a
                 '2'  = 5 nV    5 fA    n/a
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
            bins = np.array([0, 2E-15, 5E-15, 10E-15, 20E-15, 
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
    #SEN. reads the senitivity in the relevant unit, based on the Input mode
    #SEN (no full stop) reads the corresponding code
    SEN = property(__getSEN, setSEN, None, "Full Scale Sensitivity.")
    
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
        return(tuple(self.VI.query('XOF')))
    
    def getYOff(self):
        """

        Returns
        -------
        A tuple of values n1,n2. n1= 0 or 1, whether or not the y-offset is enabled
        n2- the value of the offset in %*100

        """
        return(tuple(self.VI.query('YOF')))
   
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
        return(self.VI.query('EX'))        
        
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
    def Phase(self):
        """Returns Phase of lock-in measure."""
        return self.__chkFloat(self.VI.query('PHA.'))
    @property
    def Freq(self):
        """Returns Frequency of lock-in device."""
        return self.__chkFloat(self.VI.query('FRQ.'))