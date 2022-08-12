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
        
        ########## Magnet settings ###########
        
        StartEntryLabel = tk.Label(master,text="Field Start (T)")
        StartEntryLabel.grid(column=0, row=0)
        self.StartEntry = tk.Entry(master,width = 10)
        self.StartEntry.insert(tk.END,"0")
        self.StartEntry.grid(column=0, row=1)
        
        StopEntryLabel = tk.Label(master,text="Field Stop (T)")
        StopEntryLabel.grid(column=0, row=2)
        self.StopEntry = tk.Entry(master,width = 10)
        self.StopEntry.insert(tk.END,"0.2")
        self.StopEntry.grid(column=0, row=3)
        
        StepEntryLabel = tk.Label(master,text="Field Step Size (T)")
        StepEntryLabel.grid(column=0, row=4)
        self.StepEntry = tk.Entry(master,width = 10)
        self.StepEntry.insert(tk.END,"0.01")
        self.StepEntry.grid(column=0, row=5)
        
        ########### Keithley settings ################
        
        GateStartEntryLabel = tk.Label(master,text="Gate Start (V)")
        GateStartEntryLabel.grid(column=1, row=0)
        self.GateStartEntry = tk.Entry(master,width = 10)
        self.GateStartEntry.insert(tk.END,"-0.1")
        self.GateStartEntry.grid(column=1, row=1)
        
        GateStopEntryLabel = tk.Label(master,text="Gate Stop (V)")
        GateStopEntryLabel.grid(column=1, row=2)
        self.GateStopEntry = tk.Entry(master,width = 10)
        self.GateStopEntry.insert(tk.END,"0.1")
        self.GateStopEntry.grid(column=1, row=3)
        
        GateStepEntryLabel = tk.Label(master,text="Gate Step Size (V)")
        GateStepEntryLabel.grid(column=1, row=4)
        self.GateStepEntry = tk.Entry(master,width = 10)
        self.GateStepEntry.insert(tk.END,"0.01")
        self.GateStepEntry.grid(column=1, row=5)
        
        DwellEntryLabel = tk.Label(master,text="Dwell (s)")
        DwellEntryLabel.grid(column=0, row=6)
        self.DwellEntry = tk.Entry(master,width = 10)
        self.DwellEntry.insert(tk.END,"0.5")
        self.DwellEntry.grid(column=0, row=7)

        
    def Start(self,Pipe):
        """
        Start the worker doing the measurement
        """
        
        # get values from entry windows
        Str  = float(self.StartEntry.get())
        Stp  = float(self.StopEntry.get() )
        Step = float(self.StepEntry.get())
        
        gateStr  = float(self.GateStartEntry.get())
        gateStp  = float(self.GateStopEntry.get() )
        gateStep = float(self.GateStepEntry.get())
        
        Dwl  = float(self.DwellEntry.get())
        
        #Test parameters
        if (Step>0.1):
            print("Ramp rate too high. Limit is 0.1T/min")
            return False
        elif (abs(Str)>8):
            print("Parameters out of bounds")
            return False
        elif (abs(Stp)>8):
            print("Parameters out of bounds")
            return False
        
        print("Field will start at {0}T and peak at at {1}T".format(Str,Stp))
        
        totalPoints = (2 * abs(Str-Stp)/Step + 2) * (2 * abs(gateStr-gateStp)/gateStep + 2)
        
        print("Total number of points will be {}".format(totalPoints))
        totalTime = totalPoints*(Dwl)/60 + 2*abs(Stp-Str)/0.1 #Estimated total time in minutes
        print("Estimated time to complet is {}mins".format( round(totalTime,1) ))
        
        try:
            
            self.Worker = Process(target=Worker, args=(Pipe,Str,Stp,Step,gateStr,gateStp,gateStep,Dwl))
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
            self.Measure.join()
        except:
            print("Failed to stop process")
            return False
       
        return True

        
def Worker(Pipe,Str,Stp,Step,gateStr,gateStp,gateStep,Dwl):
    
    rm = pyvisa.ResourceManager()
    
    Abort = False
    
    try:
        Lockin1 = Inst.DSP_7265(rm,14)
        Lockin2 = Inst.DSP_7280(rm,12)
        Mag = Inst.IPS120(rm,25)
        Keith = Inst.Keithley2400(rm,13)
    except Exception as e:
        print(e)
        Pipe.send("Esc")
        return
    
    #column headers
    Pipe.send("#B(T)    Gate(V)    Vxx_X(V)    Vxx_Y(V)    Vxy_X(V)    Vxy_Y(V)\n")
    
    numBPoints = round(abs(Str-Stp)/Step + 1)
    B_points = np.append(np.linspace(Str,Stp,numBPoints),
                         np.linspace(Stp,Str,numBPoints))
    
    numGPoints = round(abs(gateStr-gateStp)/gateStep + 1)
    G_points = np.append(np.linspace(gateStr,gateStp,numGPoints),
                         np.linspace(gateStp,gateStr,numGPoints))

    #Test if Magnet switch heater is on
    Mag.ExamineStatus()

    if Mag.is_SwitchHeaterOn:
        pass
    else:
        Mag.SwitchHeaterOn()
        time.sleep(60)
    
    # Magnet ready
    
    print("Sweeping Magnet to start")
    #Go to start position
    Mag.set_SetPoint(Str)
    time.sleep(0.1)
    Mag.set_FieldRate(0.1)
    time.sleep(0.1)
    Mag.sweep_SetPoint()
    time.sleep(0.1)
    
    Mag.ExamineStatus()
    time.sleep(0.1)
    #Wait until reached start position
    while(Mag.Ramping):
        #Check for commands from controller
        if Pipe.poll():
            Comm = Pipe.recv()
            if Comm=="STOP":
                Abort = True
        if Abort == True:
            break
        time.sleep(1)
        Mag.ExamineStatus()
    
    ## now at start position
    
    print("Stepping Magnet")
    
    for B in B_points:
        
        #Check for commands from controller
        if Pipe.poll():
            Comm = Pipe.recv()
            if Comm=="STOP":
                Abort = True
        if Abort == True:
            break
        
        
        Mag.set_SetPoint(B)
        time.sleep(0.1)
        #Mag.sweep_SetPoint()
        time.sleep(0.1)
        Mag.inst.clear()
        
        Keith.setV(gateStr)
        
        #time for time to reach next B point
        time.sleep(Step/0.1*60)
        
        B_real = Mag.get_B()
        
        for G in G_points:
            
            Keith.setV(G)
            Rxx_X,Rxx_Y = Lockin1.XY
            Rxy_X,Rxy_Y = Lockin2.XY
        
            Pipe.send([B_real,G,Rxx_X,Rxx_Y,Rxy_X,Rxy_Y])
            
            time.sleep(Dwl)

    print("Sweeping Magnet to start again")
    #Ramp to start field
    Mag.set_SetPoint(Str)
    time.sleep(0.1)
    Mag.sweep_SetPoint()
    time.sleep(0.1)
    
    Keith.setV(0)
    
    Pipe.send("Esc")



if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    