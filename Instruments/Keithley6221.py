# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 14:31:27 2024

@author: eencsk
Driver for the 6221, Also controls the 2182.
"""
import re
from time import sleep

class Keithley6221(object):
    
    def __init__(self, rm, GPIB_Address):
        """
        Initializes the object as the 6221.
        
        This class controls the Keithley 6221
        
        Parameters
        ----------
        rm: Pyvisa resource Manager being used 
        GPIB_Address : int or string
            GPIB Address of device. An Int assumes that this is a channel on GPIB0.
            Much of the syntax should be the same for Ethernet or RS232 butI'm assuming GPIB

        """
        if type(GPIB_Address) != type(" "):
            self.VI = rm.open_resource('GPIB0::' + str(GPIB_Address) + '::INSTR')
        else:
            self.VI = rm.open_resource(GPIB_Address)
        
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF#set up the read/write terminations
        #LF=/n Works on NIMAX so... no need to change it?
        self.status=self.VI.query("*STB?")
        #set up a reading of the status register and populate it from the start. 
        #TODO: add Handling here for particularly fatal errors.
        
            
    def __del__(self):#call to close the class
        self.VI.close()
    
    def clear_status(self):
        self.VI.write("*CLS")
        
    def get_status(self):
        #get the status byte
        return(self.status)
    
    def update_status(self):
        #update status byte and return
        self.status=self.VI.query("*STB?")
        return(self.status)

# =============================================================================
# WAVE MODE COMMANDS FOR USE WITH LOCKINS
# =============================================================================
    
    def set_WaveFunc(self,Function):
        """
        Set the Wavefunction for wave mode

        Parameters
        ----------
        Function : String
            Which wavefunc to use. Sine (SIN),Square (SQU), Ramp(RAMP) 
        """
        if re.search("SIN",Function):
            self.VI.write("SOUR:WAVE:FUNC SIN")
        elif re.search("SQU",Function):
            self.VI.write("SOUR:WAVE:FUNC SQU")
        elif re.search("RAMP",Function):
            self.VI.write("SOUR:WAVE:FUNC RAMP")
        else:
            raise KeyError("Invalid WaveFunction Sent")
            self.__del__()
        
    def WaveDuty(self,Duty_Cycle=None):
        """
        Set or get the Wave Mode Duty Cycle
        Note: If an invalid type is sent, it will be parsed as a "get" command.

        Parameters
        ----------
        Duty_Cycle : Int, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        Duty cycle if none-sent

        """
        try:
            Duty=int(Duty_Cycle)
            if 0<=Duty<=100:
                self.VI.write("SOUR:WAVE:DCYC {:d}".format(Duty))
            else:
                raise ValueError("Invalid Duty Cycle, Saw {:d}".format(Duty))
            return()
        except TypeError:
            Duty=self.VI.query("SOUR:WAVE:DCYC?")
            return(Duty)

    def WaveFrequency(self,Frequency=None):
        """
        Set or get the Wave Mode Frequency. 
        Note: If an invalid type is sent, it will be parsed as a "get" command.

        Parameters
        ----------
        Frequency : Float, optional
            Frequency should be between 1E-3 to 1E5.
            If none is sent acts as a Get command
            The default is None.

        Returns
        -------
        Frequency in Hz if nothing sent

        """
        try:
            Freq=float(Frequency)
            if 1E-3<=Freq<=1E5:
                self.VI.write("SOUR:WAVE:FREQ {}".format(Freq))
            else:
                raise ValueError("Invalid 6221 Frequency, Saw {}".format(Freq))
            return()
        except TypeError:
            Freq=self.VI.query("SOUR:WAVE:FREQ?")
            return(Freq)

    def WaveAmp(self,Amplitude=None):
        """
        Set or get the Wave Mode Amplitude. 
        Note: If an invalid type is sent, it will be parsed as a "get" command.

        Parameters
        ----------
        Amplitude : Float, optional
            Amplitude in amps should be between 2E-12 to 1E-1.
            If none is sent acts as a Get command
            The default is None.

        Returns
        -------
        Amplitude in amps if nothing sent

        """
        try:
            Amp=float(Amplitude)
            if 2E-12<=Amp<=1E-1:
                self.VI.write("SOUR:WAVE:AMPL {}".format(Amp))
            else:
                raise ValueError("Invalid 6221 Amplitude, Saw {}".format(Amp))
            return()
        except TypeError:
            Amp=self.VI.query("SOUR:WAVE:AMPL?")
            return(Amp)
    
    def Ref_Phase(self, Phase=None):
        """
        Set or get the Wave Mode Reference Phase. 
        Note: If an invalid type is sent, it will be parsed as a "get" command.

        Parameters
        ----------
        Phase : Float, optional
            Amplitude in amps should be between 0 to 360.
            If none is sent acts as a Get command
            The default is None.

        Returns
        -------
        Phase in Degrees if nothing sent

        """
        try:
            Ph=float(Phase)
            if 0<=Ph<=360:
                self.VI.write("SOUR:WAVE:PMAR {}".format(Ph))
            else:
                raise ValueError("Invalid 6221 Reference Phase, Saw {}".format(Ph))
            return()
        except TypeError:
            Ph=self.VI.query("SOUR:WAVE:PMAR?")
            return(Ph)
    
    def Conf_Ref_Trigger(self, Trigger_Channel=None):
        """
        Set and Enable/Disable the Trigger Channel.
        Again, not passing a number will return the Approprate channel

        Parameters
        ----------
        Trigger_Channel : Int, optional
            Trigger channel to use; 1-6. A value of 0 will disable the phase marker. The default is None.

        Returns
        -------
        Trigger channel in use.
        TODO: Test what happens when the trigger channel is disabled

        """
        try:
            Trigger=int(Trigger_Channel)
            if 0<Trigger<=6:
                self.VI.write("SOUR:WAVE:PMAR:OLIN {:d}".format(Trigger))
                self.VI.write("SOUR:WAVE:PMAR:STAT ON")
            elif Trigger==0:#0 is not a valid channel, but it makes a nice "Off" shorthand
                self.VI.write("SOUR:WAVE:PMAR:STAT OFF")
            else:
                raise ValueError("Invalid 6221 Waveform Trigger Channel, Saw {}".format(Trigger))
            return()
        except TypeError:
            Trigger=self.VI.query("SOUR:WAVE:PMAR:OLIN?")
            return(Trigger)
        
    def Wave_Offset(self, Offset=None):
        """
        Set oir get the waveform offset.
        Once again, No parameter makes it get the current offset

        Parameters
        ----------
        Offset : Float, optional
            DC offset applied to the AC wave, between +/-0.1 amps. The default is None.

        Returns
        -------
        DC offset in amps

        """
        try:
            Off=int(Offset)
            if -0.1<Off<=0.1:
                self.VI.write("SOUR:WAVE:OFFS {}".format(Off))
            else:
                raise ValueError("Invalid 6221 Waveform Offset, Saw {}".format(Off))
            return()
        except TypeError:
            Offs=self.VI.query("SOUR:WAVE:OFFS?")
            return(Offs)
        
    def Start_Wave(self):
        """
        Arms and Starts the Configured Wave-Mode

        Returns
        -------
        None.

        """
        self.VI.write("SOUR:WAVE:ARM")
        sleep(0.1)#Let the Source go through with the arm command. 
        #PROBABLY unnecessary but better than spamming commands at the speed of CPU
        self.VI.write("SOUR:WAVE:INIT")#starts the wave
        return()
    
    def Abort_Wave(self):
        """
        Stops the Wave-Mode output

        Returns
        -------
        None.

        """
        self.VI.write("SOUR:WAVE:ABOR")
        return()
# =============================================================================
# SWEEP MODE PARAMETERS    
# =============================================================================
    def set_Sweep(self,list_currents=[]):
        """
        Sets or gets the Current Sweep from a list of current values

        Parameters
        ----------
        list_currents : array-like
            List of currents, has to be in the range it works at.

        Returns
        -------
        If no list supplied, returns a Tuple of
        Length 2 of Points,Current Lists.

        """
        if len(list_currents) !=0 :
            out_current=str()
            for current in list_currents:
                try:
                    current=float(current)#check that its a float
                    if abs(current) < 0.1:
                        out_current=out_current+(", {}").format(current)
                    else:
                        raise ValueError("Invalid 6221 DC current, saw {}").format(current)
                except ValueError as e:
                    raise e
                    return()
                out_current=out_current[1:]#as the first point has that comma, trim.
                message="SOUR:LIST:CURR"+out_current
                self.VI.write(message)
                return()
        else:
            points=self.VI.query("SOUR:LIST:POIN?")
            currents=self.VI.query("SOUR:LIST:CURR?")
            return(tuple(points,currents))
    
    def get_Data(self):
        """
        Returns the Data within the 2182.

        """
        return(self.VI.query("SENS:DATA"))