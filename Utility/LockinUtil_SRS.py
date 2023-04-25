# -*- coding: utf-8 -*-
"""
Utitily Tab for Configuring SRS830 Lockins
Created on Tue Apr 25 12:27:31 2023

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
                "200 mV/nA","500 mV/nA","1 V/uA"] 
    
    TCvalues=["10 us","30 us","100 us","300 us","1 ms","3 ms","10 ms","30 ms","100 ms",
              "30 ms","1 s","3 s","10 s","30 s","100 s","300 s",
              "1 ks","3 ks","10 ks","30 ks"]

    
    Off_and_Expo_Values=["Off","Offset X", "Offset Y", "Offset X and Y", 
                         "Offset and Expand X x10", "Offset and Expand Y x10", "Offset and Expand X and Y x10",
                         "Offset and Expand X x100", "Offset and Expand Y x100", "Offset and Expand X and Y x100"]
    #No, I'm not making so you can Expand one Channel and Offset the other, are you MAD? 
    #Also Cant think of a scenario where you would want a x10 expand and no Offset. Just change the sensitivity.
    def __init__(self, master,title="Lockin Options",addresses=[]):

        super().__init__(master)
        
        LockinTabFrame = tk.Frame(master)
        master.add(LockinTabFrame,text=title)
        ###LOCKIN NAME GUI ELEMENT###
        self.NameEntry = tk.Entry(LockinTabFrame,width = 10)
        self.NameEntry.insert(tk.END,"Lockin ID")
        self.NameEntry.grid(column=0, row=0)
        ###COMMS GUI Element###
        #want this populated with valid VISA adresses but dont want a dangling resource manager,
        #SO
        if len(addresses)==0:
            rm=pyvisa.ResourceManager()
            addresses=rm.list_resources()
            rm.close()
        #if addresses are supplied through the script which calls this util, we dont need to poll all instruments
        #speeds up loading the util
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
        self.XOFFEntry.grid(column=1, row=3)
        self.YOFFEntry = tk.Entry(LockinTabFrame,width = 10)
        self.YOFFEntry.insert(tk.END,"Y-Offset(%)")
        self.YOFFEntry.grid(column=2, row=3)
        self.Offset_option=tk.StringVar(LockinTabFrame,"Apply Offsets?")
        self.SetOffset_Menu=tk.OptionMenu(LockinTabFrame, self.Offset_option, *self.Off_and_Expo_Values)
        self.SetOffset_Menu.grid(column=2,row=4)
        
        self.ApplyButton = tk.Button(LockinTabFrame,
                                         text = "Configure Now",
                                         bg = "red",
                                         command = self.configure,
                                         )
        self.ApplyButton.grid(column = 4, row = 0)
        
        self.update()
    #TODO: Write in a seperate "Connect" Button that populates the Menus Automatically
    #For now, if a default option is selected in the drop-downs or no offset is entered, 
    #The values will not be altered. BUT, Adrresses need to be set or everything Falls over.
    def configure(self):
        rm=pyvisa.ResourceManager()
        address=self.Com.get()
        is_default=[True,True,True]
        #list of bools to see if we need to send values to the Lockin
        #Currently in the order Sensitivity,TC,EnableOffset/Expand.
        #Feel Free to add more, but the list (and try/except statements) will need expanding.
        #T=no need to update F=Parameter Needs Updating.
        try:
            sens_to_send=(self.Sensvalues.index(self.Sensitivity.get())) 
            is_default[0]=False
        except ValueError:
            print("Did Not Update Sensitivity")
        try:
            TC_to_send=self.TCvalues.index(self.TC.get())
            is_default[1]=False
        except ValueError:
            print("Did Not Update Time Constant")

            
        try:
            ApplyExpands=self.Off_and_Expo_Values.index(self.Offset_option.get())
            is_default[2]=False
        except ValueError:
            print("Did Not Change Offset/Expand Setting") 
        X_OffToSend=0
        Y_OffToSend=0
        if is_default[2]==False:
            try:
                X_OffToSend=float(float(self.XOFFEntry.get()))
            except ValueError:
                print("Did Not Change X Offset")
            try:
                Y_OffToSend=float(float(self.YOFFEntry.get()))
            except ValueError:
                print("Did Not Change Y offset")
            
            if X_OffToSend and Y_OffToSend == 0:
                print("No Valid Offsets Detected, Did Not Apply Offset/Expand Setting")
                is_default[2]=True
        
        #ACTUAL CONNECTING TO THE INSTRUMENT SECTION
        try:
            lockin=Inst.SR830(rm,address)
            for x in range(0,len(is_default)):
                if is_default[x] == True:
                    pass# handles the not-updating
                elif x==0:
                    lockin.setSEN(str(sens_to_send))
                elif x==1:
                    lockin.setTC(str(TC_to_send))
                elif x==2:#WARNING! COLLAPSE THIS OR GAZE INTO SATAN'S ELIF STATEMENTS
                    if ApplyExpands==0:
                        lockin.setX_OffExp(0)
                        lockin.setY_OffExp(0)#sends an offset of 0 which turns off the offset
                    elif ApplyExpands==1:
                        lockin.setX_OffExp(X_OffToSend)
                        lockin.setY_OffExp(0)
                    elif ApplyExpands==2:
                        lockin.setX_OffExp(0)
                        lockin.setY_OffExp(Y_OffToSend)
                    elif ApplyExpands==3:
                        lockin.setX_OffExp(X_OffToSend)
                        lockin.setY_OffExp(Y_OffToSend)
                    elif ApplyExpands==4:
                        lockin.setX_OffExp(X_OffToSend,1)
                        lockin.setY_OffExp(0)
                    elif ApplyExpands==5:
                        lockin.setX_OffExp(0)
                        lockin.setY_OffExp(Y_OffToSend,1)
                    elif ApplyExpands==6:
                        lockin.setX_OffExp(X_OffToSend,1)
                        lockin.setY_OffExp(Y_OffToSend,1)
                    elif ApplyExpands==7:
                        lockin.setX_OffExp(X_OffToSend,2)
                        lockin.setY_OffExp(0)
                    elif ApplyExpands==8:
                        lockin.setX_OffExp(0)
                        lockin.setY_OffExp(Y_OffToSend,2)
                    elif ApplyExpands==9:
                        lockin.setX_OffExp(X_OffToSend,2)
                        lockin.setY_OffExp(Y_OffToSend,2)
            #given that kludge, may want to consider putting offset and expand on seperate
            #options, but Tab is cluttered as is!
            self.ApplyButton.configure(bg="green")
        except Exception as e:
            print(e)
            print("Failed to configure SRS830 Lockin")
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
        Lockin_Manager=Inst.SR830(rm,address)
        #create Metadata Dictionary
        Metadata={}
        Metadata["Name"]=self.NameEntry.get()
        Metadata["Sensitivity"]=self.Sensvalues[int(Lockin_Manager.getSens())]
        Metadata["Time_Constant"]=self.TCvalues[int(Lockin_Manager.getTCons())]
        XOff=Lockin_Manager.getX_OffExp()
        YOff=Lockin_Manager.getY_OffExp()
        Phas=Lockin_Manager.getRefPhase()
        if  XOff[0]!=0.0:
            Metadata["XOffset"]=XOff[0]
        if YOff[0]!=0.0:
            Metadata["YOffset"]=YOff[0]
        if Phas != 0:
            Metadata["PhaseOffset"]=Phas
        if XOff[1]==1:
            Metadata["XExpand"]="x10"
        if XOff[1]==2:
            Metadata["XExpand"]="x100"
        if YOff[1]==1:
            Metadata["YExpand"]="x10"
        if YOff[1]==2:
            Metadata["YExpand"]="x100"
        rm.close()#cleanup
        return(Metadata)
        
        #self.after(250,self.update)


if __name__=="__main__":
    
    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 595)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()