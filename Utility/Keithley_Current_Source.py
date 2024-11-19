# -*- coding: utf-8 -*-
"""
Utility Tab For configuring the 6221 Current Source.
Created on Thu Oct 24 10:48:21 2024

@author: eencsk
"""

import tkinter as tk
from tkinter import ttk
import numpy as np

import pyvisa
import Instruments as Inst

class Util(tk.Frame):
    """
    6221 Config Utility
    """
    Trigger_Channels=["Off","1","2","3","4","5","6"]
    
    def __init__(self, master,title="6221 Options",addresses=[]):

        super().__init__(master)
        self.title=title
        KeithleyFrame = tk.Frame(master)
        master.add(KeithleyFrame,text=title)#add the Util tab to the Master Workbook
        ###COMMS GUI Element###
        #want this populated with valid VISA adresses but dont want a dangling resource manager,
        #SO
        if len(addresses)==0:
            rm=pyvisa.ResourceManager()
            addresses=rm.list_resources()
            rm.close()
        #if addresses are supplied through the script which calls this util, we dont need to poll all instruments
        #speeds up loading the util
        
        #If addresses are still empty, added none
        if len(addresses)==0:
            addresses = ["none"]
        
        self.Com=tk.StringVar(KeithleyFrame,"11")
        #TODO:Populate the GPIB adresses w. the Default system value
        ComLabel=tk.Label(KeithleyFrame,text="GPIB Address")
        ComLabel.grid(column=0,row=0,padx=10)
        self.ComEntry=tk.OptionMenu(KeithleyFrame,self.Com,*addresses)
        self.ComEntry.grid(column=0,row=1,padx=10)
        
        ###TRIGGER GUI ELEMENTS###
        self.Trigger=tk.StringVar(KeithleyFrame,self.Trigger_Channels[3])
        #TODO:Populate the GPIB adresses w. the Default system value
        TriggerLabel=tk.Label(KeithleyFrame,text="Trigger-out Line")
        TriggerLabel.grid(column=1,row=0,padx=10)
        self.TriggerEntry=tk.OptionMenu(KeithleyFrame,self.Trigger,*self.Trigger_Channels)
        self.TriggerEntry.grid(column=1,row=1,padx=10)
        
        Phase_Label=tk.Label(KeithleyFrame,text="Trigger-out Phase")
        Phase_Label.grid(column=1,row=2)
        self.TriggerPhaseEntry = tk.Entry(KeithleyFrame,width = 10)
        self.TriggerPhaseEntry.insert(tk.END,"Trigger_Phase")
        self.TriggerPhaseEntry.grid(column=1, row=3, padx=10)
        
        ###WAVE MODE GUI ELEMENTS###
        AmplitudeLabel=tk.Label(KeithleyFrame,text="Current Amplitude (Amps)")
        AmplitudeLabel.grid(column=0,row=4)
        self.AmplitudeEntry=tk.Entry(KeithleyFrame,width=10)
        self.AmplitudeEntry.insert(tk.END,"Current Amplitude")
        self.AmplitudeEntry.grid(column=0,row=5,padx=10)
        
        OffsetLabel=tk.Label(KeithleyFrame,text="DC Offset (Amps)")
        OffsetLabel.grid(column=1,row=4)
        self.OffsetEntry=tk.Entry(KeithleyFrame,width=10)
        self.OffsetEntry.insert(tk.END,"DC Offset")
        self.OffsetEntry.grid(column=1,row=5,padx=10)
        
        FreqLabel=tk.Label(KeithleyFrame,text="AC Frequency (Hz)")
        FreqLabel.grid(column=2,row=4)
        self.FreqEntry=tk.Entry(KeithleyFrame,width=10)
        self.FreqEntry.insert(tk.END,"Frequency")
        self.FreqEntry.grid(column=2,row=5,padx=10)
        
        self.ApplyButton = tk.Button(KeithleyFrame,
                                         text = "Configure Now",
                                         bg = "red",
                                         command = self.configure,
                                         width=10,height=10)
        self.ApplyButton.grid(column = 4, row = 0,rowspan=5, columnspan=5)
        
        self.update()
        
    def configure(self,rm=None):
        if rm==None:
            rm=pyvisa.ResourceManager()
        address=self.Com.get()
        try:
            try:
                address=int(address)
            except ValueError:
                #handle the case where a GPIB0:: was selected from the dropdown list
                pass
            K=Inst.Keithley6221(rm,address)
            #TODO:Have some way to set either Wave or DC
            K_Line=self.Trigger_Channels.index(self.Trigger.get())
            K.Conf_Ref_Trigger(K_Line)
            #this should always work, as the default value is a valid thing and theres no
            #way to entre a different value
            try:
               TPhase=float(self.TriggerPhaseEntry.get()) 
            except ValueError:
                TPhase=None
                print("Did Not Update 6221 Ref. Phase")
            
            if TPhase!=None:
                K.Ref_Phase(TPhase)
                
            try:
               Amp=float(self.AmplitudeEntry.get()) 
            except ValueError:
                Amp=None
                print("Did Not Update 6221 Current Amplitude")
            
            if Amp!=None:
                K.WaveAmp(Amp)
                         
            try:
               Offs=float(self.OffsetEntry.get()) 
            except ValueError:
                Offs=None
                print("Did Not Update 6221 DC Offset")
            
            if Offs!=None:
                K.Wave_Offset(Offs)
                

            try:
               Freq=float(self.FreqEntry.get()) 
            except ValueError:
                Freq=None
                print("Did Not Update 6221 Frequency")
            
            if Freq!=None:
                K.WaveFrequency(Freq)
            
            K.Start_Wave()
            self.ApplyButton.configure(bg="green")
            rm.close()#clean up
        except Exception as e:
            print(e)
            rm.close()
    
    def Export_MetaData(self):
        """
        Create a dictionary of metadata. 
        Hopefully populating the Util with a default value will make this not fall over
        
        Returns
        -------
        Dictionary of metadata

        """
        rm=pyvisa.ResourceManager()
        address=self.Com.get()
        try:
            address=int(address)
        except ValueError:
            #handle the case where a GPIB0:: was selected from the dropdown list
            pass
        K=Inst.Keithley6221(rm,address)
        Metadata={}
        try:
            Metadata["Instrument"]="Keithley_6221"
            Metadata["6221_Amplitude"]=K.WaveAmp()
            Metadata["6221_Frequency"]=K.WaveFrequency()
            Offset=K.Wave_Offset()
            if float(Offset) != 0:
                Metadata["Offset"]=Offset
            TPhase=K.Ref_Phase()
            if float(TPhase)!=0:
                Metadata["6221_Reference_Phase"]=TPhase
                
        except Exception as e:
            print(e)
        rm.close()    
        return(Metadata)
            
            
            
            