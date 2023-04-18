# -*- coding: utf-8 -*-
"""
Created on Fri May  6 14:59:33 2022

@author: eenmv
"""

import tkinter as tk
from tkinter import ttk
import time
import numpy as np
from multiprocessing import Process, Queue

import sys
sys.path.append("..")
import Instruments as Inst

import pyvisa

class Handler(ttk.Notebook):
    """
    Measurement worker of the main AutoLab window
    """
    def __init__(self, master):
        """
        Preamble to set up the Main Script Frame        
        """
        super().__init__(master)
        self.Worker = None
        self.MainFrame=tk.Frame(master)
        self.MainFrame.grid(column=0, row=1, columnspan=3, rowspan=3)
        master.add(self.MainFrame,text="Main Script") 
        """
        Utilities Section
        """
        

        """
        Initial setup of GUI widgets and the general window position
        """
        StartEntryLabel = tk.Label(self.MainFrame,text="Start")
        StartEntryLabel.pack()
        self.StartEntry = tk.Entry(self.MainFrame,width = 10)
        self.StartEntry.insert(tk.END,"0")
        self.StartEntry.pack()
        
        StopEntryLabel = tk.Label(self.MainFrame,text="Stop")
        StopEntryLabel.pack()
        self.StopEntry = tk.Entry(self.MainFrame,width = 10)
        self.StopEntry.insert(tk.END,"10")
        self.StopEntry.pack()
        
        StepEntryLabel = tk.Label(self.MainFrame,text="Steps")
        StepEntryLabel.pack()
        self.StepsEntry = tk.Entry(self.MainFrame,width = 10)
        self.StepsEntry.insert(tk.END,"11")
        self.StepsEntry.pack()
        
        DwellEntryLabel = tk.Label(self.MainFrame,text="Dwell (s)")
        DwellEntryLabel.pack()
        self.DwellEntry = tk.Entry(self.MainFrame,width = 10)
        self.DwellEntry.insert(tk.END,"0.1")
        self.DwellEntry.pack()

        
    def Start(self,Pipe):
        
        Str  = float(self.StartEntry.get())
        Stp  = float(self.StopEntry.get() )
        Steps = float(self.StepsEntry.get())
        Dwl  = float(self.DwellEntry.get())
        
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
            self.Worker.terminate()
        except:
            return False
       
        return True

        
def Worker(Pipe,Str,Stp,Steps,Dwl):
    
    #column headers
    Pipe.send("X    Y1    Y2\n")
 
    for x in np.linspace(Str,Stp,int(Steps)):
        
        for y in np.linspace(Str,Stp,int(Steps)):
        
            #Check for commands from controller
            if Pipe.poll():
                Comm = Pipe.recv()
                if Comm=="STOP":
                    break
            
            
            z = np.cos(x)*np.sin(y)*x*y  + np.random.normal()
            
            Pipe.send([x,y,z])
    
            time.sleep(Dwl)
    
    Pipe.send("Esc")



if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    