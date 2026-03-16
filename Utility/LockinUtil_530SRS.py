# -*- coding: utf-8 -*-
"""
Utility tab for configuring Olde SRS530 Lockins
Created on Fri Mar  6 15:14:19 2026

@author: csk42
TODO: As with the 
"""

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
import numpy as np

import pyvisa
import Instruments as Inst

class Util(tk.Frame):
    
    name="Lockin"
    
    TCvalues=["1 ms","3 ms","10 ms","30 ms","100 ms",
              "300 ms","1 s","3 s","10 s","30 s","100 s"]
    
    Sensvalues=["10 nV", "20 nV", "50 nV", "100 nV", "200 nV", "500 nV",
                "1 uV", "2 uV", "5 uV","10 uV", "20 uV", "50 uV", "100 uV", "200 uV", "500 uV",
                "1 mV", "2 mV", "5 mV","10 mV", "20 mV", "50 mV", "100 mV", "200 mV", "500 mV"]
    
    Off_and_Expo_Values=["Off","Offset X", "Offset Y", "Offset X and Y", 
                         "Offset and Expand X x10", "Offset and Expand Y x10", "Offset and Expand X and Y x10"]
    
    NotchValues=["Off","Line filter", "Double-Line filter", "Both Linefilters"]
    
    Reserve_Values=["Low Noise", "Normal", "High Reserve"]
    
    Slope_Values=["1 Hz", "10 Hz"]
    
    def __init__(self, master,title="Lockin Options",addresses=[]):

        super().__init__(master)
        self.title=title
        LockinTabFrame = tk.Frame(master)
        master.add(LockinTabFrame,text=title)
        ###LOCKIN NAME GUI ELEMENT###
        self.Name=tk.StringVar(LockinTabFrame,"Lockin ID")
        self.NameEntry = tk.Entry(LockinTabFrame,textvariable=self.Name, width = 10)
        self.NameEntry.grid(column=0, row=0)
        ###COMMS GUI Element###

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
        self.XOFFEntry.grid(column=0, row=3)
        self.YOFFEntry = tk.Entry(LockinTabFrame,width = 10)
        self.YOFFEntry.insert(tk.END,"Y-Offset(%)")
        self.YOFFEntry.grid(column=1, row=3)
        self.Offset_option=tk.StringVar(LockinTabFrame,"Apply Offsets?")
        self.SetOffset_Menu=tk.OptionMenu(LockinTabFrame, self.Offset_option, *self.Off_and_Expo_Values)
        self.SetOffset_Menu.grid(column=2,row=3)
        
        ###FILTER GUI ELEMENTS###
        self.NotchOption=tk.StringVar(LockinTabFrame,"Line Filters")
        self.SetNotch_Menu=tk.OptionMenu(LockinTabFrame,self.NotchOption , *self.NotchValues)
        self.SetNotch_Menu.grid(column=0, row=4)
        self.SlopeOption=tk.StringVar(LockinTabFrame,"Filter Slope")
        self.SetSlope_Menu=tk.OptionMenu(LockinTabFrame,self.SlopeOption , *self.Slope_Values)
        self.SetSlope_Menu.grid(column=1,row=4)
        self.ReserveOption=tk.StringVar(LockinTabFrame,"Dynamic Reserve")
        self.Reserve_Menu=tk.OptionMenu(LockinTabFrame, self.ReserveOption, *self.Reserve_Values)
        self.Reserve_Menu.grid(column=2,row=4)        
        
        self.ApplyButton = tk.Button(LockinTabFrame,
                                         text = "Configure Now",
                                         bg = "red",
                                         command = self.configure,
                                         )
        self.ApplyButton.grid(column = 4, row = 5)
        
        self.update()
        
        
    def configure(self):
        rm=pyvisa.ResourceManager()
        address=self.Com.get()
        is_default=[True,True,True,True,True,True]
        #list of bools to see if we need to send values to the Lockin
        #Currently in the order Sensitivity,TC,EnableOffset/Expand/Line Filters/Filter Slope/Dynamic Reserve.
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
        
        try:
            LF_to_send=(self.NotchValues.index(self.NotchOption.get()))
            is_default[3]=False
        except ValueError:
            print("Did not Change LineFilter Setting")
        
        try:
            Slope_to_Send=self.Slope_Values.index(self.SlopeOption.get())
            is_default[4]=False
        except ValueError:
            print("Did not change Filter slope")
        
        try:
            Reserve_to_Send=self.Reserve_Values.index(self.ReserveOption.get())
            is_default[5]=False
        except ValueError:
            print("Did not Change Dynamic Reserve")
        
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
            
            if X_OffToSend ==0 and Y_OffToSend == 0 and ApplyExpands != 0: 
                #if ApplyExpands is 0, we're trying to disable the Offsets, so we need to handle the case where no value has been entered in the Dialogues
                print("No Valid Offsets Detected, Did Not Apply Offset/Expand Setting")
                is_default[2]=True
                
        #ACTUAL CONNECTING TO THE INSTRUMENT SECTION
        try:
            lockin=Inst.SR530(rm,address)
            for x in range(0,len(is_default)):
                if is_default[x] == True:
                    pass# handles the not-updating
                elif x==0:
                    lockin.setSEN(str(sens_to_send))
                elif x==1:
                    lockin.setTC(str(TC_to_send))
                elif x==2:
                    if ApplyExpands == 0:
                        lockin.XOffset()
                        lockin.YOffset()
                        lockin.setExpand()#default options for these are to disable offsets so this makese it easy
                    else:
                        mod=ApplyExpands%3
                        dev=ApplyExpands//4 #lets not redo satans ELIF chain
                        if mod == 1 or mod == 0:
                            lockin.XOFFset(X_OffToSend)
                        if mod==2 or mod==0:#should work if mod=0 i.e offset X and Y
                            lockin.YOffset(Y_OffToSend)
                        if dev ==1:#apply expands now
                            if mod==1:
                                lockin.setExpand(True,False)
                            elif mod==2:
                                lockin.setExpand(False,True)
                            elif mod==0:
                                lockin.setExpand(True,True)
            
                        
                elif x==3:
                    if LF_to_send ==0:
                        lockin.setNotchFilters()
                    elif LF_to_send ==1:
                        lockin.setNotchFilters(True,False)
                    elif LF_to_send == 2:
                        lockin.setNotchFilters(False,True)
                    elif LF_to_send ==3:
                        lockin.setNotchFilters(True,True)
                elif x==4:
                    lockin.setNoiseBW(str(Slope_to_Send))
                elif x==5:
                    lockin.setReserve(str(Reserve_to_Send))
                        
                self.ApplyButton.configure(bg="green")
        except Exception as e:
            print(e)
            print("Failed to configure SRS530 Lockin")
            rm.close()#cleanup    
            return False
    
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
        Lockin_Manager=Inst.SR530(rm,address)
        #create Metadata Dictionary
        Metadata={}
        Metadata["Instrument"]="Lockin"
        #because unlike other instruments the "Name" is user-defined, want something to Call out that this is a Lockin
        Metadata["Name"]=self.NameEntry.get()
        Metadata["Sensitivity"]=self.Sensvalues[int(Lockin_Manager.getSens())]
        Metadata["Time_Constant"]=self.TCvalues[int(Lockin_Manager.getTCons())]
        current_display=int(Lockin_Manager.getDisplay())
        Lockin_Manager.setDisplay(1)
        XOff=Lockin_Manager.Q1
        YOff=Lockin_Manager.Q2
        Lockin_Manager.setDisplay(current_display)
        #reset the display to the initial value after Offsets have been read
        Expands=Lockin_Manager.getExpands()
        
        Phas=Lockin_Manager.getRefPhase()
        if  XOff!=0.0:
            Metadata["XOffset"]=XOff[0]
        if YOff!=0.0:
            Metadata["YOffset"]=YOff[0]
        if Phas != 0:
            Metadata["PhaseOffset"]=Phas
        if Expands[0]==1:
            Metadata["XExpand"]="x10"
        if Expands[1]==1:
            Metadata["YExpand"]="x10"
        rm.close()#cleanup
        return(Metadata)
            