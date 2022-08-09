# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 16:02:22 2022

@author: eenmv
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import font as tkFont

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
        
        Y1axisEntryLabel = tk.Label(GraphUtilTab,text="Y1")
        Y1axisEntryLabel.grid(column=1, row=0)
        self.Y1axisEntry = tk.Entry(GraphUtilTab,width = 10)
        self.Y1axisEntry.insert(tk.END,"1")
        self.Y1axisEntry.grid(column=1, row=1)
        
        Y2axisEntryLabel = tk.Label(GraphUtilTab,text="Y2")
        Y2axisEntryLabel.grid(column=2, row=0)
        self.Y2axisEntry = tk.Entry(GraphUtilTab,width = 10)
        self.Y2axisEntry.insert(tk.END,"2")
        self.Y2axisEntry.grid(column=2, row=1)
        
        self.Autoscale = tk.IntVar()
        self.Autoscale.set(True)
        AutoscaleCheck = tk.Checkbutton(GraphUtilTab,text="Autoscale",variable=self.Autoscale)
        AutoscaleCheck.grid(column=0, row=2)


if __name__=="__main__":
    
    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 495)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()