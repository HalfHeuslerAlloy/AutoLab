# -*- coding: utf-8 -*-
"""
Created on Tue Jul  8 15:27:09 2025

@author: csk42
Driver for the Keithley 236 SMU
"""

import re
from Instruments.Instrument_class import Instrument
import time
import numpy as np
from math import log10, fmod #only import functions we need


class Keithley236(Instrument):
    modelist=["F0,0X","F0,1X","F1,0X","F1,1X"]
    # List of Change Mode operators. In order;
    # Source Voltage DC, Source Voltage Sweep, Source Current DC, Source Current Sweep
    def __init__(self, rm,address,mode=0):
        """
        Initialises the Keithley236

        Parameters
        ----------
        rm : pyvisa.Resource Manager
            Resource Manager responsible for Handling the Instrument
        address : Int or Str
            Comms address for the instrument
            Int will parse as a GPIB adress, or String as an address from
            pyvisa.list_resources
        mode: Int
            Mode that the Keithley is initialised in. Defaults to Source Voltage measure Current, DC.
            

        Returns
        -------
        None.

        """
        super().__init__(rm,address)
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF
        self.Mode=mode#here so that we can set ranges and compliances accordingly
        self.Write(self.modelist[self.Mode])
        
        
    def set_Compliance(self,value,Source_Range):
        """
        Sets the compliance and measurement Range for the source

        Parameters
        ----------
        value : Float
            The compliance value Current is between pm 100mA
            Voltage is between pm 110 V
        Range : Int
            Index on a list for the Source channel
            Index,Current/Voltage
            0=Auto/Auto
            1=1nA/1.1V
            2=10nA/11V
            3-100nA/110V
            4=1uA/NA
            5=10uA/NA
            6=100uA/NA
            7=1mA/NA
            8=10mA/NA
            9=100mA/NA            

        """
        try:
            value=float(value)
            Source_Range=int(Source_Range)
        except ValueError:
            raise Exception("Values in Set_Compliance could not be passed as Numbers!")
        if self.Mode>=1:
            #Source I mode
            if abs(value)>110 or Source_Range>4:
                raise ValueError("Invalid Voltage compliance! Expected a number less than pm 110 and a range less than 4, got {0} and {1}".format(value,Source_Range))
            else:
                value=str(value)
                Source_Range=str(Source_Range)
                self.write("L"+value+","+Source_Range+"X")
                return()
        else:
            #source V mode
            if abs(value)>0.1 or Source_Range>9:
                raise ValueError("Invalid Current compliance! Expected a number less than pm 0.1 and a range less than 9, got {0} and {1}".format(value,Source_Range))
            else:
                value=str(value)
                Source_Range=str(Source_Range)
                self.write("L"+value+","+Source_Range+"X")
                return()
    
    def Change_Mode(self,NewMode):
        """
        Change the output mode of the 236. Here mostly for set-dressing. You really should be setting the mode at __init__
        
        Parameters
        ----------
        NewMode : Int between 0 and 3
            Corresponds to the command in self.modelist
            0=Source Voltage DC
            1=Source Voltage Sweep
            2=Source Current DC
            3=Source Current Sweep

        Returns
        -------
        None.

        """
        NewMode=int(NewMode)
        if NewMode==self.Mode:
            print("Identical Mode Detected!")#Bugfixing Code Fragment. Delete once tested.
            return()#I'm not doing anything if you just want to select the same mode over and over
        else:
            self.Mode=NewMode
            self.Write(self.modelist[self.Mode])
            return()
    
    def set_Bias(self,Bias,Source_Range=0,Delay=0):
        """
        Set the DC Bias, which is either the Standby level for the Sweep Fn
        Or the Output for the DC fn. 
        
        NOTE: When setting the bias the output will turn on and be at the OLD
        Bias level for 10 ms prior to changing the bias. Proper compliance should
        mean this isnt an issue. But to be sure make sure bias is set to 0 on start
        
        Parameters
        ----------
        Bias : Float
            Bias to be applied. Between pm 1 mA or pm 110 V depending on mode
        Source_Range : Int, optional
            Index on a list for the Source channel
            Index,Current/Voltage
            0=Auto/Auto DEFAULT
            1=1nA/1.1V
            2=10nA/11V
            3-100nA/110V
            4=1uA/NA
            5=10uA/NA
            6=100uA/NA
            7=1mA/NA
            8=10mA/NA
            9=100mA/NA     
        Delay : int, optional
            Time in ms to delay output. The default is 0.

        """
        try:
            Delay=int(Delay)
        except ValueError:
            raise Exception("K236 Delay could not be parsed as int! Got {}".format(Delay))
        
        if self.Mode<=1:
            #Source V mode
            if abs(Bias)>110 or Source_Range>4:
                raise Exception("Invalid Voltage Bias! Expected a number less than pm 110 and a range less than 4, got {0} and {1}".format(Bias,Source_Range))
            else:
                if Source_Range>0 and abs(Bias)>(1.1*(10**(Source_Range-1))):
                    raise Exception("Voltage Source Overrange! Range index={0}, Bias Supplied={1}".format(Source_Range,Bias))
                else:
                    self.Write(("B{0},{1},{2}X").format(Bias,Source_Range,Delay))
                    return()
        else:
            #Source I Mode
            if abs(Bias)>0.1 or Source_Range>9:
                raise Exception("Invalid Current Bias! Expected a number less than pm 0.1 and a range less than 9, got {0} and {1}".format(Bias,Source_Range))
            
            else:
                if Source_Range>0 and abs(Bias)>(10**(Source_Range-10)):
                    raise Exception("Current Bias overrange! Max current={}, Bias Requested={}".format((10**(Source_Range-10)),Bias))
                else:
                    self.Write(("B{0},{1},{2}X").format(Bias,Source_Range,Delay))
                    return()
    
    def data_Format(self, lines, items=4,form=1):
        """
        Set the Format of data Returned from the K236
        As lines is the one most likely to change, (between sweep and DC), 
        Everything else is set to something I think will be useful. 
        THINK this is your "Get Data" Function?
        
        Parameters
        ----------
        lines : Int, 0-2
            Number of lines per output:
                0 = One line of dc data per talk
                1 = One line of sweep data per talk
                2 = All lines of sweep data per talk 
        items : INT, optional
            items - Sum of items in IEEE output string:
                O=Noitems
                1 = Source value
                2 = Delay value
                4 = Measure value
                8 =Time value  The default is 4.
        form : INT, optional
            Format of IEEE output string:
                0 = ASCll data with prefix and suffix
                1 = ASCll data with prefix, no suffix
                2 = ASCll data, no prefix or suffix
                3 = HP binary data
                4 = IBM binary data The default is 1.

        Returns
        -------
        None.

        """
        if lines not in (0,1,2) or items not in (1,2,4,8) or form not in (0,1,2,3,4):
            raise Exception("Invalid Keithley236 Dataformat Lines has to be 0,1 or 2, Items 0,1,2,4,8 and form an Int less than 5")
        else:
            lines=int(lines)
            items=int(items)
            form=int(form)
            self.Query("G{},{},{}X".format(items,form,lines))
            
    def set_Trigger(self,Origin=3,In=0,Out=0,End=1):
        """
        Set the trigger for the Keithley 236. Seems mainly to do with Sweep operation
        NB: Does not ENABLE the trigger, only sets when and where it should send/waitfor a trigger pulse

        Parameters
        ----------
        Origin : Int, optional
            O=IEEEX
            1 =IEEE GET
            2=1EEETalk
            3 = External (TRIGGER IN pulse)
            4 =Immediate only (front panel MANUAL key or HOX command). The default is 3.
        In : Int, optional
            in - Specifies the effect of an input trigger:
            0 =Continuous (no trigger needed to continue S-D-M cycles)
            1 = "SRC DLY MSR (trigger starts source phase)
            2 = SRC,.DLY MSR (trigger starts delay phase)
            3 = "SRC,.DLY MSR
            4 = SRC DL Y "MSR (trigger starts measure phase)
            5 = "SRC DLY,.MSR
            6 = SRC·.OLY "MSR
            7 = "SRC,.DLY,.MSR
            8 = "Single pulse . The default is 0.
        Out : Int, optional
            out- Specifies when an output trigger is generated:
            0 =None during sweep
            1 = SRC,.DLY MSR (end of source phase)
            2 = SRC DLY,.MSR (end of delay phase)
            3 = SRC,.DLY,.MSR
            4 = SRC DLY MSR" (end of measure phase)
            5 = SRC,.DLY MSR"
            6 = SRC DLY,.MSR"
            7 = SRC,.DLY "MSR"
            8 = Pulse end"
             The default is 0.
        End : Int, optional
            end -Sweep End" trigger out:
            0= Disabled
            1 =Enabled. The default is 1.

        Returns
        -------
        None.

        """
        if Origin not in range(0,5) or In not in range(0,8) or Out not in range(0,8) or End not in (0,1) :
            raise Exception("Invalid Trigger Configuration for 236")
        else:
            self.Write("T{},{},{},{}X".format(Origin,In,Out,End))
    
    def set_IntTime(self,Option):
        """
        Sets the integration time for the measurement channel. From experience, 1 line cycle (Option=3) is best.

        Parameters
        ----------
        Option : Int
            Sets the Integration time as;
            0 416usec
            1 4msec 
            2 16.67msec Line Cycle (60Hz) 5-digit
            3 20msec Line Cycle (50Hz)

        Returns
        -------
        None.

        """
        if Option not in range(0,4):
            raise Exception("Invalid Integration time, Must be an Int from 0-3!")
        else:
            self.Write("S{}X".format(int(Option)))
            
    def set_sweep(self, sweep_list,delay=0,DPP=1):
        """
        Programs a sweep from an array of levels 
        NB: Assumes Mode is already set and calculates ranges accordingly
        
        Uses the "Fixed Level" sweep option and appends the points
        to the list. This should allow you to create an arbitrary IV characteristics
        TODO: Test that this works and doesnt flick the output all over the place.
        Also test if we need a Time.Sleep between all Sweep points.

        Parameters
        ----------
        sweep_list : Array-like
            List of datapoints to do sweep. Max 1000
        delay : Array-like of Ints or Int, optional
            Delay before taking a measurement in ms. If an array must be the same Len as sweep_list,
            which will then apply that point-wise. If Int, sets it for all points. The default is 0
        DPP : Int, optional
            Data-Per-Point. How many datapoints will be taken at each sweep step. Assumed constant throughout sweep The default is 1.

        Returns
        -------
        None 

        """
        sweep_list=np.array(sweep_list,dtype=float)#convert to nparray for reason. should throw a valueerror if a non-number is passed
        delay=np.array(delay,dtype=int)#force delay into int and make it so we can np.size() it.
        sweep_size=np.size(sweep_list)
        if np.size(delay)==1:
            delay=np.full(sweep_size,delay)#create array full of the delay value
        elif np.size(delay) != sweep_size:
            raise ValueError("Sweep and Delay Must be the same size if Arrays! Sweep_Size={}, Delay_size={}".format(sweep_size,np.size(delay)))
            
        range_test=np.max(abs(sweep_list))#first find appropiate range  
        if self.Mode==1:
            if range_test < 110:#make sure voltages are in-range
                range_test=divmod(log10(range_test),1)#gets appropriate power of 10
                if range_test[1]<0.04:#case where we're less than 1.1 times pow10
                    Source_Range=int(range_test[0])+1
                else:#case where we're more than 1.1xpow10
                    Source_Range=int(range_test[0])+2
            else:
                raise ValueError("Voltage overrange! Max voltage is pm 110 V!")
        elif self.Mode==3:
            if range_test < 0.1:
                Source_Range=10+int(log10(range_test))#it just works
            else:
                raise ValueError("Current Overrange! Max current is 100 mA!")
        else:
            raise ValueError("Wrong Mode Detected! Must be Either 1 (Voltage Source) or 3 (Current Source) Current Mode={}".format(self.Mode))           
            
            
# =============================================================================
#             START ACTUALLY WRITING THE SWEEP
# =============================================================================
        self.Write("Q0,{},{},{},{}X".format(sweep_list[0],Source_Range,delay[0],DPP))#create list.
        for x in range(1,sweep_list.size()):
            self.Write("Q6,{},{},{},{}X".format(sweep_list[0],Source_Range,delay[0],DPP))#append points to list. Unsure if we need X on every line here.
            
        
    def enable_Trigger(self,Enable=True):
        """
        Enables or Disables the Trigger Sending/Receiving

        Parameters
        ----------
        Enable : Bool, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None.

        """
        if Enable ==True:
            self.Write("R1X")
        elif Enable ==False:
            self.Write("R0X")
        else:
            raise Exception("K236 Trigger enable not a Bool! Trigger Unchanged!")
    
    def Operate (self,Enable):
        """
        Enables or Disables the Output

        Parameters
        ----------
        Enable : Bool, 
            Whether to enable the output of the K236

        Returns
        -------
        None.

        """
        if Enable ==True:
            self.Write("N1X")
        elif Enable ==False:
            self.Write("N0X")
        else:
            raise Exception("K236 Output enable not a Bool! Output Unchanged!")
            
    def Trigger(self):
        """
        Immediately sends a Trigger pulse to the K236

        Returns
        -------
        None.

        """
        self.Write("H0X")
    
    