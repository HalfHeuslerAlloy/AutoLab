# -*- coding: utf-8 -*-
"""
Created on Wed May 10 15:39:59 2023

@author: eencsk
NOTE, TO AVOID PYTHON THROWING PROBLEMS WITH VARIABLE NAMES,
THE LAKESHORE 350 IS REFERRED TO AS Tcon (Temperature controller)
AND THE LAKESHORE 218 IS REFERRED TO AS Tmon (Temperature Monitor)
"""
import tkinter as tk
import time
import pyvisa
import Instruments as Inst
from time import sleep
from Utility import Monitor_Window


class Util(tk.Frame):
    """Controller widget for Temperature control of the Green Cryo
    """
    
    #Name of utility so it can be refer to later as part of a dictionary
    name = "Temp_Con"
    statusTemplate = """VTI Temperature (K) :\n{}\nSample Temperature (K):\n{}\nVTI Setpoint (K):{} \nHeater Status: {}
        """
    
    statParam = ["NAN","NAN","NAN","NAN"]
    
    def __init__(self, master, parent):
        """
        Initial Setup of the Util Frame
        """
        self.parent=parent
        super().__init__(master)
        Utilframe = tk.Frame(master)
        master.add(Utilframe,text="Temperature Reading")
        self.Is_connected=False
        #latch to see if something is connected. If not connected, asking to update
        #Status or Turn off Heaters will connect first, Setting a setpoint will yell at foolhardy user
        self.Is_monitoring=False
        
        gbipLabel_350 = tk.Label(Utilframe,text="350 GPIB")
        gbipLabel_350.grid(column=0, row=0, pady=5)
        self.gpib350Entry = tk.Entry(Utilframe,width = 5)
        self.gpib350Entry.insert(tk.END,"7")
        self.gpib350Entry.grid(column=1, row=0, pady=5)
        
        gbipLabel_218 = tk.Label(Utilframe,text="218 GPIB")
        gbipLabel_218.grid(column=0, row=1)
        self.gpib218Entry = tk.Entry(Utilframe,width = 5)
        self.gpib218Entry.insert(tk.END,"6")
        self.gpib218Entry.grid(column=1, row=1)
        
        self.ConnectButton = tk.Button(Utilframe,
                                         text = "Connect",
                                         command = self.Connect,
                                         bg="light gray"
                                         )
        self.ConnectButton.grid(column = 2, row = 0)
        #This button Toggles between Connect and Disconnect depending on the last function used.
        
        
        self.Off_Button=tk.Button(Utilframe,
                                         text = "All Off",
                                         command = self.Alloff,
                                         bg = "red",
                                         width=55
                                         )
        self.Off_Button.grid(column = 0, row = 3, columnspan=4)
        
        self.setpoint_entry=tk.Entry(Utilframe)
        self.setpoint_entry.insert(tk.END,"Enter Setpoint")
        self.setpoint_entry.grid(column = 2, row =1)
        self.setpoint_Button = tk.Button(Utilframe,
                                         text="Apply Setpoint",
                                         command= self.set_Setpoint
                                         )
        self.setpoint_Button.grid(column = 3, row =1)
        
        """
        Status Widget
        """
        self.statParam = ["NAN","NAN","NAN","NAN","NAN"]
        
        self.StatusLabel = tk.Label(Utilframe,text=self.statusTemplate.format(*self.statParam),
                                    relief=tk.RIDGE,
                                    justify=tk.LEFT)
        self.StatusLabel.grid(column=5, row=0, rowspan=5)
        
        self.Toggle_Monitor = tk.Button(Utilframe,
                                         text="Open\nTCon",
                                         command= self.Start_monitoring,
                                         height=5
                                         )
        self.Toggle_Monitor.grid(column = 6, row =0, rowspan=5)
        
    def Connect(self):
        """
        Attempt to connect to the two temperature controllers
        """
        self.rm=pyvisa.ResourceManager()
        L350add=self.gpib350Entry.get()
        L218add=int(self.gpib218Entry.get())#lakeshore addresses
        try:
            self.Tcon=Inst.lakeshore350(self.rm,int(L350add))
            self.Tmon=Inst.lakeshore218(self.rm,L218add)
            self.ConnectButton.configure(bg="green",text="Disconnect",command=self.Disconnect)
            self.Is_connected=True
        except Exception as e:
            print("Error Found In Connection")
            self.ConnectButton.configure(bg="red")
            print(e)
        
    def Disconnect(self):
        """
        Attempt to Disconnect from the instruments and close the resource manager

        """
        try:
            self.Tcon.close()
            self.Tmon.close()
            self.ConnectButton.configure(bg="light gray",text="Connect",command=self.Connect)
            self.Is_connected=False
            self.rm.close()
        except Exception as e:
            self.ConnectButton.configure(bg="red")
            print(e)
            
    def set_Setpoint(self, pipe=None):
        """
        If connected, set the Setpoint on the VTI on the 350. Using Loop/Output 1
        TO DO: Change to Zone. Currently uses fixed PID.
        
        Parameters:
            
            pipe= Python multiprocessing duplex pipe to send the setpoint command to.
        """
        if self.Is_connected==True and self.Is_monitoring==False:
            try:
                setpoint=float(self.setpoint_entry.get())
            except ValueError:
                print("Invalid Setpoint: Not a Number")
                return False
            
            if setpoint > 300:
                print("Setpoint Out of Range")
                return False
            else:
                self.Tcon.setOutputMode(1,1,1,0)
                #confrims that the loop is reading form the correct input and turns it on
                sleep(0.1)
                self.Tcon.setTempSetpointN(1,setpoint)
                A=self.Tcon.getTempN("A")
                B=self.Tcon.getTempN("B")
                self.update_status(A,B,setpoint,"ON")
        else:
            print("Connect to the Supply before enabling the heaters!")
            return(False)
        
    def update_status(self,VTI_Temp,Sample_Temp,setpoint,Heater_Status):
        """ 
        Quick Method to update the StatParam Box
        """
        self.statParam=[VTI_Temp,Sample_Temp,setpoint,Heater_Status]
        self.StatusLabel["text"] = self.statusTemplate.format(*self.statParam)
        
    def Alloff(self):
        if self.Isconnected == False:
            rm=pyvisa.ResourceManager()
            L350add=self.gpib350Entry.get()
            Tcon=Inst.lakeshore350(self.rm,int(L350add))
            Tcon.allOff()
            Tcon.close()
            rm.close()
        else:            
            self.Tcon.allOff()
        
    
    def Start_monitoring(self):
        """
        Starts a new thread to read and control the temperature controllers. 
        NOTE: While monitoring, all commands have to be sent via the pipe.

        Returns
        -------
        None.

        """
        # Mon_Window=tk.Toplevel(self.master)
        # Mon_Window.title("Temp_Mon")
        addresses=[int(self.gpib350Entry.get()),int(self.gpib218Entry.get())]
        self.parent.Temperature_Monitor=Monitor_Window.Mon_Win(self,self.parent,addresses)
        #Passes the Temperature Monitor to the Main Autolab script, where Workers can inherit it
        #Note; I think the Base thing will be inheriting a bit much from this! 
        #It only NEEDS the output of the Pipe and a way to send commands to the Controller. 
        #TODO: Think.
        

        
        
