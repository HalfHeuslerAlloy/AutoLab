# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 16:02:22 2022

@author: eenmv
"""
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont

import matplotlib.pyplot as plot

class Util(tk.Frame):
    """
    Test utility function
    """
    
    #Name of utility so it can e refer to later as part of a dictionary
    name = "Graph"
    
    def __init__(self, master):
        
        super().__init__(master)
        
        GraphUtilTab = tk.Frame(master)
        master.add(GraphUtilTab,text="Graph Settings")
        
        XaxisEntryLabel = tk.Label(GraphUtilTab,text="X")
        XaxisEntryLabel.grid(column=0, row=0)
        self.XaxisEntry = tk.Entry(GraphUtilTab,width = 10)
        self.XaxisEntry.insert(tk.END,"0")
        self.XaxisEntry.grid(column=0, row=1)
        
        Y1axisEntryLabel = tk.Label(GraphUtilTab,text="Y")
        Y1axisEntryLabel.grid(column=1, row=0)
        self.Y1axisEntry = tk.Entry(GraphUtilTab,width = 10)
        self.Y1axisEntry.insert(tk.END,"1")
        self.Y1axisEntry.grid(column=1, row=1)
        
        Y2axisEntryLabel = tk.Label(GraphUtilTab,text="Z")
        Y2axisEntryLabel.grid(column=2, row=0)
        self.Y2axisEntry = tk.Entry(GraphUtilTab,width = 10)
        self.Y2axisEntry.insert(tk.END,"2")
        self.Y2axisEntry.grid(column=2, row=1)
        
        self.Autoscale = tk.IntVar()
        self.Autoscale.set(True)
        AutoscaleCheck = tk.Checkbutton(GraphUtilTab,text="Autoscale",variable=self.Autoscale)
        AutoscaleCheck.grid(column=0, row=2)


if __name__=="__main__":
    
    #Creates a dummy to test loading of data
    class dummy():
        def __init__(self):
            
            x = np.linspace(-5, 5, 26)
            y = np.linspace(-5, 5, 26)
            
            xx, yy = np.meshgrid(x, y)
            
            zz = np.sqrt(xx**2 + yy**2)
            
            xx = xx.flatten()
            yy = yy.flatten()
            zz = zz.flatten()
            
            self.Data = np.transpose(np.array([xx,yy,zz]))
    
    Experiment = dummy()
    
#    Data = Experiment.Data
#    
#    Data = np.transpose(Data)
#    
#    x = Data[0]
#    y = Data[1]
#    z = Data[2]
#    
    plot = plot.tricontourf([0,1,2],[1,2,0],[4,5,6])
    
    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 595)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()