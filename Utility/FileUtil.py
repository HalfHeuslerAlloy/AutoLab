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
    """Creates the utilities tab for controlling how the file should be saved
        """
    
    #Name of utility so it can e refer to later as part of a dictionary
    name = "Graph"
    
    def __init__(self, master):
        
        super().__init__(master)
        
        FileUtilTab = tk.Frame(master)
        master.add(FileUtilTab,text="Save Settings")
        
        
        #TODO - Make this an either/or option
        self.OverrideFile = tk.IntVar()
        OverrideFile = tk.Checkbutton(FileUtilTab,text="Override",variable=self.OverrideFile)
        OverrideFile.pack()
        self.AutoEnumerate = tk.IntVar()
        AutoEnumerate = tk.Checkbutton(FileUtilTab,text="Auto Enumerate",variable=self.AutoEnumerate)
        AutoEnumerate.pack()


if __name__=="__main__":
    
    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 495)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()