# -*- coding: utf-8 -*-
"""
Created on Wed May 10 15:39:59 2023

@author: eencsk
Rehashed Temp_Con Util to be a bit more of a generic poll 
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
    statusTemplate = """VTI Temperature (K) :\n{}\nSample Temperature (K):\n{}
        """
    TC_Model=["Lakeshore_350","OI_503"]#Temperature controller Models
    statParam = ["NAN","NAN"]
    
    def __init__(self, master, parent):
        """
        Initial Setup of the Util Frame
        """
        self.parent=parent
        #Master is the Host ttk.Notebook the util is embedded into. Parent should be a 
        #non-gui type script that can recieve the pipes (for adding to data, ect)
        super().__init__(master)
        Utilframe = tk.Frame(master)
        master.add(Utilframe,text="Temperature Reading")
        self.Is_connected=False
        #latch to see if something is connected. If not connected, asking to update
        #Status or Turn off Heaters will connect first, Setting a setpoint will yell at foolhardy user
        self.Is_monitoring=False
        
        gpiBLabel_Con = tk.Label(Utilframe,text="Temp_COMS")
        gpiBLabel_Con.grid(column=0, row=0, pady=5)
        self.gpiBLabel_ConEntry = tk.Entry(Utilframe,width = 5)
        self.gpiBLabel_ConEntry.insert(tk.END,"24")
        self.gpiBLabel_ConEntry.grid(column=1, row=0, pady=5)
        
        
        gbipLabel_218 = tk.Label(Utilframe,text="Controller Model")
        gbipLabel_218.grid(column=0, row=1)
        self.Model=tk.StringVar(Utilframe,self.TC_Model[1])
        #Should Attempt to Initialise with whatever model Temperature controller was given at main button press. 
        self.ModelEntry=tk.OptionMenu(Utilframe, self.Model, *self.TC_Model)
        self.ModelEntry.grid(column=1, row=1)
        
        self.ConnectButton = tk.Button(Utilframe,
                                         text = "Connect",
                                         command = self.Connect,
                                         bg="light gray"
                                         )
        self.ConnectButton.grid(column = 2, row = 0)
        #This button Toggles between Connect and Disconnect depending on the last function used.
        
        
        """
        Status Widget
        """
        self.statParam = ["NAN","NAN"]
        
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
        Tcon_add=self.gpiBLabel_ConEntry.get()
        try:
            Controller=self.Model.get()
            if Controller == "Lakeshore_350":
                self.Tcon=Inst.lakeshore350(self.rm,int(Tcon_add))
            elif Controller == "OI_503" :
                self.Tcon=Inst.OI_503(self.rm,int(Tcon_add))
            else:
                raise Exception("Unknown Temperature Controller Model!")
            
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
            #self.Tmon.close()
            self.ConnectButton.configure(bg="light gray",text="Connect",command=self.Connect)
            self.Is_connected=False
            self.rm.close()
        except Exception as e:
            self.ConnectButton.configure(bg="red")
            print(e)
            
    # def set_Setpoint(self, pipe=None):
    #     """
    #     If connected, set the Setpoint on the VTI on the 350. Using Loop/Output 1
    #     TO DO: Change to Zone. Currently uses fixed PID.
        
    #     Parameters:
            
    #         pipe= Python multiprocessing duplex pipe to send the setpoint command to.
    #     """
    #     if self.Is_connected==True and self.Is_monitoring==False:
    #         try:
    #             setpoint=float(self.setpoint_entry.get())
    #         except ValueError:
    #             print("Invalid Setpoint: Not a Number")
    #             return False
            
    #         if setpoint > 300:
    #             print("Setpoint Out of Range")
    #             return False
    #         else:
    #             self.Tcon.setOutputMode(1,1,1,0)
    #             #confrims that the loop is reading form the correct input and turns it on
    #             sleep(0.1)
    #             self.Tcon.setTempSetpointN(1,setpoint)
    #             A=self.Tcon.getTempN("A")
    #             B=self.Tcon.getTempN("B")
    #             self.update_status(A,B,setpoint,"ON")
    #     else:
    #         print("Connect to the Supply before enabling the heaters!")
    #         return(False)
        
    # def update_status(self,VTI_Temp,Sample_Temp,setpoint,Heater_Status):
    #     """ 
    #     Quick Method to update the StatParam Box
    #     """
    #     self.statParam=[VTI_Temp,Sample_Temp,setpoint,Heater_Status]
    #     self.StatusLabel["text"] = self.statusTemplate.format(*self.statParam)
        
    def Alloff(self):
        if self.Isconnected == False:
            rm=pyvisa.ResourceManager()
            try:
                Controller=self.Model.get()
                if Controller == "Lakeshore_350":
                    Tcon=Inst.lakeshore350(self.rm,int(self.gpiBLabel_ConEntry.get()))
                elif Controller == "OI_503" :
                    Tcon=Inst.OI_503(self.rm,int(self.gpiBLabel_ConEntry.get()))
                else:
                    raise Exception("Unknown Temperature Controller Model!")
            except Exception as e:
                print("Error Found In Connection")
                print (e)
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

        addresses=[int(self.gpiBLabel_ConEntry.get())]
        monitor=Monitor_Window.Mon_Win(self,self.parent,addresses,self.TC_Model.index(self.Model.get()))
        #Passes the Temperature Monitor to the Main Autolab script, where Workers can inherit it
        #Note; I think the Base thing will be inheriting a bit much from this! 
        #It only NEEDS the output of the Pipe and a way to send commands to the Controller. 
        #TODO: Think.
        self.parent.T_PipeRecv,self.parent.T_PipeSend=monitor.Temp_PipeRecv, monitor.Temp_PipeSend
        #gives the parent access to the tmon pipes, which can be polled for temperatures
        

        
        
