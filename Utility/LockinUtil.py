# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 16:02:22 2022

@author: eenmv
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import font as tkFont
import numpy as np

import pyvisa
import Instruments as Inst

class Util(tk.Frame):
    """
    Lockin Config Utility
    """
    
    #Name of utility so it can e refer to later as part of a dictionary
    name = "Lockin"
    Sensvalues=["2 nV/fA","5 nV/fA","10 nV/fA","20 nV/fA","50 nV/fA","100 nV/fA",
                "200 nV/fA","500 nV/fA","1 uV/pA","2 uV/pA","5 uV/pA","10 uV/pA",
                "20 uV/pA","50 uV/pA","100 uV/pA","200 uV/pA","500 uV/pA","1 mV/nA",
                "2 mV/nA","5 mV/nA","10 mV/nA","20 mV/nA","50 mV/nA","100 mV/nA",
                "200 mV/nA","500 mV/nA","1 V/uA"]
    
    TCvalues=["10 us","20 us","40 us","60 us","80 us","160 us","320 us","640 us",
              "5 ms","10 ms","20 ms","50 ms","100 ms","200 ms","500 ms","1 s",
              "2 s","5 s","10 s","20 s","50 s","100 s","200 s","500 s","1 Ks",
              "2 Ks","5 Ks","10 Ks","20 Ks","50 Ks","100 Ks"]
    
    Off_and_Expo_Values=["Off","Offset X", "Offset Y", "Offset X and Y",
                         "Expand X", "Expand Y", "Expand X and Y", 
                         "Offset and Expand X", "Offset and Expand Y", "Offset and Expand X and Y"]
    def __init__(self, master):

        super().__init__(master)
        
        LockinTabFrame = tk.Frame(master)
        master.add(LockinTabFrame,text="Lockin Options")
        ###LOCKIN NAME GUI ELEMENT###
        self.NameEntry = tk.Entry(LockinTabFrame,width = 10)
        self.NameEntry.insert(tk.END,"Lockin ID")
        self.NameEntry.grid(column=0, row=0)
        ###COMMS GUI Element###
        #want this populated with valid VISA adresses but dont want a dangling resource manager,
        #SO
        rm=pyvisa.ResourceManager()
        addresses=rm.list_resources()
        rm.close()
        Com=tk.StringVar(LockinTabFrame,"GPIB Address")
        self.ComEntry=tk.OptionMenu(LockinTabFrame,Com,*addresses)
        self.ComEntry.grid(column=0,row=1)
        
        ###SENSITIVITY GUI ELEMENT###
        SenEntryLabel = tk.Label(LockinTabFrame,text="Sensitivity")
        SenEntryLabel.grid(column=1, row=0)
        Sensitivity=tk.StringVar(LockinTabFrame,"Enter Sensitivity")
        self.SenEntry=tk.OptionMenu(LockinTabFrame, Sensitivity, *self.Sensvalues)
        #asterix is a packing argument, so will accept elements in array as seperate arguments
        #rather than as a single "1 2 3 4" argument as will be the case 
        self.SenEntry.grid(column=2, row=0)
        ###TC GUI ELEMENT###
        TCEntryLabel = tk.Label(LockinTabFrame,text="Time Constant")
        TCEntryLabel.grid(column=1, row=1)
        TC=tk.StringVar(LockinTabFrame,"Enter Time Constant")
        self.TCEntry=tk.OptionMenu(LockinTabFrame, TC, *self.TCvalues)
        self.TCEntry.grid(column=2, row=1)
        
    
        self.update()
    
    def update(self):
        pass
        
        #self.after(250,self.update)


if __name__=="__main__":
    
    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 595)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()