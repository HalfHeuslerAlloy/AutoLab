# -*- coding: utf-8 -*-
"""
Created on Fri May  6 14:59:33 2022

@author: eenmv

Basic Keithley IV curve setup

"""

import tkinter as tk
import time
import numpy as np

import sys
sys.path.append("..")

from multiprocessing import Process, Queue

import pyvisa

import Instruments as Inst

class Handler(tk.Frame):
    """
    Measurement worker of the main AutoLab window
    """
    def __init__(self, master):
        """
        Initial setup of GUI widgets and the general window position
        """
        super().__init__(master)
        
        StartEntryLabel = tk.Label(master,text="Start (V)")
        StartEntryLabel.pack()
        self.StartEntry = tk.Entry(master,width = 10)
        self.StartEntry.insert(tk.END,"-0.5")
        self.StartEntry.pack()
        
        StopEntryLabel = tk.Label(master,text="Stop (V)")
        StopEntryLabel.pack()
        self.StopEntry = tk.Entry(master,width = 10)
        self.StopEntry.insert(tk.END,"0.5")
        self.StopEntry.pack()
        
        StepEntryLabel = tk.Label(master,text="Steps (N)")
        StepEntryLabel.pack()
        self.StepsEntry = tk.Entry(master,width = 10)
        self.StepsEntry.insert(tk.END,"100")
        self.StepsEntry.pack()
        
        DwellEntryLabel = tk.Label(master,text="Dwell (s)")
        DwellEntryLabel.pack()
        self.DwellEntry = tk.Entry(master,width = 10)
        self.DwellEntry.insert(tk.END,"0.1")
        self.DwellEntry.pack()
        
        GBIPLabel = tk.Label(master,text="Keithley GBIP")
        GBIPLabel.pack()
        self.GBIP = tk.Entry(master,width = 10)
        self.GBIP.insert(tk.END,"13")
        self.GBIP.pack()

        
    def Start(self,Pipe):
        
        # get values from entry windows
        Str  = float(self.StartEntry.get())
        Stp  = float(self.StopEntry.get() )
        Steps = float(self.StepsEntry.get())
        Dwl  = float(self.DwellEntry.get())
        GBIPAddress = int(self.GBIP.get())
        
        #Connect to and setup Keithley
        rm = pyvisa.ResourceManager()
        
        try:
            Keithley = Inst.Keithley2400(rm,GBIPAddress)
            Keithley.sense("CURR") #set keithley to measure CURRent
            Keithley.setV(0)
            Keithley.outputOn()
    
            Keithley.close()
        except:
            print("Failed to connect to Keithley during shutdown sequence")
        
        try:
            
            self.Worker = Process(target=Worker, args=(Pipe,Str,Stp,Steps,Dwl,GBIPAddress))
            self.Worker.start()
            
        except Exception as e:
            print(e)
            print("failed to start multiprocessing of expirement worker")
            return False
        
        return True
    
    def Stop(self):
        """
        Abort the current measurement as gracefully as possible
        Put any instruments into a safe state
        
        This is also called if program already has finished
        """
        try:
            self.Measure.terminate()
        except:
            print("Failed to stop process")
            return False
        
        
        GBIPAddress = int(self.GBIP.get())
        
        #Make safe
        rm = pyvisa.ResourceManager()
    
        try:
            Keithley = Inst.Keithley2400(rm,GBIPAddress)
            
            Keithley.setV(0)
            Keithley.outputOff()
    
            Keithley.close()
        except:
            print("Failed to connect to Keithley during shutdown sequence")
       
        return True

        
def Worker(Pipe,Str,Stp,Steps,Dwl,GBIPAddress):
    
    rm = pyvisa.ResourceManager()
    
    Abort = False
    
    try:
        Keithley = Inst.Keithley2400(rm,GBIPAddress)
    except:
        Pipe.send("Esc")
        return
    
    #column headers
    Pipe.send("V    I    R\n")
 
    for V in np.linspace(Str,Stp,Steps):
        
        if Pipe.poll():
            Comm = Pipe.recv()
            if Comm=="STOP":
                Abort = False
        if Abort==True:
            break
        
        Keithley.setV(V)
        
        time.sleep(Dwl)
        
        values = Keithley.readAll()
        
        Pipe.send([values[0],values[1],values[2]])

    
    for V in np.linspace(Stp,Str,Steps):
        
        if Pipe.poll():
            Comm = Pipe.recv()
            if Comm=="STOP":
                Abort = False
        if Abort==True:
            break
        
        Keithley.setV(V)
        
        time.sleep(Dwl)
        
        values = Keithley.readAll()
        
        Pipe.send([values[0],values[1],values[2]])
    
    Keithley.setV(0)
    
    Keithley.close()
    
    Pipe.send("Esc")



if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    