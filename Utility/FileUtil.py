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
        
        OverwriteFrame = tk.Frame(FileUtilTab)
        OverwriteFrame.pack(side=tk.LEFT)
        
        self.fileMakeOption = tk.StringVar(None,"A")
        
        AutoEnumerateOption = ttk.Radiobutton(OverwriteFrame,
                                              text="Auto Enumerate         ",
                                              variable=self.fileMakeOption,
                                              value="A")
        AutoEnumerateOption.pack(anchor="w")
        
        OverwriteOption = ttk.Radiobutton(OverwriteFrame,
                                          text="Overwrite",
                                          variable=self.fileMakeOption,
                                          value="O")
        OverwriteOption.pack(anchor="w")
        
        
        DelimiterFrame = tk.Frame(FileUtilTab)
        DelimiterFrame.pack(side=tk.LEFT)
        
        # Defaults to 4 spaces
        self.delimiterOption = tk.StringVar(None,"    ")
        
        SpaceOption = ttk.Radiobutton(DelimiterFrame,
                                          text="4 Spaces",
                                          variable=self.delimiterOption,
                                          value="    ")
        SpaceOption.pack(anchor="w")
        
        CommaOptionOption = ttk.Radiobutton(DelimiterFrame,
                                              text="Comma ,",
                                              variable=self.delimiterOption,
                                              value=",")
        CommaOptionOption.pack(anchor="w")
        
        TabOptionOption = ttk.Radiobutton(DelimiterFrame,
                                              text="Tabs",
                                              variable=self.delimiterOption,
                                              value="\t")
        TabOptionOption.pack(anchor="w")


if __name__=="__main__":
    
    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 595)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()