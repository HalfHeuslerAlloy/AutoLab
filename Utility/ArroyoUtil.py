# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 16:02:22 2022

@author: eenmv
"""

import os 
print(os.getcwd())

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import font as tkFont

import time

try:
    import Instruments as Inst
except:
    pass


class Util(tk.Frame):
    """
    Test utility function
    """
    
    #Name of utility so it can e refer to later as part of a dictionary
    name = "test"
    
    def __init__(self, master,parent=None):
        
        super().__init__(master)
        
        frame = tk.Frame(master)
        
        master.add(frame,text="Arroyo Control")
        
        self.connected = False
        self.Arroyo = None
        
        
        gbipLabel = tk.Label(frame,text="COM Port")
        gbipLabel.grid(column=0, row=0)
        self.gbipEntry = tk.Entry(frame,width = 10)
        self.gbipEntry.insert(tk.END,"6")
        self.gbipEntry.grid(column=0, row=1)
        
        self.ConnStatusLabel = tk.Label(frame,text="Disconnect",bg = "red")
        self.ConnStatusLabel.grid(column=0, row=2)
        
        self.ConnectButton = tk.Button(frame,
                                         text = "Connect",
                                         command = self.Connect,
                                         )
        self.ConnectButton.grid(column = 1, row = 0)
        
        
        self.DisconnectButton = tk.Button(frame,
                                         text = "Disconnect",
                                         command = self.Disconnect,
                                         )
        self.DisconnectButton.grid(column = 1, row = 1)
        
        self.DisconnectButton = tk.Button(frame,
                                         text = "Status",
                                         command = self.Status,
                                         )
        self.DisconnectButton.grid(column = 1, row = 2)
        
        

    
    def Connect(self):
        pass
    
    def Disconnect(self):
        pass
    def Status(self):
        pass
    
    def update(self):
        pass
    
        self.after(101,self.update)


if __name__=="__main__":

    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 595)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()