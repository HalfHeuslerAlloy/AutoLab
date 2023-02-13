# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 11:42:47 2022

@author: eenmv
"""

import time

class SMS120C:
    def __init__(self,rm,Channel):
        """
        try to connect to the SMS120C over serial
        """
        self.inst = rm.open_resource('COM'+str(Channel))
        self.tpa=""
        message = self.inst.query("R S")
        if message == '':
            print("ERROR: No message received, check SMS is in remote mode")
            raise
        
        self.update()
    
    def update(self):
        """
        general get status of system
        """
        try:
            self.inst.clear()
            
            self.inst.write("U")
            
            #Remote status
            mess = self.inst.read()
            
            #External trip status
            mess = self.inst.read()
            
            #Field Constant status
            mess = self.inst.read()
            self.TPA = float(mess.split(" ")[3])
            
            #Heater output voltage setting status
            mess = self.inst.read()
            
            #Voltage limit status
            mess = self.inst.read()
            
            #Ramp rate status
            mess = self.inst.read()
            self.RampRate = float(mess.split(" ")[3])
            
            #MID setpoint status
            mess = self.inst.read()
            self.MID = float(mess.split(" ")[3])
            
            #MAX setpoint status
            mess = self.inst.read()
            self.MAX = float(mess.split(" ")[3])
            
            #Heater status
            mess = self.inst.read()
            self.HeaterStatus = mess.split(" ")[3][:-2]
            
            #Pause status
            mess = self.inst.read()
            
            #Ramp state status
            mess = self.inst.read()
            self.RampStatus = mess.split(" ")[3]
            
            #level guage
            mess = self.inst.read()
            
            #Current B Output
            mess = self.inst.read()
            self.B = float(mess.split(" ")[2])
            
            self.inst.clear()
            
            self.Direction = self.get_sign()
            
        except Exception as e:
            print(e)
        
    def get_output(self):
        """
        Get current output
        """
        try:
            message = self.inst.query("G O")
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
#        self.inst.write("G L\r\n")
#        time.sleep(0.3) #it takes more than 0.5 seconds to read the entire update message.
#        message=self.inst.read()
#        split = message.split(" ")
#        return split[2]
    
    def get_ramp_status(self):
        """
        Return text string of current ramp status
        Either: ["RAMPING","HOLDING","QUENCH","EXTERNAL"]
        """
        message = self.inst.query("R S")
        split = message.split(" ")
        return split[3]
    
    def get_mid_ramp(self):
        """
        Get current mid setpoint
        """
        try:
            message = self.inst.query("G %")
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
            message = self.inst.query("G !")
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
            message = self.inst.query("G T")
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
            message = self.inst.query("G S")
            split = message.split(" ")
            Dir = split[2][:-2]
        except Exception as e:
            print(e)
            Dir = None
        
        return Dir
        
    def ramp_to_zero(self):
        "Ramp to zero field"
        self.inst.write("R 0")
    
    def ramp_to_MID(self):
        "Ramp to mid field"
        self.inst.write("R %")
    
    def ramp_to_MAX(self):
        "Ramp to max field"
        self.inst.write("R !") 
    
    def toggle_pause(self,paused):
        """
        paused the current sweep
        """
        if paused == True:
            self.inst.write("P 1") 
        elif paused == False:
            self.inst.write("P 0")
        self.inst.clear()
    
    def toggle_heater(self,heating):
        """
        Turns on/off heater
        """
        
        if heating:
            print("Turning heater on")
            self.inst.query("H 1")
        else:
            print("Turning heater off")
            self.inst.query("H 0")
        self.inst.clear()
    
    def toggle_tesla(self,tesla):
        """
        Change front panel units
        """
        if tesla == True:
            self.inst.write("T 1") 
        elif tesla == False:
            self.inst.write("T 0")
        time.sleep(0.1)
        self.inst.clear()
    
    def toggle_direction(self,direction):
        if direction in ["+","-"]:
            try:
                self.inst.write("D "+direction)
            except Exception as e:
                print(e)
                self.inst.clear()
        else:
            print("exp")
    
    def set_mid(self, field):
        try:
            message = self.inst.query("S % {:.3f}".format(field))
            split = message.split(" ")
            if field-0.001 <float(split[3])< field+0.001:
                print("Warning: Mid field may not be set correctly")
        except Exception as e:
            print(e)
    
    def set_max(self, field):
        self.inst.query("S ! {:.3f}".format(field))
        self.inst.clear()
    
    def set_ramp(self,ramp_rate):
        #rate in amps/hour
        self.inst.query("S R {:.3f}".format(ramp_rate))
        self.inst.clear()
    
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
        self.inst.close()