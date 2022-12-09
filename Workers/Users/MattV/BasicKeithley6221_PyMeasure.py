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

from pymeasure.instruments.keithley import Keithley6221

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

        
    def Start(self,Pipe):
        
        # get values from entry windows
        Str  = float(self.StartEntry.get())
        Stp  = float(self.StopEntry.get() )
        Steps = float(self.StepsEntry.get())
        Dwl  = float(self.DwellEntry.get())
        
        
        #Connect to and setup Keithley
        try:
            pass
        except Exception as e:
            print(e)
            print("failed to find or communicate with keithley")
            return False
        
        try:
            
            self.Worker = Process(target=Worker, args=(Pipe,Str,Stp,Steps,Dwl))
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

        
def Worker(Pipe,Str,Stp,Steps,Dwl):
    
    try:
        Keithley = keithley = Keithley6221("GPIB::1")
    except:
        Pipe.send("Esc")
        return
    
    keithley.clear()

    # Use the keithley as an AC source
    keithley.waveform_function = "square"   # Set a square waveform
    keithley.waveform_amplitude = 0.005     # Set the amplitude in Amps
    keithley.waveform_offset = 0            # Set zero offset
    keithley.source_compliance = 1          # Set compliance (limit) in V
    keithley.waveform_dutycycle = 50        # Set duty cycle of wave in %
    keithley.waveform_frequency = 347       # Set the frequency in Hz
    keithley.waveform_ranging = "best"      # Set optimal output ranging
    keithley.waveform_duration_cycles = 100 # Set duration of the waveform

    # Link end of waveform to Service Request status bit
    keithley.operation_event_enabled = 128  # OSB listens to end of wave
    keithley.srq_event_enabled = 128        # SRQ listens to OSB

    keithley.waveform_arm()                 # Arm (load) the waveform

    keithley.waveform_start()               # Start the waveform

    keithley.adapter.wait_for_srq()         # Wait for the pulse to finish

    keithley.waveform_abort()               # Disarm (unload) the waveform

    keithley.shutdown()                     # Disables output
    
    for Freq in range(100,500,10):
        Keithley6221.beep(Freq,0.05)
        time.sleep(0.04)
    
    Pipe.send("Esc")



if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    