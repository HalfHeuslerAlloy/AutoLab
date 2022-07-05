# -*- coding: utf-8 -*-
"""
Created on Fri May 13 10:54:26 2022

@author: eenmv
"""

from time import sleep

class IPS120(object):
    
    def __init__(self, rm, channel):
        
        self.inst = rm.open_resource('GPIB0::'+str(channel)+'::INSTR')
        #Setup termination characters
        self.inst.write_termination = "\r"
        self.inst.read_termination = "\r"
        
        try:
            self.inst.clear()
            self.inst.clear()
            #Set to remote and unlocked
            self.inst.write("C3")
            sleep(0.1)
            #Set to extend high precesion return values
            self.inst.write("Q4")
            sleep(0.1)
            #Set display to tesla
            self.inst.write("M1")
            sleep(0.1)
        except:
            print("Failed comms and setup")
        
        self.inst.clear()
        
    
    def __del__(self):
        self.inst.close()
    
    def ExamineStatus(self):
        #Get Statues of machine
        self.inst.clear()
        
        for Try in range(5):
            #5 attempts to read the status of the instrument
            self.inst.clear()
            
            sleep(0.1)
            
            statusMessage = self.inst.query("X")
            
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
            self.Activity = "Ramping to Setpoint"
            
        elif self.ActivityStatus==2:
            self.Activity = "Ramping to Zero"
            
        elif self.ActivityStatus==3:
            self.Activity = "Clamped"
        
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
            self.is_SwitchHeaterON = False
            
        self.RemoteStatus = int(statusMessage[6])
        
        self.PolarityStatus = int(statusMessage[13:])
    
    
    def SwitchHeaterOff(self):
        self.inst.write("H0")
    
    def SwitchHeaterOn(self):
        self.inst.write("H2")
    
    
    def get_SweepRate(self):
        """Returns the field sweep rate
        """
        try:
            rate = self.inst.query("R 9")
            rate = float(rate)
        except:
            rate = None
        return rate
    
    def get_SetPoint(self):
        """Returns the set point
        """
        try:
            setP = self.inst.query("R 8")
            setP = float(setP)
        except:
            setP = None
        return setP
    
    def get_B(self):
        """Returns the current sweep rate
        """
        try:
            B = self.inst.query("R 7")
            B = float(B[1:])
        except Exception as e:
            print(e)
            print(B)
            B = None
        return B
    
    
    def set_SetPoint(self,B):
        self.inst.write("J{:.5f}".format(B))
        
    def set_FieldRate(self,Rate):
        """Sets the ramp rate of the magnet in Tesla/Min
        """
        self.inst.write("T{:.5f}".format(Rate))
    
    
    #set the activity of the IPS
    def sweep_Hold(self):
        self.inst.write("A0")
        
    def sweep_SetPoint(self):
        self.inst.write("A1")
        
    def sweep_ToZero(self):
        self.inst.write("A2")
    
    def sweep_Clamp(self):
        self.inst.write("A4")