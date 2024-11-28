# -*- coding: utf-8 -*-
"""
Created on Fri May  6 14:59:33 2022

@author: eenmv
Test Worker for fiddling around with Multi-Parameter Loops.
"""

import tkinter as tk
from tkinter import ttk
import time
import numpy as np
from multiprocessing import Process, Queue

import sys
sys.path.append("..")
import Instruments as Inst
import Utility

import pyvisa

class Handler(ttk.Notebook):
    """
    Measurement worker of the main AutoLab window
    """
    def __init__(self, master, parent):
        """
        Preamble to set up the Main Script Frame
        """
        self.parent = parent
        super().__init__(master)
        self.Util_List=[]#list to append tabs to, so that the Autolab wrapper can access them 
        self.Worker = None
        self.MainFrame=tk.Frame(master)
        self.MainFrame.grid(column=0, row=1, columnspan=3, rowspan=3)
        master.add(self.MainFrame,text="Main Script")
        
        """
        Utilities Section
        """
        self.UtilTab1=Utility.TestUtil.Util(master,title="Test 1")#Calls the Relevant Util Tab and Adds to Master
        self.Util_List.append(self.UtilTab1)
        self.UtilTab2=Utility.TestUtil.Util(master,title="Test 2")
        #Duplicate Util tabs are a-Ok!, just make sure they're called something else
        self.Util_List.append(self.UtilTab2)
        
        """
        Metadata Section
        """
        self.Header_List=["X","Y1","Y2","Z"]
        
        """
        Initial setup of GUI widgets and the general window position
        """
        LoopLabel=tk.Label(self.MainFrame, text="Loop Number")
        LoopLabel.pack()
        self.LoopText = tk.Message(self.MainFrame,font=200, relief = "sunken",text="Not Started")
        self.LoopText.pack()
        
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
        self.StepsEntry.insert(tk.END,"100")
        self.StepsEntry.pack()
        
        DwellEntryLabel = tk.Label(self.MainFrame,text="Dwell (s)")
        DwellEntryLabel.pack()
        self.DwellEntry = tk.Entry(self.MainFrame,width = 10)
        self.DwellEntry.insert(tk.END,"0.1")
        self.DwellEntry.pack()
        
        self.SkipButton = tk.Button(self.MainFrame,text="Skip",command=self.Skip)
        self.SkipButton.pack()
        
        
        
        
    def Start(self,Pipe):
        
        Str  = float(self.StartEntry.get())
        Stp  = float(self.StopEntry.get() )
        Steps = float(self.StepsEntry.get())
        Dwl  = float(self.DwellEntry.get())
        
        try:

            self.Worker = Process(target=Worker, args=(Pipe,self.Header_List,Str,Stp,Steps,Dwl))
            self.Worker.start()
            
        except Exception as e:
            print(e)
            print("failed to start multiprocessing of expirement worker")
            return False
        
        return True
    
    def Skip(self):
        """

        Returns
        -------
        None.

        """
        
        print("Sending skip command")
        self.parent.PipeRecv.send("SKIP")
        
    def Update(self, Data):
        """
        Update GUI Widgets with Relevant Data. 
        Called during the Main Autolab Get Data routine (nested in the Update window routine)
        so SPEED is the key
        
        Data:the data currently in the pipe in list form.

        """
        self.LoopText["text"]=Data[-1]
        
    
    def Stop(self):
        """
        Abort the current measurement as gracefully as possible
        """
        try:
            self.Worker.terminate()
        except:
            return False
       
        return True

        
def Worker(Pipe,Headers,Str,Stp,Steps,Dwl):
    

    
    for z in range(0,3):
        #column headers, do it once per multi param loop.
        Pipe.send(Headers)
        for x in np.linspace(Str,Stp,int(Steps)):
            #steps has to be broadcast as int explicitly for np 1.23.5
            #Check for commands from controller
            if Pipe.poll():
                Comm = Pipe.recv()
                if Comm=="STOP":
                    break
                if Comm=="SKIP":
                    print("Skipping")
                    break
            
            X = x
            
            Y1 = np.sin(x)*x**z + np.random.normal()
            Y2 = np.cos(x)*x**z + np.random.normal()
            
            Pipe.send([X,Y1,Y2,z])
    
            time.sleep(Dwl)
        print("Finished Loop {}".format(z+1))
        Pipe.send("NewFile")
    
    Pipe.send("Esc")



if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    