# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 16:02:22 2022

@author: eenmv
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import font as tkFont

import time

import pyvisa
import Instruments as Inst

class Util(tk.Frame):
    """Controller widget for a IPS120 magnet power supply
    """
    
    #Name of utility so it can be refer to later as part of a dictionary
    name = "SMS"
    
    # B, setB,Heater,Ramping,mode
    statusTemplate = """Current Status:         
        Field (T) : {}
        Setpoint (T): {}
        Switch heater: {}
        Ramping: {}
        Direction: {}"""
    
    statParam = ["NAN","NAN","NAN","NAN","NAN"]
    
    def __init__(self, master,parent=None):
        
        super().__init__(master)
        self.parent=parent
        self.connected = False
        self.Mag = None
        
        frame = tk.Frame(master)
        master.add(frame,text="SMS120C controller")
        
        gbipLabel = tk.Label(frame,text="COM")
        gbipLabel.grid(column=0, row=0)
        self.gbipEntry = tk.Entry(frame,width = 10)
        self.gbipEntry.insert(tk.END,"4")
        self.gbipEntry.grid(column=0, row=1)
        
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
        
        self.DisconnectButton = tk.Button(frame,
                                         text = "Status",
                                         command = self.GetStatusAndField,
                                         )
        self.DisconnectButton.grid(column = 1, row = 2)
        
        SetpointEntryLabel = tk.Label(frame,text="Setpoint (T)")
        SetpointEntryLabel.grid(column = 2, row = 0)
        self.SetpointEntry = tk.Entry(frame,width = 10)
        self.SetpointEntry.insert(tk.END,"0")
        self.SetpointEntry.grid(column = 2, row = 1)
        
        RampEntryLabel = tk.Label(frame,text="Ramp (A/sec)")
        RampEntryLabel.grid(column = 3, row = 0)
        self.RampEntry = tk.Entry(frame,width = 10)
        self.RampEntry.insert(tk.END,"0.0104")
        self.RampEntry.grid(column = 3, row = 1)
        
        
        self.HeaterButton = tk.Button(frame,
                                         text = "Toggle Heater",
                                         command = self.ToggleHeater,
                                         )
        self.HeaterButton.grid(column = 4, row = 0)
        
        self.StartRampButton = tk.Button(frame,
                                         text = " Ramp Start ",
                                         command = self.StartRamp,
                                         )
        self.StartRampButton.grid(column = 4, row = 2)
        
        # B, setB,Heater,Ramping,mode
        self.statParam = ["NAN","NAN","NAN","NAN","NAN"]
        
        self.StatusLabel = tk.Label(frame,text=self.statusTemplate.format(*self.statParam),
                                    relief=tk.RIDGE,
                                    justify=tk.LEFT)
        self.StatusLabel.grid(column=5, row=0, rowspan=4)
        
    def Connect(self):
        """Connect to eht IPS-120 magnet power supply, 
        should not be done while a measure is running and
        a measure should not be started while this is connected!
        """
        
        gbip = int(self.gbipEntry.get())
        
        rm = pyvisa.ResourceManager()
        
        try:
            self.Mag = Inst.SMS120C(rm,gbip)
            self.ConnStatusLabel["text"] = "Connected"
            self.ConnStatusLabel["bg"] = "green"
            print("Connected to SMS120C magnet power supply")
            print("\n\n    WARNING: DO NOT START MEASURE WHILE\n    THIS IS STILL CONNECTED!!!   \n\n")
        except Exception as e:
            print(e)
            print("Failed to connect to SMS120C magnet power supply")
            return False
        
        try:
            self.GetStatusAndField()
        except:
            print("Failed to get initial Examination")
            return False
    
    def Disconnect(self):
        
        try:
            self.Mag.inst.close()
            self.ConnStatusLabel["text"] = "Disconnect"
            self.ConnStatusLabel["bg"] = "red"
            print("Closed connection to IPS-120 magnet power supply")
        except:
            print("Failed to close connection to IPS-120 magnet power supply")
    
    def GetStatusAndField(self):
        
        try:
            self.Mag.update()
            time.sleep(0.1)
            B = self.Mag.B
            time.sleep(0.1)
            self.Mag.inst.clear()
            setB = self.Mag.MID
            
            
            heaterStr = self.Mag.HeaterStatus
            # B, setB,Heater,Ramping,mode
            self.statParam = [B,setB,heaterStr,self.Mag.RampStatus,self.Mag.Direction]
        except Exception as e:
            print(e)
            # B, setB,Heater,Ramping,mode
            self.statParam = ["FAIL","FAIL","FAIL","FAIL","FAIL"]
        
        self.StatusLabel["text"] = self.statusTemplate.format(*self.statParam)
    
    def ToggleHeater(self):
        """Toggle Switch heater on and off
        """
        
        self.Mag.update()
        
        try:
            
            heater = self.Mag.HeaterStatus
            
            if heater=="ON":
                self.Mag.toggle_heater(False)
                print("Heater turned off, wait 1 min for cool down")
            elif heater=="OFF":
                self.Mag.toggle_heater(True)
                print("Heater turned on, wait 1 min for warm up")
            
        except Exception as e:
            print(e)
            print("Failed to toggle heater")
            return
    
    def StartRamp(self):
        """Toggle Switch heater on and off
        """
        try:
            heater = self.Mag.HeaterStatus
            
            if heater == "ON":
            
                setB = float(self.SetpointEntry.get())
                rate = float(self.RampEntry.get())
                
                self.Mag.set_mid(setB)
                time.sleep(0.1)
                self.Mag.set_ramp(rate)
                time.sleep(0.1)
                self.Mag.ramp_to_MID()
                time.sleep(0.1)
                
                print("Ramp started")
                
            else:
                print("Switch heater is Off, can't start ramp!!!")
                return
            
            self.GetStatusAndField()
        
        except Exception as e:
            print(e)
            print("Failed to start ramping")
        

if __name__=="__main__":
    
    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 595)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()