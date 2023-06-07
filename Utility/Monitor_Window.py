# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 17:35:23 2023

@author: eencsk
Class to manage the Temperature Monitoring Window. 
Developed for the green cryostat but should be adaptable
"""
import tkinter as tk
from multiprocessing import Process, Queue, Pipe
import Instruments as Inst
from Utility import GraphUtil
from tkinter import ttk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib import ticker
import pyvisa

class Mon_Win:
    """
    Class for the Monitoring window GUI
    """
    Mode_Select=[ "Zone","Manual Control", "Manual PID"]
    SensorInput=["A","B","C","D"]
    TC_Model=["Lakeshore 350"]#Temperature controller Models
    TM_Model=["Lakeshore 218", "Lakeshore 350"]
    
    def __init__(self, master,parent,default_addresses):
        #assume that the last element of the Default addresses is the temperature monitor
        self.parent=parent
        addresses=self.parent.address_list
        """Set up Temperature Monitoring GUI"""
        self.Window=tk.Toplevel()
        self.Window.title("Temperature Monitoring")
        self.Window.protocol("WM_DELETE_WINDOW",self.close_function)
        
        Control_Frame=tk.Frame(self.Window,height = 330,width = 480)
        Control_Frame.grid(column=0, row=1, rowspan=3,sticky="N"+"S")
        if len(addresses)==0:
            rm=pyvisa.ResourceManager()
            addresses=rm.list_resources()
            rm.close()
        #if addresses are supplied through the script which calls this util, we dont need to poll all instruments
        #speeds up loading the util
        self.Model=tk.StringVar(Control_Frame,"Lakeshore 350")
        self.ModelEntry=tk.OptionMenu(Control_Frame, self.Model, *self.TC_Model)
        #future-proofing if we want to apply this to, say, HgITCs
        self.ModelEntry.grid(row=0,column=0)
        self.Com=tk.StringVar(Control_Frame,"GPIB Address")
        self.ComEntry=tk.OptionMenu(Control_Frame,self.Com,*addresses)
        self.ComEntry.grid(column=1,row=0)
        
        self.Mode=tk.StringVar(Control_Frame,self.Mode_Select[0])
        self.Mode_Entry=tk.OptionMenu(Control_Frame,self.Mode,*self.Mode_Select)
        self.Mode_Entry.grid(column=3,row=0)
# =============================================================================
#         HEATER CONTROL WIGETS
# =============================================================================
        self.setpoint_entry=tk.Entry(Control_Frame)
        self.setpoint_entry.insert(tk.END,"Enter Setpoint")
        self.setpoint_entry.grid(column = 0, row =1)
        self.ramp_button=tk.Checkbutton(Control_Frame,text="Ramp Setpoint?")
        self.ramp_button.grid(column=1,row=1)
        self.ramp_entry=tk.Entry(Control_Frame)
        self.ramp_entry.insert(tk.END,"Enter Ramp Rate")
        self.ramp_entry.grid(column=2,row=1)
        
        #Setup Manual Heater Output, Hidden by default
        self.power_Label=tk.Label(Control_Frame,text="Heater Power")
        self.power_Label.grid(column=0,row=1)
        self.power_Label.grid_remove()
        self.power_Entry=tk.Scale(Control_Frame, from_=0, to=100, length=300, orient="horizontal",tickinterval=10)
        self.power_Entry.grid(column=1,row=1,columnspan=3)
        self.power_Entry.grid_remove()
        self.range_Label=tk.Label(Control_Frame,text="Heater Range")
        self.range_Label.grid(column=0,row=2)
        self.range_Label.grid_remove()
        
        #setup PID entry, Hidden by Default
        
        
        
        
        self.setpoint_Button = tk.Button(Control_Frame,
                                         text="Activate",
                                         #command= self.set_Setpoint_Zone
                                         )
        self.setpoint_Button.grid(column = 5, row =1)
        #Default is Zone, but the function to switch modes should have a 
        #Method to change the command to the Appropriate mode
        
        self.Off_Button=tk.Button(Control_Frame,
                                         text = "All Off",
                                         #command = self.Alloff,
                                         bg = "red",
                                         width=55
                                         )
        self.Off_Button.grid(column = 0, row = 6, columnspan=4,sticky="s")
        
        

        #frame weighting, from https://stackoverflow.com/questions/31844173/tkinter-sticky-not-working-for-some-frames
        Control_Frame.grid_rowconfigure(0, weight=1)
        Control_Frame.grid_columnconfigure(0, weight=1)
# =============================================================================
#         MONITORING GRAPH GUI, Stolen from Base Autolab
# =============================================================================
        self.GraphFrame = tk.Frame(self.Window)
        self.GraphFrame.grid(column=1, row=1, columnspan=3, rowspan=3)
        self.GraphFrame['borderwidth'] = 10
        self.GraphFrame['relief'] = 'sunken'
        self.GraphFrame['padx'] = 5
        self.GraphFrame['pady'] = 5
        
        self.fig = Figure(figsize=(6,4.62), dpi=100)
        self.fig.set_facecolor("white")
        self.ax = self.fig.add_subplot(111)

        self.Plot1, = self.ax.plot([], [],"#000000",antialiased=False,linewidth=0.5)
       
        
        self.ax.set_facecolor("black")
        self.ax.grid(color="grey")
        self.ax.tick_params(axis='y', colors='#000000')
        #self.ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        #self.axtwin.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        
        formatter = ticker.ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((-2,2))
        
        self.ax.yaxis.set_major_formatter(formatter)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.GraphFrame)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        toolbar = NavigationToolbar2Tk(self.canvas, self.GraphFrame)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        
        
        
    
    
    def close_function(self):
        """
        Funciton to call when the monitoring window is exited.

        """
        print("This will exit the multithreading gracefully")
        #TODO: Impliment the threads exiting correctly on X press
        self.Window.destroy()
