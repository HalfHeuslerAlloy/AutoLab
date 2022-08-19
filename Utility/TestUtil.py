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
    name = "test"
    
    def __init__(self, master):
        
        super().__init__(master)
        
        utilTabFrame = tk.Frame(master)
        master.add(utilTabFrame,text="Test")
        
        TestEntryLabel = tk.Label(utilTabFrame,text="X")
        TestEntryLabel.grid(column=0, row=0)
        self.XaxisEntry = tk.Entry(utilTabFrame,width = 10)
        self.XaxisEntry.insert(tk.END,"0")
        self.XaxisEntry.grid(column=0, row=1)
    
        self.update()
    
    def update(self):
        pass
        
        self.after(250,self.update)


if __name__=="__main__":
    
    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 595)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()