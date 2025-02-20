# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 16:02:22 2022

@author: eenmv
"""

import os 
print(os.getcwd())

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import font as tkFont

import time
import pyvisa

try:
    import Instruments as Inst
except:
    pass


class Util(tk.Frame):
    """
    Test utility function
    """
    
    #Name of utility so it can e refer to later as part of a dictionary
    name = "Arroyo"
    
    statusTemplate = """Freq. (Hz) : {}
Duty  (%) : {}
Current (mA) : {}
Power (W) : {}
Output : {}"""
    
    statParam = [None,None,None,None,None]
    
    def __init__(self, master,parent=None):
        
        super().__init__(master)
        
        frame = tk.Frame(master)
        
        master.add(frame,text="Arroyo Control")
        
        self.connected = False
        self.Arroyo = None
        
        
        gbipLabel = tk.Label(frame,text="COM Port")
        gbipLabel.grid(column=0, row=0)
        self.ComEntry = tk.Entry(frame,width = 10)
        self.ComEntry.insert(tk.END,"6")
        self.ComEntry.grid(column=0, row=1)
        
        self.ConnStatusLabel = tk.Label(frame,text="Disconnect",bg = "red")
        self.ConnStatusLabel.grid(column=0, row=2)
        
        self.ConnectButton = tk.Button(frame,
                                         text = "Connect",
                                         command = self.Connect,
                                         )
        self.ConnectButton.grid(column = 1, row = 0)
        
        
        self.DisconnectButton = tk.Button(frame,
                                         text = "Disconnect",
                                         command = self.Disconnect,
                                         )
        self.DisconnectButton.grid(column = 1, row = 1)
        
        self.StatusButton = tk.Button(frame,
                                         text = "Status",
                                         command = self.Status,
                                         )
        self.StatusButton.grid(column = 1, row = 2)
        
        
        #set frequency
        
        FreqLabel = tk.Label(frame,text="Freq. (Hz)")
        FreqLabel.grid(column = 2, row = 0)
        
        self.FreqEntry = tk.Entry(frame,width = 10)
        self.FreqEntry.insert(tk.END,"227")
        self.FreqEntry.grid(column=2, row=1)
        
        
        #set duty cycle
        
        DutyLabel = tk.Label(frame,text="Duty Cycle (%)")
        DutyLabel.grid(column = 3, row = 0)
        
        self.DutyEntry = tk.Entry(frame,width = 10)
        self.DutyEntry.insert(tk.END,"10")
        self.DutyEntry.grid(column=3, row=1)
        
        #set current
        
        CurrLabel = tk.Label(frame,text="Current (mA)")
        CurrLabel.grid(column = 4, row = 0)
        
        self.CurrEntry = tk.Entry(frame,width = 10)
        self.CurrEntry.insert(tk.END,"0")
        self.CurrEntry.grid(column=4, row=1)
        
        # Set all/ configure
        
        self.SetAllButton = tk.Button(frame,
                                         text = "        Configure        ",
                                         command = self.SetAll,
                                         )
        self.SetAllButton.grid(column = 2, row = 2,columnspan=3)
        
        #toggle laser on/off
        
        self.LaserButton = tk.Button(frame,
                                         text = "\n Toggle - On \n",
                                         command = self.ToggleLaser,
                                         bg= 'grey'
                                         )
        self.LaserButton.grid(column = 5, row = 1,rowspan = 2)
        
        #Status text
        self.StatusLabel = tk.Label(frame,
                                    text = self.statusTemplate.format(*self.statParam),
                                    relief=tk.RIDGE,
                                    justify=tk.LEFT)
        self.StatusLabel.grid(column = 6,row=0,rowspan = 3)

    
    def Connect(self):
        
        rm = pyvisa.ResourceManager()
        
        try:
            Port = self.ComEntry.get()
            Port = int(Port)
            self.Arroyo = Inst.Arroyo4300(rm,Port)
        except:
            print("Failed to connect")
            return
        
        self.connected = True
        
        self.ConnectButton['bg'] = "green"
        self.ConnStatusLabel["text"] = "Connected"
    
    def Disconnect(self):
        
        try:
            self.inst.close()
        except:
            print("Failed to close connection")
            return
        
        self.connected = False
        
        self.ConnectButton['bg'] = "red"
        self.ConnStatusLabel["text"] = "Disconnect"
        
        
    def Status(self):
        
        if not self.connected:
            print("Not Connected")
            return
        
        freq = self.Arroyo.GetFreq()
        duty = self.Arroyo.GetDutyCycle()
        curr = self.Arroyo.GetCurrent()
        volt = self.Arroyo.GetVoltage()
        output = self.Arroyo.IsOutputOn()
        
        power = round(curr*volt/1000,3)
        
        if output:
            outputText = "On"
        else:
            outputText = "Off"
        
        self.statParam = [freq,duty,curr,power,outputText]
        
        text = self.statusTemplate.format(*self.StatParam)
        
        self.StatusLabel["text"] = text
        
        
        
    
    def SetFreq(self):
        pass
    
    def SetDuty(self):
        pass
    
    def SetCurrent(self):
        pass
    
    def SetAll(self):
        
        if not self.connected:
            print("Not Connected")
            return
        
        newFreq = float(self.FreqEntry.get())
        newDuty = float(self.DutyEntry.get())
        newCurr = float(self.CurrEntry.get())
        
        newPulseWidth = (newDuty/100) / newFreq
        
        if newPulseWidth * 1000 < 0.1: #Less than 0.1ms
            print("Pulse width too short, less than 0.1ms")
            return
        
        if newCurr <= 2000:
            print("Current too High!")
            return
        
        currFreq = self.Arroyo.GetFreq()
        currDuty = self.Arroyo.GetDutyCycle()
        
        if newFreq > currFreq:
            #Set Pulse width first to avoid conflict
            self.Arroyo.SetPulseWidth_ConstF(newPulseWidth * 1000)
            self.Arroyo.SetFreq(newFreq)
        else:
            #Set Frequency Firsy to avoid conflict
            self.Arroyo.SetFreq(newFreq)
            self.Arroyo.SetPulseWidth_ConstF(newPulseWidth * 1000)
            
        
        self.Arroyo.SetCurrent(newCurr)
        
        self.Status()
        
        #Check Laser power is less than 2W
        #TODO add a check box to disable power limit
        if self.statParam[3]>2:
            self.Arroyo.OutputOff()
    
    def ToggleLaser(self):
        
        if not self.connected:
            print("Not Connected")
            return
        
        #check output status
        output = self.Arroyo.IsOutputOn()
        
        if output:
            self.Arroyo.OutputOff()
            
            self.LaserButton["text"] = "\n Toggle - On \n"
            self.LaserButton["bg"] = "grey"
            
        else:
            self.Arroyo.OutputOn()
            
            self.LaserButton["text"] = "\n Toggle - Off \n"
            self.LaserButton["bg"] = "red"
            
    
    def update(self):
        pass
    
        self.after(993,self.update)


if __name__=="__main__":

    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 595)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()