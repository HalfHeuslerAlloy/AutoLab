# -*- coding: utf-8 -*-
"""
Created on Fri May  6 14:59:33 2022

@author: eenmv
"""

import tkinter as tk
import time
import numpy as np
from multiprocessing import Process, Queue

import sys
sys.path.append("..")
import Instruments as Inst

import pyvisa

class Handler(tk.Frame):
    """
    Measurement worker of the main AutoLab window
    """
    def __init__(self, master):
        """
        Initial setup of GUI widgets and the general window position
        """
        super().__init__(master)
        
        self.Worker = None
        
        StartEntryLabel = tk.Label(master,text="Start")
        StartEntryLabel.pack()
        self.StartEntry = tk.Entry(master,width = 10)
        self.StartEntry.insert(tk.END,"0")
        self.StartEntry.pack()
        
        StopEntryLabel = tk.Label(master,text="Stop")
        StopEntryLabel.pack()
        self.StopEntry = tk.Entry(master,width = 10)
        self.StopEntry.insert(tk.END,"10")
        self.StopEntry.pack()
        
        StepEntryLabel = tk.Label(master,text="Steps")
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
        
        Str  = float(self.StartEntry.get())
        Stp  = float(self.StopEntry.get() )
        Steps = float(self.StepsEntry.get())
        Dwl  = float(self.DwellEntry.get())
        
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
            self.Worker.terminate()
        except:
            return False
       
        return True

        
def Worker(Que,Str,Stp,Steps,Dwl):
    
    #column headers
    Que.put("X    Y1    Y2\n")
 
    for x in np.linspace(Str,Stp,Steps):
        
        X = x
        
        Y1 = np.sin(x)*x**1.2 + np.random.normal()
        Y2 = np.cos(x)*x**1.2 + np.random.normal()
        
        Que.put([X,Y1,Y2])

        time.sleep(Dwl)
    
    Que.put("Esc")



if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    