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
        
        self.RotationFrame = tk.Frame(master)
        self.RotationFrame.grid(column=0, row=1, columnspan=3, rowspan=3)
        master.add(self.RotationFrame,text="Rotation Settings")
        
        self.XPSFrame = tk.Frame(master)
        self.XPSFrame.grid(column=0, row=1, columnspan=3, rowspan=3)
        master.add(self.XPSFrame,text="XPS Settings")
        
        self.XPSRotationFrame = tk.Frame(master)
        self.XPSRotationFrame.grid(column=0, row=1, columnspan=3, rowspan=3)
        master.add(self.XPSRotationFrame,text="XPS Rotation Settings")
        
        """
        Utilities Section
        """
        
        
        """
        Data Format Section
        """
        self.Header_List=["Delay","L1_X", "L1_Y", "L2_X", "L2_Y", "Repeat", "Angle"]
        
        """
        Initial setup of GUI widgets and the general window position
        """
        
        ## Delay Controls
        StartDelayEntryLabel = tk.Label(self.MainFrame,text="Start")
        StartDelayEntryLabel.pack()
        self.StartDelayEntry = tk.Entry(self.MainFrame,width = 10)
        self.StartDelayEntry.insert(tk.END,"0")
        self.StartDelayEntry.pack()

        
        StopDelayEntryLabel = tk.Label(self.MainFrame,text="Stop")
        StopDelayEntryLabel.pack()
        self.StopDelayEntry = tk.Entry(self.MainFrame,width = 10)
        self.StopDelayEntry.insert(tk.END,"10")
        self.StopDelayEntry.pack()
        
        StepDelayEntryLabel = tk.Label(self.MainFrame,text="Step")
        StepDelayEntryLabel.pack()
        self.StepDelayEntry = tk.Entry(self.MainFrame,width = 10)
        self.StepDelayEntry.insert(tk.END,"0.03")
        self.StepDelayEntry.pack()
        
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
        
        #Rotation Controls
        
        StartAngleEntryLabel = tk.Label(self.RotationFrame,text="Start")
        StartAngleEntryLabel.pack()
        self.StartAngleEntry = tk.Entry(self.RotationFrame,width = 10)
        self.StartAngleEntry.insert(tk.END,"0")
        self.StartAngleEntry.pack()

        
        StopAngleEntryLabel = tk.Label(self.RotationFrame,text="Stop")
        StopAngleEntryLabel.pack()
        self.StopAngleEntry = tk.Entry(self.RotationFrame,width = 10)
        self.StopAngleEntry.insert(tk.END,"360")
        self.StopAngleEntry.pack()
        
        StepAngleEntryLabel = tk.Label(self.RotationFrame,text="Step")
        StepAngleEntryLabel.pack()
        self.StepAngleEntry = tk.Entry(self.RotationFrame,width = 10)
        self.StepAngleEntry.insert(tk.END,"15")
        self.StepAngleEntry.pack()
        
        
        # XPS Delay Controls
        
        IPDelayEntryLabel = tk.Label(self.XPSFrame,text="IP Address")
        IPDelayEntryLabel.pack()
        self.IPDelayEntry = tk.Entry(self.XPSFrame,width = 20)
        self.IPDelayEntry.insert(tk.END,"192.168.0.77")
        self.IPDelayEntry.pack()
        
        GroupDelayEntryLabel = tk.Label(self.XPSFrame,text="Group Name")
        GroupDelayEntryLabel.pack()
        self.GroupDelayEntry = tk.Entry(self.XPSFrame,width = 20)
        self.GroupDelayEntry.insert(tk.END,"Group4.Pos")
        self.GroupDelayEntry.pack()
        
        ZPDelayEntryLabel = tk.Label(self.XPSFrame,text="Zero Position (ps)")
        ZPDelayEntryLabel.pack()
        self.ZPDelayEntry = tk.Entry(self.XPSFrame,width = 10)
        self.ZPDelayEntry.insert(tk.END,"184")
        self.ZPDelayEntry.pack()
        
        PassDelayEntryLabel = tk.Label(self.XPSFrame,text="Passes")
        PassDelayEntryLabel.pack()
        self.PassDelayEntry = tk.Entry(self.XPSFrame,width = 10)
        self.PassDelayEntry.insert(tk.END,"2")
        self.PassDelayEntry.pack()
        
        self.ReverseDelayCheckVar = tk.IntVar()
        
        self.ReverseDelayCheck = tk.Checkbutton(self.XPSFrame, variable=self.ReverseDelayCheckVar, text="Reverse", onvalue=1, offvalue=0)
        self.ReverseDelayCheck.pack()
        
        
        # XPS Rotation Controls
        
        IPAngleEntryLabel = tk.Label(self.XPSRotationFrame,text="IP Address")
        IPAngleEntryLabel.pack()
        self.IPAngleEntry = tk.Entry(self.XPSRotationFrame,width = 20)
        self.IPAngleEntry.insert(tk.END,"192.168.0.77")
        self.IPAngleEntry.pack()
        
        GroupEntryAngleLabel = tk.Label(self.XPSRotationFrame,text="Group Name")
        GroupEntryAngleLabel.pack()
        self.GroupAngleEntry = tk.Entry(self.XPSRotationFrame,width = 20)
        self.GroupAngleEntry.insert(tk.END,"Group1.Pos")
        self.GroupAngleEntry.pack()
        
        ZPAngleEntryLabel = tk.Label(self.XPSRotationFrame,text="Zero Position (ps)")
        ZPAngleEntryLabel.pack()
        self.ZPAngleEntry = tk.Entry(self.XPSRotationFrame,width = 10)
        self.ZPAngleEntry.insert(tk.END,"-7")
        self.ZPAngleEntry.pack()
        
        PassAngleEntryLabel = tk.Label(self.XPSRotationFrame,text="Passes")
        PassAngleEntryLabel.pack()
        self.PassAngleEntry = tk.Entry(self.XPSRotationFrame,width = 10)
        self.PassAngleEntry.insert(tk.END,"0.3")
        self.PassAngleEntry.pack()
        
        self.ReverseAngleCheckVar = tk.IntVar()
        
        self.ReverseAngleCheck = tk.Checkbutton(self.XPSRotationFrame, variable=self.ReverseAngleCheckVar, text="Reverse", onvalue=1, offvalue=0)
        self.ReverseAngleCheck.pack()



    def Start(self,Pipe):
        
        start_delay  = float(self.StartDelayEntry.get())
        stop_delay  = float(self.StopDelayEntry.get())
        step_delay = float(self.StepDelayEntry.get())
        
        start_angle  = float(self.StartAngleEntry.get())
        stop_angle  = float(self.StopAngleEntry.get())
        step_angle = float(self.StepAngleEntry.get())
        
        ip_delay = self.IPDelayEntry.get()
        groupName_delay = self.GroupDelayEntry.get()
        bandwidth = float(self.BandwidthEntry.get())
        zeroPos_delay = float(self.ZPDelayEntry.get())
        passes_delay = float(self.PassDelayEntry.get())
        reverse_delay = bool(self.ReverseDelayCheckVar.get())
        
        ip_angle = self.IPAngleEntry.get()
        groupName_angle = self.GroupAngleEntry.get()
        zeroPos_angle = float(self.ZPAngleEntry.get())
        passes_angle = float(self.PassAngleEntry.get())
        reverse_angle = bool(self.ReverseAngleCheckVar.get())
        
        repeats = int(self.RepeatsEntry.get())
                
        try:
            self.Worker = Process(target=Worker, args=(Pipe,self.Header_List,start_delay,stop_delay,step_delay, start_angle, stop_angle, step_angle, ip_delay, groupName_delay, bandwidth, zeroPos_delay, passes_delay, reverse_delay, ip_angle, groupName_angle, zeroPos_angle, passes_angle, reverse_angle, repeats))
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
    

        
def Worker(Pipe,Headers,start_delay,stop_delay,step_delay, start_angle, stop_angle, step_angle, ip_delay, groupName_delay, bandwidth, zeroPos_delay, passes_delay, reverse_delay, ip_angle, groupName_angle, zeroPos_angle, passes_angle, reverse_angle, repeats):
    #column headers
    Pipe.send(Headers)
    
    print("Connecting to instruments")
    
    # Connect to XPS
    try:
        xps = Inst.XPS(ip_delay)
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
    
    
    for a in np.arange(start_angle, stop_angle+step_angle, step_angle):
        
        # Move rotation mount
        xps.xps.move_stage(groupName_angle, a)
        
        for r in range(repeats):
    
            print("Starting gathering")
            # Setup gathering
            err, msg = xps.InitXPSGathering(groupName_delay, start_delay, step_delay, stop_delay, zeroPos_delay, passes_delay, reverse_delay, bandwidth, lockin.tc)
            
            if err != 0:
                print(err)
                print(msg)

            # Run Gathering
            err, msg = xps.RunGathering(groupName_delay, start_delay, step_delay, stop_delay, zeroPos_delay, passes_delay, reverse_delay)
            
            if err != 0:
                print(err)
                print(msg)
                
            # Read Gathering
            data = xps.ReadGathering(start_delay, step_delay, stop_delay, zeroPos_delay, passes_delay, reverse_delay, lockin.sensitivity * 1000)
                
            # Output Data
            for n in range(len(data["Delay"])):
                Pipe.send([float(data["Delay"][n]), float(data["X"][n]), float(data["Y"][n]), float(data["A"][n]), float(data["B"][n]), r, float(a)])

if __name__=="__main__":
    root = tk.Tk()
    Expirment = Handler(root)
    Expirment.mainloop()
    