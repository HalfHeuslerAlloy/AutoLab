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
        master.add(self.MainFrame,text="Scan Settings")
        
        self.XPSFrame = tk.Frame(master)
        self.XPSFrame.grid(column=0, row=1, columnspan=3, rowspan=3)
        master.add(self.XPSFrame,text="XPS Settings")
        
        """
        Utilities Section
        """
        
        
        """
        Data Format Section
        """
        self.Header_List=["Delay","L1_X", "L1_Y", "L2_X", "L2_Y", "Repeat"]
        
        """
        Initial setup of GUI widgets and the general window position
        """
        
        ## Delay Controls
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
        
        BandwidthEntryLabel = tk.Label(self.MainFrame,text="Bandwidth (THz)")
        BandwidthEntryLabel.pack()
        self.BandwidthEntry = tk.Entry(self.MainFrame,width = 10)
        self.BandwidthEntry.insert(tk.END,"15")
        self.BandwidthEntry.pack()
        
        RepeatsEntryLabel = tk.Label(self.MainFrame,text="Repeats")
        RepeatsEntryLabel.pack()
        self.RepeatsEntry = tk.Entry(self.MainFrame,width = 10)
        self.RepeatsEntry.insert(tk.END,"1")
        self.RepeatsEntry.pack()
        
        # XPS Controls
        
        IPEntryLabel = tk.Label(self.XPSFrame,text="IP Address")
        IPEntryLabel.pack()
        self.IPEntry = tk.Entry(self.XPSFrame,width = 20)
        self.IPEntry.insert(tk.END,"192.168.0.77")
        self.IPEntry.pack()
        
        GroupEntryLabel = tk.Label(self.XPSFrame,text="Group Name")
        GroupEntryLabel.pack()
        self.GroupEntry = tk.Entry(self.XPSFrame,width = 20)
        self.GroupEntry.insert(tk.END,"Group4.Pos")
        self.GroupEntry.pack()
        
        ZPEntryLabel = tk.Label(self.XPSFrame,text="Zero Position (ps)")
        ZPEntryLabel.pack()
        self.ZPEntry = tk.Entry(self.XPSFrame,width = 10)
        self.ZPEntry.insert(tk.END,"184")
        self.ZPEntry.pack()
        
        PassEntryLabel = tk.Label(self.XPSFrame,text="Passes")
        PassEntryLabel.pack()
        self.PassEntry = tk.Entry(self.XPSFrame,width = 10)
        self.PassEntry.insert(tk.END,"2")
        self.PassEntry.pack()
        
        self.ReverseCheckVar = tk.IntVar()
        
        self.ReverseCheck = tk.Checkbutton(self.XPSFrame, variable=self.ReverseCheckVar, text="Reverse", onvalue=1, offvalue=0)
        self.ReverseCheck.pack()
        


    def Start(self,Pipe):
        
        start  = float(self.StartEntry.get())
        stop  = float(self.StopEntry.get())
        step = float(self.StepEntry.get())
        
        ip = self.IPEntry.get()
        groupName = self.GroupEntry.get()
        bandwidth = float(self.BandwidthEntry.get())
        zeroPos = float(self.ZPEntry.get())
        passes = float(self.PassEntry.get())
        reverse = bool(self.ReverseCheckVar.get())
        
        repeats = int(self.RepeatsEntry.get())
                
        try:
            self.Worker = Process(target=Worker, args=(Pipe,self.Header_List,start,stop,step, ip, groupName, bandwidth, zeroPos, passes, reverse, repeats))
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
    

        
def Worker(Pipe,Headers,start,stop,step, ip, groupName, bandwidth, zeroPos, passes, reverse, repeats):
    #column headers
    Pipe.send(Headers)
    
    print("Connecting to instruments")
    
    # Connect to XPS
    try:
        xps = Inst.XPS(ip)
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
    
    for r in range(repeats):
    
        print("Starting gathering")
        # Setup gathering
        err, msg = xps.InitXPSGathering(groupName, start, step, stop, zeroPos, passes, reverse, bandwidth, lockin.tc)
        
        if err != 0:
            print(err)
            print(msg)
        
        # Run Gathering
        err, msg = xps.RunGathering(groupName, start, step, stop, zeroPos, passes, reverse)
    
        if err != 0:
            print(err)
            print(msg)
    
        # Read Gathering
        data = xps.ReadGathering(start, step, stop, zeroPos, passes, reverse, lockin.sensitivity * 1000)
    
        # Output Data
        for n in range(len(data["Delay"])):
            Pipe.send([float(data["Delay"][n]), float(data["X"][n]), float(data["Y"][n]), float(data["A"][n]), float(data["B"][n]), r])

if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    