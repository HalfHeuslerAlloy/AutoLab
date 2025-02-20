# -*- coding: utf-8 -*-
"""
Created on Fri May 13 10:54:26 2022

@author: eenmv
"""

from time import sleep
from Instruments.Instrument_class import Instrument

class IPS120(Instrument):
    
    def __init__(self, rm, channel):
        super().__init__(rm,channel)
        
        #Setup termination characters
        self.VI.write_termination = "\r"
        self.VI.read_termination = "\r"
        
        try:
            self.VI.clear()
            self.VI.clear()
            #Set to remote and unlocked
            self.Write("C3")
            sleep(0.1)
            #Set to extend high precesion return values
            self.Write("Q4")
            sleep(0.1)
            #Set display to tesla
            self.Write("M1")
            sleep(0.1)
        except:
            print("Failed comms and setup")
        
        self.VI.clear()
        
    
    def __del__(self):
        try:
            self.VI.close()
        except Exception as e:
            print(e)
            print("Failed to close, or never connected")
    
    def ExamineStatus(self):
        #Get Statues of machine
        self.VI.clear()
        
        for Try in range(5):
            #5 attempts to read the status of the instrument
            self.VI.clear()
            
            sleep(0.1)
            
            statusMessage = self.Query("X")
            
            if len(statusMessage)==15:
                break
        if len(statusMessage)!=15:
            raise Exception("Could not get status message from IPS120-10")
        #returns:
        #   XnmAnCnHnMmnPmn
        try:
            self.SystemStatus = int(statusMessage[1:3])
        except:
            print(statusMessage)
            self.SystemStatus = None
            
        try:
            self.ActivityStatus = int(statusMessage[4])
        except:
            print(statusMessage)
            self.ActivityStatus = None
        
        if self.ActivityStatus==0:
            self.Activity = "Hold"
            
        elif self.ActivityStatus==1:
            self.Activity = "Ramp to Setpoint"
            
        elif self.ActivityStatus==2:
            self.Activity = "Ramp to Zero"
            
        elif self.ActivityStatus==3:
            self.Activity = "Clamped"
        else:
            self.Activity = "unknown"
        
        self.ModeStatus_m = int(statusMessage[10])
        self.ModeStatus_n = int(statusMessage[11])
        
        if self.ModeStatus_n==0:
            self.Ramping = False
        else:
            self.Ramping = True
        
        self.SwitchHeaterStatus = int(statusMessage[8])
        
        if self.SwitchHeaterStatus==1:
            self.is_SwitchHeaterOn = True
        else:
            self.is_SwitchHeaterOn = False
            
        self.RemoteStatus = int(statusMessage[6])
        
        self.PolarityStatus = int(statusMessage[13:])
    
    
    def SwitchHeaterOff(self):
        self.Write("H0")
    
    def SwitchHeaterOn(self):
        self.Write("H2")
    
    
    def get_SweepRate(self):
        """Returns the field sweep rate
        """
        try:
            rate = self.Query("R 9")
            rate = float(rate)
        except:
            rate = None
        return rate
    
    def get_SetPoint(self):
        """Returns the set point
        """
        try:
            setB = self.Query("R 8")
            setB = float(setB[1:])
        except Exception as e:
            print(e)
            print(setB)
            setB = None
        return setB
    
    def get_B(self):
        """Returns the current sweep rate
        """
        try:
            B = self.Query("R 7")
            B = float(B[1:])
        except Exception as e:
            print(e)
            print(B)
            B = None
        return B
    
    
    def set_SetPoint(self,B):
        self.Write("J{:.5f}".format(B))
        
    def set_FieldRate(self,Rate):
        """Sets the ramp rate of the magnet in Tesla/Min
        """
        self.Write("T{:.5f}".format(Rate))
    
    
    #set the activity of the IPS
    def sweep_Hold(self):
        self.Write("A0")
        
    def sweep_SetPoint(self):
        self.Write("A1")
        
    def sweep_ToZero(self):
        self.Write("A2")
    
    def sweep_Clamp(self):
        self.Write("A4")