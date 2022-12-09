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
        
        ########## Gate1 settings ###########
        
        Gate1StartEntryLabel = tk.Label(master,text="Gate1 Start (V)")
        Gate1StartEntryLabel.grid(column=0, row=0)
        self.Gate1StartEntry = tk.Entry(master,width = 10)
        self.Gate1StartEntry.insert(tk.END,"0")
        self.Gate1StartEntry.grid(column=0, row=1)
        
        Gate1StopEntryLabel = tk.Label(master,text="Gate1 Stop (V)")
        Gate1StopEntryLabel.grid(column=0, row=2)
        self.Gate1StopEntry = tk.Entry(master,width = 10)
        self.Gate1StopEntry.insert(tk.END,"0.2")
        self.Gate1StopEntry.grid(column=0, row=3)
        
        Gate1StepEntryLabel = tk.Label(master,text="Gate1 Size (V)")
        Gate1StepEntryLabel.grid(column=0, row=4)
        self.Gate1StepEntry = tk.Entry(master,width = 10)
        self.Gate1StepEntry.insert(tk.END,"0.01")
        self.Gate1StepEntry.grid(column=0, row=5)
        
        ########### Gate2 settings ################
        
        Gate2StartEntryLabel = tk.Label(master,text="Gate2 Start (V)")
        Gate2StartEntryLabel.grid(column=1, row=0)
        self.Gate2StartEntry = tk.Entry(master,width = 10)
        self.Gate2StartEntry.insert(tk.END,"-0.1")
        self.Gate2StartEntry.grid(column=1, row=1)
        
        Gate2StopEntryLabel = tk.Label(master,text="Gate2 Stop (V)")
        Gate2StopEntryLabel.grid(column=1, row=2)
        self.Gate2StopEntry = tk.Entry(master,width = 10)
        self.Gate2StopEntry.insert(tk.END,"0.1")
        self.Gate2StopEntry.grid(column=1, row=3)
        
        Gate2StepEntryLabel = tk.Label(master,text="Gate2 Step Size (V)")
        Gate2StepEntryLabel.grid(column=1, row=4)
        self.Gate2StepEntry = tk.Entry(master,width = 10)
        self.Gate2StepEntry.insert(tk.END,"0.01")
        self.Gate2StepEntry.grid(column=1, row=5)
        
        ######### Dwell ###########
        
        Dwell1EntryLabel = tk.Label(master,text="Dwell X (s)")
        Dwell1EntryLabel.grid(column=0, row=6)
        self.Dwell1Entry = tk.Entry(master,width = 10)
        self.Dwell1Entry.insert(tk.END,"5")
        self.Dwell1Entry.grid(column=0, row=7)
        
        Dwell2EntryLabel = tk.Label(master,text="Dwell Y (s)")
        Dwell2EntryLabel.grid(column=1, row=6)
        self.Dwell2Entry = tk.Entry(master,width = 10)
        self.Dwell2Entry.insert(tk.END,"0.5")
        self.Dwell2Entry.grid(column=1, row=7)

        
    def Start(self,Pipe):
        """
        Start the worker doing the measurement
        """
        
        # get values from entry windows        
        gate1Str  = float(self.Gate1StartEntry.get())
        gate1Stp  = float(self.Gate1StopEntry.get())
        gate1Step = float(self.Gate1StepEntry.get())
        
        gate2Str  = float(self.Gate2StartEntry.get())
        gate2Stp  = float(self.Gate2StopEntry.get())
        gate2Step = float(self.Gate2StepEntry.get())
        
        Dwl1  = float(self.Dwell1Entry.get())
        Dwl2  = float(self.Dwell2Entry.get())
        
        
#        totalPoints = (2 * abs(Str-Stp)/Step + 2) * (2 * abs(gateStr-gateStp)/gateStep + 2)
#        
#        print("Total number of points will be {}".format(totalPoints))
#        totalTime = totalPoints*(Dwl)/60 + 2*abs(Stp-Str)/0.1 #Estimated total time in minutes
#        print("Estimated time to complet is {}mins".format( round(totalTime,1) ))
        
        try:
            
            self.Worker = Process(target=Worker, args=(Pipe,
                                                       gate1Str,gate1Stp,gate1Step,
                                                       gate2Str,gate2Stp,gate2Step,
                                                       Dwl1,Dwl2))
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

        
def Worker(Pipe,gate1Str,gate1Stp,gate1Step,gate2Str,gate2Stp,gate2Step,Dwl1,Dwl2):
    """
    Actual worker that runs the measurement
    """
    
    #spawn resource manager
    rm = pyvisa.ResourceManager()
    
    Abort = False
    
    try:
        Lockin1 = Inst.DSP_7265(rm,12)
        Lockin2 = Inst.DSP_7265(rm,14)
        Keith1 = Inst.Keithley2400(rm,13)
        Keith2 = Inst.Keithley2400(rm,23)
    except Exception as e:
        print(e)
        Pipe.send("Esc")
        return
    
    #column headers
    Pipe.send("#Gate1(V)    Gate2(V)    L1V_X(V)    L1V_Y(V)    L2V_X(V)    L2V_Y(V)\n")
    
    
    numGPoints = round(abs(gate1Str-gate1Stp)/gate1Step + 1)
    G1_points = np.linspace(gate1Str,gate1Stp,numGPoints)
    
    numGPoints = round(abs(gate2Str-gate2Stp)/gate2Step + 1)
    G2_points = np.linspace(gate2Str,gate2Stp,numGPoints)
    
    for Gate1 in G1_points:
        
        Keith1.setV(Gate1)
        
        for Gate2 in G2_points:
        
            Keith2.setV(Gate2)
            
            # normally dwell longer for start of new row
            if Gate2==G2_points[0]:
                time.sleep(Dwl1)
            else:
                time.sleep(Dwl2)
            
            #Check for commands from controller
            if Pipe.poll():
                Comm = Pipe.recv()
                if Comm=="STOP":
                    Abort = True
            if Abort == True:
                break
                
            R1_X,R1_Y = Lockin1.XY
            R2_X,R2_Y = Lockin2.XY
        
            Pipe.send([Gate1,Gate2,R1_X,R1_Y,R2_X,R2_Y])
            
            ###########
            
        if Abort == True:
            break

    
    Keith1.setV(0)
    Keith2.setV(0)
    
    Pipe.send("Esc")



if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    