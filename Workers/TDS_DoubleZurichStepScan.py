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
        
        
        """
        Data Format Section
        """
        self.Header_List=["Delay","L1_X", "L1_Y", "L2_X", "L2_Y"]
        
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
        
        StepEntryLabel = tk.Label(self.MainFrame,text="Step")
        StepEntryLabel.pack()
        self.StepEntry = tk.Entry(self.MainFrame,width = 10)
        self.StepEntry.insert(tk.END,"0.03")
        self.StepEntry.pack()
        
        DwellEntryLabel = tk.Label(self.MainFrame,text="Time Constant (s)")
        DwellEntryLabel.pack()
        self.DwellEntry = tk.Entry(self.MainFrame,width = 10)
        self.DwellEntry.insert(tk.END,"0.1")
        self.DwellEntry.pack()
        


    def Start(self,Pipe):
        
        Str  = float(self.StartEntry.get())
        Stp  = float(self.StopEntry.get() )
        Step = float(self.StepEntry.get())
        Dwl  = float(self.DwellEntry.get())
        
        try:

            self.Worker = Process(target=Worker, args=(Pipe,self.Header_List,Str,Stp,Step,Dwl))
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
        
    
    def Stop(self):
        """
        Abort the current measurement as gracefully as possible
        """
        try:
            self.Worker.terminate()
        except:
            return False
       
        return True
    

        
def Worker(Pipe,Headers,Str,Stp,Step,Dwl):
    #column headers
    Pipe.send(Headers)
    
    print("Connecting to instruments")
    
    # Connect to XPS
    try:
        xps = Inst.XPS("192.168.0.77")
    except:
        print("Could not connect to XPS")
        Pipe.send("Esc")
        return
    
    # Connect to Lockin
    try:
        lockin = Inst.ZurichHF2LI()
    except:
        print("Could not connect to Zurich Lockin")
        Pipe.send("Esc")
        return
    
    print("Starting step scan")
    
    for delay in np.arange(Str,Stp,Step):
        #steps has to be broadcast as int explicitly for np 1.23.5
        #Check for commands from controller
        if Pipe.poll():
            Comm = Pipe.recv()
            if Comm=="STOP":
                break
            if Comm=="SKIP":
                print("Skipping")
                break
        
        # Move to position
        xps.GotoDelay('Group4.Pos', delay, 184, 2, True)
        
        # Wait two tc
        time.sleep(lockin.tc * 4.0)
        
        # Get lockin value
        x1, y1, x2, y2 = lockin.GetDoubleLockinValues()
        
        
        Pipe.send([delay, x1, y1, x2, y2])



if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    