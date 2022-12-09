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

from pymeasure.instruments.keithley import Keithley2400

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

        
    def Start(self,Que):
        
        # get values from entry windows
        Str  = float(self.StartEntry.get())
        Stp  = float(self.StopEntry.get() )
        Steps = float(self.StepsEntry.get())
        Dwl  = float(self.DwellEntry.get())
        
        
        #Connect to and setup Keithley
        try:
            #TODO add communication test
            #Keithley = self.Resources.insts["Keithley1"]
            #Keithley.setV(0)
            pass
        except Exception as e:
            print(e)
            print("failed to find or communicate with keithley")
            return False
        
        try:
            
            self.Worker = Process(target=Worker, args=(Que,Str,Stp,Steps,Dwl))
            self.Worker.start()
            
        except Exception as e:
            print(e)
            print("failed to start multiprocessing of expirement worker")
            return False
        
        return True
    
    def Stop(self):
        """
        Abort the current measurement as gracefully as possible
        """
        try:
            self.Measure.terminate()
        except:
            print("Failed to stop process")
            return False
       
        return True

        
def Worker(Que,Str,Stp,Steps,Dwl):
    
    try:
        Keithley = Keithley2400("GPIB::13")
    except:
        Que.put("Esc")
        return
    
    Keithley.reset()
    Keithley.measure_resistance()
    Keithley.apply_voltage()
    time.sleep(0.1)
    Keithley.enable_source()
    
    #column headers
    Que.put("V    I    R\n")
 
    for V in np.linspace(Str,Stp,Steps):
        
        Keithley.source_voltage = V
        
        time.sleep(Dwl)
        
        #voltage,current, and resistance
        values = Keithley.means
        
        Que.put([values[0],values[1],values[2]])

    
    for V in np.linspace(Stp,Str,Steps):
        
        Keithley.source_voltage = V
        
        time.sleep(Dwl)
        
        #voltage,current, and resistance
        values = Keithley.means
        
        Que.put([values[0],values[1],values[2]])
    
    Keithley.source_voltage = 0
    
    Keithley.shutdown()
    
    Que.put("Esc")



if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    