# -*- coding: utf-8 -*-
"""
Utitily Tab for Configuring DSP_7265 Lockins
Created on Thu Jul 21 16:02:22 2022

@author: eencsk
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
                "200 mV/nA","500 mV/nA","1 V/uA"]#Doesnt include the Low-noise current settings. 
    
    TCvalues=["10 us","20 us","40 us","60 us","80 us","160 us","320 us","640 us",
              "5 ms","10 ms","20 ms","50 ms","100 ms","200 ms","500 ms","1 s",
              "2 s","5 s","10 s","20 s","50 s","100 s","200 s","500 s","1 Ks",
              "2 Ks","5 Ks","10 Ks","20 Ks","50 Ks","100 Ks"]
    
    Off_and_Expo_Values=["Off","Offset X", "Offset Y", "Offset X and Y",
                         "Expand X", "Expand Y", "Expand X and Y", 
                         "Offset and Expand X", "Offset and Expand Y", "Offset and Expand X and Y"]
    #No, I'm not making so you can Expand one Channel and Offset the other, are you MAD?
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
        self.Com=tk.StringVar(LockinTabFrame,"GPIB Address")
        self.ComEntry=tk.OptionMenu(LockinTabFrame,self.Com,*addresses)
        self.ComEntry.grid(column=0,row=1)
        
        ###SENSITIVITY GUI ELEMENT###
        SenEntryLabel = tk.Label(LockinTabFrame,text="Sensitivity")
        SenEntryLabel.grid(column=1, row=0)
        self.Sensitivity=tk.StringVar(LockinTabFrame,"Enter Sensitivity")
        self.SenEntry=tk.OptionMenu(LockinTabFrame, self.Sensitivity, *self.Sensvalues)
        #asterix is a packing argument, so will accept elements in array as seperate arguments
        #rather than as a single "1 2 3 4" argument as will be the case otherwise
        self.SenEntry.grid(column=2, row=0)
        ###TC GUI ELEMENT###
        TCEntryLabel = tk.Label(LockinTabFrame,text="Time Constant")
        TCEntryLabel.grid(column=1, row=1)
        self.TC=tk.StringVar(LockinTabFrame,"Enter Time Constant")
        self.TCEntry=tk.OptionMenu(LockinTabFrame, self.TC, *self.TCvalues)
        self.TCEntry.grid(column=2, row=1)
        ###OFFSET GUI ELEMENTS###
        self.XOFFEntry = tk.Entry(LockinTabFrame,width = 10)
        self.XOFFEntry.insert(tk.END,"X-Offset(%)")
        self.XOFFEntry.grid(column=4, row=0)
        self.YOFFEntry = tk.Entry(LockinTabFrame,width = 10)
        self.YOFFEntry.insert(tk.END,"Y-Offset(%)")
        self.YOFFEntry.grid(column=4, row=1)
        self.Offset_option=tk.StringVar(LockinTabFrame,"Set Offset Enable")
        self.SetOffset_Menu=tk.OptionMenu(LockinTabFrame, self.Offset_option, *self.Off_and_Expo_Values)
        self.SetOffset_Menu.grid(column=4,row=2)
        
        self.ApplyButton = tk.Button(LockinTabFrame,
                                         text = "Configure Now",
                                         bg = "red",
                                         command = self.configure,
                                         )
        self.ApplyButton.grid(column = 0, row = 2)
        
        self.update()
    #TODO: Write in a seperate "Connect" Button that populates the Menus Automatically
    #For now, if a default option is selected in the drop-downs or no offset is entered, 
    #The values will not be altered. BUT, Adrresses need to be set or everything Falls over.
    def configure(self):
        rm=pyvisa.ResourceManager()
        address=self.Com.get()
        is_default=[True,True,True,True,True]
        #list of bools to see if we need to send values to the Lockin
        #Currently in the order Sensitivity,TC,XOffset,YOffset,EnableOffset/Expand.
        #Feel Free to add more, but the list (and try/except statements) will need expanding.
        #T=no need to update F=Parameter Needs Updating.
        try:
            sens_to_send=(self.Sensvalues.index(self.Sensitivity.get()))+1 
            #for some reason, starts at 1, not 0
            is_default[0]=False
        except ValueError:
            print("Did Not Update Sensitivity")
        try:
            TC_to_send=self.TCvalues.index(self.TC.get())
            is_default[1]=False
        except ValueError:
            print("Did Not Update Time Constant")

        try:
            XOFF_to_send=float(self.XOFFEntry.get())
            is_default[2]=False
        except ValueError:
            print("Did Not Update X-Offset")
        
        try:
            YOFF_to_send=float(self.YOFFEntry.get())
            is_default[3]=False
        except ValueError:
            print("Did Not Update Y-Offset")
            
        try:
            ApplyExpands=self.Off_and_Expo_Values.index(self.Offset_option.get())
            is_default[4]=False
        except ValueError:
            print("Did Not Change Offset/Expand Setting")    
        
        #ACTUAL CONNECTING TO THE INSTRUMENT SECTION
        try:
            lockin=Inst.DSP_7265(rm,address)
            for x in range(0,len(is_default)):
                if is_default[x] == True:
                    pass# handles the not-updating
                elif x==0:
                    lockin.setSen(str(sens_to_send))
                elif x==1:
                    lockin.setTC(str(TC_to_send))
                elif x==2:
                    if lockin.getXOff()[0]==0.0:
                        lockin.setXOff(XOFF_to_send,False)
                    else:
                        lockin.setXOff(XOFF_to_send,True)
                elif x==3:
                    if lockin.getYOff()[0]==0.0:
                        lockin.setYOff(YOFF_to_send,False)
                    else:
                        lockin.setYOff(YOFF_to_send,True)
                elif x==4:#WARNING! COLLAPSE THIS OR GAZE INTO SATAN'S ELIF STATEMENTS
                    if ApplyExpands==0:
                        lockin.Toggle_Offset(0)
                        lockin.setExp(0)
                    elif ApplyExpands==1:
                        lockin.Toggle_Offset(1)
                        lockin.setExp(0)
                    elif ApplyExpands==2:
                        lockin.Toggle_Offset(2)
                        lockin.setExp(0)
                    elif ApplyExpands==3:
                        lockin.Toggle_Offset(3)
                        lockin.setExp(0)
                    elif ApplyExpands==4:
                        lockin.Toggle_Offset(0)
                        lockin.setExp(1)
                    elif ApplyExpands==5:
                        lockin.Toggle_Offset(0)
                        lockin.setExp(2)
                    elif ApplyExpands==6:
                        lockin.Toggle_Offset(0)
                        lockin.setExp(3)
                    elif ApplyExpands==7:
                        lockin.Toggle_Offset(1)
                        lockin.setExp(1)
                    elif ApplyExpands==8:
                        lockin.Toggle_Offset(2)
                        lockin.setExp(2)
                    elif ApplyExpands==9:
                        lockin.Toggle_Offset(3)
                        lockin.setExp(3)
            #given that kludge, may want to consider putting offset and expand on seperate
            #options, but Tab is cluttered as is!
            self.ApplyButton.configure(bg="green")
        except Exception as e:
            print(e)
            print("Failed to configure DSP 7265 Lockin")
            return False
        rm.close()#cleanup
        
    def Export_MetaData(self):
        """
        Creates a Metadata Dictionary for the Lockin.
        NOTE: CURRENTLY ADDRESS HAS TO BE SET CORRECTLY. IF NOT THEN THIS, AND ALL THINGS
        WILL FALL OVER
            
        Returns:
            Metadata: A Dictionary of Metadata values.
        """
        rm=pyvisa.ResourceManager()
        address=self.Com.get()
        Lockin_Manager=Inst.DSP_7265(rm,address)
        #create Metadata Dictionary
        Metadata={}
        Metadata["Name"]=self.NameEntry.get
        Metadata["Sensitivity"]=self.Sensvalues[int(Lockin_Manager.getSens()-1)]
        Metadata["Time_Constant"]=self.TCvalues[int(Lockin_Manager.getTCons())]
        XOff=Lockin_Manager.getXOff()
        YOff=Lockin_Manager.getXOff()
        Phas=Lockin_Manager.getRefPhase()
        if  XOff[0]!=0.0:
            Metadata["XOffset"]=XOff[1]/100
        if YOff[0]!=0.0:
            Metadata["YOffset"]=YOff[1]/100
        if Phas != 0:
            Metadata["PhaseOffset"]=Phas
        Exp=Lockin_Manager.getExp()
        if Exp==1 or Exp==3:
            Metadata["XExpand"]=True
        else:
            Metadata["XExpand"]=False
        if Exp==2 or Exp==3:
            Metadata["YExpand"]=True
        else:
            Metadata["YExpand"]=False
        
        return(Metadata)
        
        #self.after(250,self.update)


if __name__=="__main__":
    
    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 595)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()