# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 11:42:47 2022

@author: eenmv
"""

import time
from Instruments.Instrument_class import Instrument

class SMS120C(Instrument):
    def __init__(self,rm,Channel):
        """
        try to connect to the SMS120C over serial
        """
        super().__init__(rm,Channel,GPIB=False)
        self.tpa=""
        message = self.Query("R S")
        if message == '':
            print("ERROR: No message received, check SMS is in remote mode")
            raise
        
        self.update()
    
    def update(self):
        """
        general get status of system
        """
        try:
            self.VI.clear()
            
            self.Write("U")
            
            #Remote status
            mess = self.Read()
            
            #External trip status
            mess = self.Read()
            
            #Field Constant status
            mess = self.Read()
            self.TPA = float(mess.split(" ")[3])
            
            #Heater output voltage setting status
            mess = self.Read()
            
            #Voltage limit status
            mess = self.Read()
            
            #Ramp rate status
            mess = self.Read()
            self.RampRate = float(mess.split(" ")[3])
            
            #MID setpoint status
            mess = self.Read()
            self.MID = float(mess.split(" ")[3])
            
            #MAX setpoint status
            mess = self.Read()
            self.MAX = float(mess.split(" ")[3])
            
            #Heater status
            mess = self.Read()
            self.HeaterStatus = mess.split(" ")[3][:-2]
            
            #Pause status
            mess = self.Read()
            
            #Ramp state status
            mess = self.Read()
            self.RampStatus = mess.split(" ")[3]
            
            #level guage
            mess = self.Read()
            
            #Current B Output
            mess = self.Read()
            self.B = float(mess.split(" ")[2])
            
            self.VI.clear()
            
            self.Direction = self.get_sign()
            
        except Exception as e:
            print(e)
        
    def get_output(self):
        """
        Get current output
        """
        try:
            message = self.Query("G O")
            split = message.split(" ")
            B = float(split[1])
        except Exception as e:
            print(e)
            B = None
        
        return B
    
    def get_level(self):
        """
        No helium level sensot
        """
        return None
#        self.Write("G L\r\n")
#        time.sleep(0.3) #it takes more than 0.5 seconds to read the entire update message.
#        message=self.Read()
#        split = message.split(" ")
#        return split[2]
    
    def get_ramp_status(self):
        """
        Return text string of current ramp status
        Either: ["RAMPING","HOLDING","QUENCH","EXTERNAL"]
        """
        message = self.Query("R S")
        split = message.split(" ")
        return split[3]
    
    def get_mid_ramp(self):
        """
        Get current mid setpoint
        """
        try:
            message = self.Query("G %")
            split = message.split(" ")
            B = float(split[3])
        except Exception as e:
            print(e)
            B = None
        
        return B
    
    def get_max_ramp(self):
        """
        Get current max setpoint
        """
        try:
            message = self.Query("G !")
            split = message.split(" ")
            B = float(split[3])
        except Exception as e:
            print(e)
            B = None
        
        return B
        
    def get_TPA(self):
        """
        Get field to current constant
        """
        try:
            message = self.Query("G T")
            split = message.split(" ")
            TPA = float(split[3])
        except Exception as e:
            print(e)
            TPA = None
        
        return TPA
        
    def get_sign(self):
        """
        Get Sign of magnetic field
        Either:  POSITIVE or NEGATIVE
        """
        try:
            message = self.Query("G S")
            split = message.split(" ")
            Dir = split[2][:-2]
        except Exception as e:
            print(e)
            Dir = None
        
        return Dir
        
    def ramp_to_zero(self):
        "Ramp to zero field"
        self.Write("R 0")
    
    def ramp_to_MID(self):
        "Ramp to mid field"
        self.Write("R %")
    
    def ramp_to_MAX(self):
        "Ramp to max field"
        self.Write("R !") 
    
    def toggle_pause(self,paused):
        """
        paused the current sweep
        """
        if paused == True:
            self.Write("P 1") 
        elif paused == False:
            self.Write("P 0")
        self.VI.clear()
    
    def toggle_heater(self,heating):
        """
        Turns on/off heater
        """
        
        if heating:
            print("Turning heater on")
            self.Query("H 1")
        else:
            print("Turning heater off")
            self.Query("H 0")
        self.VI.clear()
    
    def toggle_tesla(self,tesla):
        """
        Change front panel units
        """
        if tesla == True:
            self.Write("T 1") 
        elif tesla == False:
            self.Write("T 0")
        time.sleep(0.1)
        self.VI.clear()
    
    def toggle_direction(self,direction):
        if direction in ["+","-"]:
            try:
                self.Write("D "+direction)
            except Exception as e:
                print(e)
                self.VI.clear()
        else:
            print("exp")
    
    def set_mid(self, field):
        try:
            message = self.Query("S % {:.3f}".format(field))
            split = message.split(" ")
            if field-0.001 <float(split[3])< field+0.001:
                print("Warning: Mid field may not be set correctly")
        except Exception as e:
            print(e)
    
    def set_max(self, field):
        self.Query("S ! {:.3f}".format(field))
        self.VI.clear()
    
    def set_ramp(self,ramp_rate):
        #rate in amps/hour
        self.Query("S R {:.3f}".format(ramp_rate))
        self.VI.clear()
    
#    def set_limit(self,limit):
#        #limit in volts
#        self.sms.write("S L "+limit+"\r\n")
    
#    def set_heater(self,heater):
#        #heater value in volts
#        self.sms.write("S H "+heater+"\r\n")
#    
#    def set_TPA(self,tesla_per_amp):
#        self.sms.write("S R "+tesla_per_amp+"\r\n")
        
    def close(self):
        self.VI.close()
    
    # def programmable_Sweep(self,breakpoints,rates):
    #     """
    #     Sets up a multiple point magnet sweep between a list of break-points at defined rates
    #     Starts a new thread to handle the magnet. TO DO: Work syncing this to the Measurement

    #     Parameters
    #     ----------
    #     breakpoints : Array-Like
    #         Array/List of Break-points
    #     rates : TYPE
    #        List of rates of the Same size as breakpoints

    #     Returns
    #     -------
    #     None.

    #     """
