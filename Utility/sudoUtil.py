# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 11:05:24 2026

@author: csk42 

Utility for calling commands from the front panel
"""

import tkinter as tk
from tkinter import ttk
import pyvisa
import Instruments as Inst
import pkgutil
from inspect import signature
import re


class Util(tk.Frame):
    
    def __init__(self, master, parent=None):
        super().__init__(master)
        
        self.name="Manual Control"
        sudoTab=tk.Frame(master)
        master.add(sudoTab,text="Manual Control")
        
        try:
            self.addresses=parent.address_list
        except AttributeError:
            #if there is no address list, then make your own list
            rm=pyvisa.ResourceManager()
            self.addresses=rm.list_resources()
            rm.close()
        self.addresses.insert(0, "GPIB Address")
        self.Comlabel=tk.Label(sudoTab,text="Visa Address")
        self.Comlabel.grid(column=0,row=0)
        self.Com=tk.StringVar(sudoTab,"GPIB Address")
        self.ComEntry=ttk.OptionMenu(sudoTab,self.Com,*self.addresses)
        self.ComEntry.grid(column=0,row=1)
        
        self.Instlabel=tk.Label(sudoTab, text="Active Instrument")
        self.Instlabel.grid(column=1, row=0)
        Loaded_instruments=[f for _ ,f, _ in pkgutil.iter_modules(["Instruments"]) if f != "Instrument_class"]
        Loaded_instruments.insert(0, "Select Instrument")
        #list the things loaded into the instrument modules. 
        self.Devices=tk.StringVar(sudoTab,"Select Instrument")
        #need to add in a default value, as otherwise ttk Optionmenu takes the 1st element as the default and deletes the 1st element of the list
        self.Device_Menu=ttk.OptionMenu(sudoTab, self.Devices, *Loaded_instruments)
        self.Device_Menu.grid(column=1, row=1)
        self.Devices.trace_add("write", self.change_device)#Add trace to the instrument so that we can populate the function list!
        #Call the functions from the loaded module
        self.Function_Label=tk.Label(sudoTab, text="Instrument Function")
        self.Function=tk.StringVar(sudoTab,"Select Function")
        self.Function_Label.grid(column=2,row=0)
        self.FunctionList=["Please Select an Instrument","PLEASE!!!"]
        self.Function_Menu=ttk.OptionMenu(sudoTab, self.Function, *self.FunctionList)#use ttk Optionmenu in order to use the handy .setmenu option
        self.Function_Menu.grid(column=2, row=1)
        
        print(self.Function_Menu.keys())
        
        #Input the parameters
        self.Input_Label=tk.Label(sudoTab, text="Parameter Entry")
        self.Input_Label.grid(column=0,row=2)
        self.Input_Text=tk.Entry(sudoTab, width=30)
        self.Input_Text.insert(tk.END, "Parameters for function")
        self.Input_Text.grid(column=1, row=2, columnspan=2)
        
        self.Return_Label=tk.Label(sudoTab, text="Parameter Return")
        self.Return_Label.grid(column=0,row=3)

        self.Return_Message=tk.Message(sudoTab, relief="sunken", text="Returned Parameter", width=1000)
        self.Return_Message.grid(column=1, row=3, columnspan=6)
        #Button to 
        self.Activate_button=tk.Button(sudoTab,
                                         text = "Execute Commands",
                                         bg = "red",
                                         command = self.Activate
                                         )
        self.Activate_button.grid(column=4,row=1)
        
        self.Connect_button=tk.Button(sudoTab,
                                         text = "Connect",
                                         command = self.Connect
                                         )
        self.Connect_button.grid(column=4,row=0)
        
        self.is_connected=False
        
    def change_device(self,var,index,mode):
        """
        Populate the Function list with the functions from the selected device.
        Parameters are tk nonsense. Not used

        """
        New_Device=self.Devices.get()
        #self.Function_Menu["menu"].delete(0,"end")#clear Function_Menu
        function_list=dir(getattr(Inst,New_Device))#get a list of functions in the module
        function_list.insert(0,"Select a Function")
        self.Function_Menu.set_menu(*[f for f  in function_list  if f[0]!="_"])
        #filter the functions so that we ignore builtin functions and the attributes (i.e lockin.X)
    
        
    def Activate(self):
        function=self.Function.get()
        if self.is_connected == True and function !="Select a Function":
            func_parameters=list(signature(getattr(self.active_Device, function)).keys())
            #get a list of the paramerters required from the function
            if len(func_parameters) >= 1:
                #if the function requires parameters, get the input from the textbox
                message_to_send=self.Input_Text.get()
                message_to_send=re.split(",",message_to_send)#should now have a list separated by commas
                if len(func_parameters) != len(message_to_send):
                    self.Return_Message["text"]=("Failed to {0}, expected {1} parameters, got {2}".format(function,len(func_parameters),len(message_to_send)))
                else:#now that we've confirmed we've got the correct number of parameters...
                #NB: This will require you to set OPTIONAL parameters as well
                    try:
                        output=getattr(self.active_Device, function)(*message_to_send)
                        if output is not None:
                            self.Return_Message["text"]=str(output)#output any results to the textbox
                    except Exception as e:
                        self.Return_Message["text"]=e#at this point theres an issue with what was sent. This should be readable here
            else:
                try:
                    output=getattr(self.active_Device, function)()#no parameters required, no problem
                    if output is not None:
                        self.Return_Message["text"]=str(output)#output any results to the textbox
                except Exception as e:
                    self.Return_Message["text"]=e#at this point theres an issue with what was sent. This should be readable here
        else:
            self.Return_Message["text"]="I can't do a function that doesnt exist to an instrument that isnt there! Give me a break!!"
            
        
    def Connect(self):
        """
        Connect to the device using the parameters given from the menu and initialise the resource manager
        """
        self.rm=pyvisa.ResourceManager()
        if self.Com.get() != "GPIB Address" and self.Devices.get() != "Select Instrument": 
            #only does something if you have selected an address+instrument from dropdown
            try:
                self.active_Device=getattr(Inst, self.Devices.get())(self.rm, self.Com.get())#initialise device
                self.Connect_button.configure(text="Disconnect",command=self.Disconnect)
                self.is_connected=True
                self.Activate_button.configure(bg="green")
                
            except Exception as e:
                self.Return_Message["text"]=("Failed to connect to {0} on address {1}".format(self.Devices.get(),self.Com.get()))
                print(e)
                
    def Disconnect(self):
        """
        Disconnect from the active instrument and close the resource manager

        """
        try:
            del(self.active_Device)#close the instrument
            del(self.rm)
            self.is_connected=False
            self.Connect_button.configure(text="Connect",command=self.Connect)
            self.Activate_button.configure(bg="red")
        except Exception as e:
            print("Failed to close instrument!!")
            print(e)