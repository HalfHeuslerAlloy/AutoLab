# -*- coding: utf-8 -*-
"""
Created on Fri May  6 14:59:33 2022

@author: eenmv

Basic Keithley IV curve setup

"""

import tkinter as tk
import time
import datetime
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
        
        Keith1EntryLabel = tk.Label(master,text="Keithley 1 GBIP")
        Keith1EntryLabel.pack()
        self.Keith1Entry = tk.Entry(master,width = 10)
        self.Keith1Entry.insert(tk.END,"13")
        self.Keith1Entry.pack()
        
        Keith2EntryLabel = tk.Label(master,text="Keithley 2 GBIP")
        Keith2EntryLabel.pack()
        self.Keith2Entry = tk.Entry(master,width = 10)
        self.Keith2Entry.insert(tk.END,"24")
        self.Keith2Entry.pack()
        
        OscEntryLabel = tk.Label(master,text="Oscilloscope GBIP")
        OscEntryLabel.pack()
        self.OscEntry = tk.Entry(master,width = 10)
        self.OscEntry.insert(tk.END,"17")
        self.OscEntry.pack()
        
        RateEntryLabel = tk.Label(master,text="Update Rate (s)")
        RateEntryLabel.pack()
        self.RateEntry = tk.Entry(master,width = 10)
        self.RateEntry.insert(tk.END,"10")
        self.RateEntry.pack()

        
    def Start(self,Que):
        """
        Start the worker doing the measurement
        """
        
        # get values from entry windows
        Dwell  = float(self.StartEntry.get())
        
        Keith1_GBIP  = float(self.Keith1Entry.get())
        Keith2_GBIP  = float(self.Keith2Entry.get())
        Osc_GBIP  = float(self.OscEntry.get())
        
        try:
            
            self.Worker = Process(target=Worker, args=(Que,Keith1_GBIP,Keith2_GBIP,Osc_GBIP,Dwell))
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

        
def Worker(Que,Keith1_GBIP,Keith2_GBIP,Osc_GBIP,Dwell):
    
    rm = pyvisa.ResourceManager()
    
    try:
        Keith1 = Inst.Keithley2400(rm,Keith1_GBIP)
        Keith2 = Inst.Keithley2400(rm,Keith2_GBIP)
        Osc = rm.open_resource(Osc_GBIP)
        Osc.write_termination = Osc.CR
        Osc.read_termination = Osc.CR
    except:
        try:
            Keith1.close()
            Keith2.close()
            Osc.close()
        except:
            pass
        Que.put("Esc")
        return
    
    #column headers
    Que.put("Time    Gate1(Ohm)    Gate2(Ohm)    SpikeCh1(V)    SpikeCh2(V)")
    
    while(True):
        
        Data = []
        
        #Get current time
        TimeCurr = int(time.time())
        Data.append(TimeCurr)
        
        #Read keithleys
        values = Keith1.readAll()
        Data.append(values[2])
        
        values = Keith2.readAll()
        Data.append(values[2])
        
        #Read Oscilloscope
        Osc.write(":STOP")
        Osc.write(":MEASure:SOUR CHAN1;:MEASURE:VPP?")
        Val = float(Osc.read())
        if Val>100:
            Val = 0
        Data.append(Val)
        
        Osc.write(":MEASure:SOUR CHAN2;:MEASURE:VPP?")
        Val = float(Osc.read())
        if Val>100:
            Val = 0
        Data.append(Val)
        
        Osc.write(":RUN")
        
        time.sleep(Dwell)
    
    Que.put("Esc")



if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    