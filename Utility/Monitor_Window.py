# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 17:35:23 2023

@author: eencsk
Class to manage the Temperature Monitoring Window. 
Developed for the green cryostat but should be adaptable

TASKS:
    See if Temperature Control can Monitor an OI503 (Will test isMonitoring==True at same time)
    See if We can disconnect and Reconnect to an Instrument
    See if we can Populate the GUI elements w. the "Read" Button.

TODO:(In order of Importance) 
Make Reconnecting to the Controllers POssible if Incorrect adresses supplied
Stability Criteria for Measurements as a Fn of Temperature
Unshow certain elements in the Monitor window (I.e Stage 1 Temperature)
Methods to Read Controller and Populate GUI with current values of, say, Setpoint
Support for Non-Lakeshore 350 Temperature Controllers

"""
#GUI Packages
import tkinter as tk
from tkinter import ttk
from multiprocessing import Process, Queue, Pipe
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib import ticker
#Instrument Packages
import Instruments as Inst
import pyvisa
#Export/String Packages
import time
import re
import datetime
import csv
from os import path, mkdir
#scripts to handle the temperature controllers themselves. 
from .Temperature_Controllers import*
#Previously just "Controller". Needed as different controllers return things differently.
#NB: COMMAND SYNTAX MUST BE THE SAME


class Mon_Win(tk.Frame):
    """
    Class for the Monitoring window GUI
    """
    Mode_Select=[ "Zone","Open Loop", "Manual PID"]
    SensorInput=["A","B","C","D"]
    TC_Model=["Lakeshore_350","OI_503"]#Temperature controller Models
    TM_Model=["Lakeshore_218", "Lakeshore_350"]#temperature Monitor models
    Heater_Range=["Off","5/2.5 mW","50/25 mW","500/250 mW","5/2.5 W","50/25 W"]#Delete as appropraite when you know the power
    Temperature_Keys=["VTI","Sample","1st Stage","2nd Stage","Magnet 1", "Magnet 2","Helium Pot","Switch Heater"]
    Time_Data=[]
    Temperature_Data=[]
    Plot_Dict={} #Dictionary to append plots into
    Colour_List=["#a10000","#a15000","#a1a100","#626262","#416600","#008141","#008282","#005682","#000056","#2b0057","#6a006a","#77003c"]
    #Totally Innocent Colours to be passed to the plots so they dont randomise the colour every tick. 
    
    
    
    def __init__(self, master,parent,default_addresses):
        #assume that the last element of the Default addresses is the temperature monitor
        super().__init__(master)#adds all the TK objects in
        self.parent=parent
        addresses=self.parent.address_list
        """Set up Temperature Monitoring GUI"""
        self.Window=tk.Toplevel()
        self.Window.title("Temperature Monitoring")
        self.Window.protocol("WM_DELETE_WINDOW",self.close_function)
        
        Control_Frame=tk.Frame(self.Window)#,height = 330,width = 480)
        Control_Frame.grid(column=0, row=1,sticky="E"+"W",columnspan=2)
        if len(addresses)==0:
            rm=pyvisa.ResourceManager()
            addresses=rm.list_resources()
            rm.close()
        #if addresses are supplied through the script which calls this util, we dont need to poll all instruments
        #speeds up loading the util
        self.Model=tk.StringVar(Control_Frame,"Lakeshore_350")
        self.ModelEntry=tk.OptionMenu(Control_Frame, self.Model, *self.TC_Model)
        self.Model.trace_add("write", self.ChangeModel)
        #future-proofing if we want to apply this to, say, HgITCs
        #For now, rely on having the temperature polling being written with the same syntax
        self.ModelEntry.grid(row=0,column=0)
        self.Com=tk.StringVar(Control_Frame,"GPIB Address")
        self.ComEntry=tk.OptionMenu(Control_Frame,self.Com,*addresses)
        self.ComEntry.grid(column=1,row=0)
        
        self.Mode=tk.StringVar(Control_Frame,self.Mode_Select[0])
        self.Mode_Entry=tk.OptionMenu(Control_Frame,self.Mode,*self.Mode_Select)
        self.Mode_Entry.grid(column=3,row=0)
        self.Mode.trace_add("write", self.ChangeMode)
        #when a new mode is selected, automatically update the GUI and send
        #the correct mode to the Controller
        
        self.Range_var=tk.StringVar(Control_Frame,"Heater Range")
        self.range_Entry=tk.OptionMenu(Control_Frame,self.Range_var,*self.Heater_Range)
        self.range_Entry.grid(column=2,row=0)
# =============================================================================
#         HEATER CONTROL WIDGETS
# =============================================================================
        self.setpoint_entry=tk.Entry(Control_Frame)
        self.setpoint_entry.insert(tk.END,"Enter Setpoint")
        self.setpoint_entry.grid(column = 0, row =1)
        self.ramp_enable=tk.BooleanVar(Control_Frame)
        self.ramp_button=tk.Checkbutton(Control_Frame,text="Ramp Setpoint?", variable=self.ramp_enable, onvalue=True, offvalue=False)
        self.ramp_button.grid(column=1,row=1)
        self.ramp_entry=tk.Entry(Control_Frame)
        self.ramp_entry.insert(tk.END,"Enter Ramp Rate")
        self.ramp_entry.grid(column=2,row=1)
        
        #Setup Manual Heater Output, Hidden by default
        self.power_Label=tk.Label(Control_Frame,text="Heater Power")
        self.power_Label.grid(column=0,row=1)
        self.power_Label.grid_remove()
        self.power_Entry=tk.Scale(Control_Frame, from_=0, to=100, length=300, orient="horizontal",tickinterval=10)
        self.power_Entry.grid(column=1,row=1,columnspan=3)
        self.power_Entry.grid_remove()

        
        #setup PID entry for Manual PID Hidden by Default
        self.P_entry=tk.Entry(Control_Frame)
        self.P_entry.insert(tk.END,"Enter P")
        self.I_entry=tk.Entry(Control_Frame)
        self.I_entry.insert(tk.END,"Enter I")
        self.D_entry=tk.Entry(Control_Frame)
        self.D_entry.insert(tk.END,"Enter D")
        self.P_entry.grid(column=1, row=1)
        self.I_entry.grid(column=2, row=1)
        self.D_entry.grid(column=3, row=1)
        self.P_entry.grid_remove()
        self.I_entry.grid_remove()
        self.D_entry.grid_remove()  
        
        #setup Gas Supply bar, Hidden By Default
        self.Gas_Label=tk.Label(Control_Frame,text="Gas Flow")
        self.Gas_Label.grid(column=0,row=2)
        self.Gas_Label.grid_remove()
        self.Gas_Entry=tk.Scale(Control_Frame, from_=0, to=100, length=300, orient="horizontal",tickinterval=10)
        self.Gas_Entry.grid(column=1,row=2,columnspan=3)
        self.Gas_Entry.grid_remove()
        
        self.setpoint_Button = tk.Button(Control_Frame,
                                         text="Activate",
                                         command= self.set_Setpoint_Zone
                                         )
        self.setpoint_Button.grid(column = 5, row =1)
        #Default is Zone, but the function to switch modes should have a 
        #Method to change the command to the Appropriate mode
        
        self.read_button=tk.Button(Control_Frame, text="Read Controller",
                                   command=self.Read_Controller_Zone)
        self.read_button.grid(column = 5, row=0)
        #Button to read the controller and populate the GUI accordingly.
        #like the activate button,Defaults to Zone mode, but ChamgeMode should swap to a relevant 
        #Mode.
        
        self.Off_Button=tk.Button(Control_Frame,
                                         text = "All Off",
                                         command = self.Alloff,
                                         bg = "red",
                                         width=55
                                         )
        self.Off_Button.grid(column = 0, row = 6, columnspan=4,sticky="s")
        
        
        self.StartButton=tk.Button(Control_Frame,
                                         text = "Start\n Logging",
                                         command = self.UpdateWindow,
                                         bg = "green",
                                         height=5,
                                         
                                         )
        self.StartButton.grid(column=7,row=0,rowspan=6)

# =============================================================================
#         MONITORING GRAPH GUI, Stolen from Base Autolab
# =============================================================================
        self.GraphFrame = tk.Frame(self.Window)
        self.GraphFrame.grid(column=0, row=0)#, columnspan=3, rowspan=3)
        self.GraphFrame['borderwidth'] = 10
        self.GraphFrame['relief'] = 'sunken'
        self.GraphFrame['padx'] = 5
        self.GraphFrame['pady'] = 5
        
        self.fig = Figure(figsize=(6,4.62), dpi=100)
        self.fig.set_facecolor("white")
        self.ax = self.fig.add_subplot(111)

        self.Plot1, = self.ax.plot([], [],"#000000",antialiased=False,linewidth=0.5)
        # self.plotlist=[]
        # for x in range (0,10):
        #     self.plotlist.append(self.ax.plot([], [],antialiased=False,linewidth=0.5))
            #add a plot for each Dataset that we can have.
        for key in self.Temperature_Keys:
            self.Plot_Dict[key]=self.ax.plot([],[],self.Colour_List[self.Temperature_Keys.index(key)],
                                             antialiased=False,linewidth=0.5)
            #set up dictionary of plots to append to.
        self.ax.set_facecolor("black")
        self.ax.grid(color="grey")
        self.ax.tick_params(axis='y', colors='#000000')
        #self.ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        #self.axtwin.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        
        formatter = ticker.ScalarFormatter(useMathText=True)
        #formatter.set_powerlimits((-2,2))
        
        self.ax.yaxis.set_major_formatter(formatter)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.GraphFrame)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        toolbar = NavigationToolbar2Tk(self.canvas, self.GraphFrame)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
# =============================================================================
# STATUS SIDEBAR GUI ELEMENTS
# =============================================================================
        StatusFrame=tk.Frame(self.Window)
        StatusFrame.grid(column=1,row=0)#frame to hold individual GUI elements
        StatusFrame['padx']=5
        StatusFrame["pady"]=5
        VTILabel=tk.Label(StatusFrame,text="VTI Temperature")
        VTILabel.grid(row=0,column=0)
        self.VTI_Readout=tk.Message(StatusFrame,font=100, relief = "raised",text="VTI Temperature")
        #message to Update w. values
        self.VTI_Readout.grid(row=1,column=0)
        SampleLabel=tk.Label(StatusFrame,text="Sample Temperature")
        SampleLabel.grid(row=2,column=0)
        self.Sample_Readout=tk.Message(StatusFrame,font=100, relief = "raised",text="Sample Temperature")
        self.Sample_Readout.grid(row=3,column=0)
        #VTI and sample readings are always needed, but would be nice to have a reading for other temperature elements
        #Create Dropdown and a Modular box to cycle through as needed. 
        #Default to Switch Heater, because its the most needed IMO
        self.Modular_Selection=tk.StringVar(StatusFrame,self.Temperature_Keys[-1])
        ModularSelector=tk.OptionMenu(StatusFrame,self.Modular_Selection,*self.Temperature_Keys)
        ModularSelector.grid(row=4,column=0)
        self.Modular_Readout=tk.Message(StatusFrame,font=100, relief = "raised",text="Selected Temperature")
        self.Modular_Readout.grid(row=5,column=0)
        
# =============================================================================
# GUI IS NOW INITIALISED, START THE MONITORING. DOESNT UPDATE GRAPH UNTILL START IS PRESSED       
# =============================================================================
        
        try:
            self.Open_Pipes(default_addresses[0],TMon_Address=(default_addresses[1]))
            self.IsMonitoring=True
            print("PIPE CONTENTS:")
            print(self.Temp_PipeRecv.recv())
        except AttributeError:
            #if the program does not configure correctly, the generated Lakeshore object
            #will have no VI attribute to open or close. Catch this.
            print("Connection Error Detected!")
            self.StartButton.configure(command=self.Reconnect,text="Reconnect",bg="red")
            #change the start button to now attempt recconnection.

        except Exception as e:
            print(e)
            
        
        
# =============================================================================
#  OPEN/CLOSE FUNCTIONS   
# =============================================================================
    def Open_Pipes(self,TCon_Address,TMon_Address=None):
        """
        Opens the MultiThreading, Create a Log File for Diagnostics and initialises. 
     
        """
        self.Temp_PipeRecv, self.Temp_PipeSend = Pipe(duplex=True)
        Controller=self.Model.get()
        if Controller == "Lakeshore_350":
            self.Control=Process(target=(Lakeshore_350_Controller),args=(self.Temp_PipeSend,TCon_Address,self.Com.get() ,TMon_Address))
        elif Controller == "OI_503" :
            self.Control=Process(target=(OI_503_Controller),args=(self.Temp_PipeSend,TCon_Address,self.Com.get()))
        else:
            raise Exception("Unknown Temperature Controller Model!")
            
        self.Control.start()

        self.Temp_PipeRecv.send("T; G")
        while self.Temp_PipeRecv.poll():
            print("Connection Successful. Current Setpoint is {}").format(self.Temp_PipeRecv.recv())
            break
        time.sleep(0.1)
        self.Temp_PipeRecv.send("HMD; S; Z")#initialise Heater control in Zone mode, to match W. gui.
        time.sleep(0.1)
        #TODO; Find some way to counteract this, as its a pain if the heaters are turned off every time we
        #initialise the software.
        #Set Setpoint to 0 has to be there to prevent unintentional application of MAX POWER from Base
        #If the Setpoint was, say, 290K but actual T was 1.5 K.
        #if Logs arent there, create.
        if path.exists(r".\LogFiles")==False:
            LogPath=path.join(r".","LogFiles")
            mkdir(LogPath)#Now Has created a Log File Directory
        today=datetime.date.today()
        Log_Name=(today.strftime("%Y%m%d"))+"_TempLog.txt"
        self.Log_SavePath=path.join(r".\LogFiles",Log_Name)
        #As Open_Pipes only gets called at instantisation, this should work across days.
        self.Current_Log=open(self.Log_SavePath,"w")
        self.Temperature_Log_Writer=csv.writer(self.Current_Log, delimiter='\t',quotechar='|')
        #TAB GANG BAYBE
        self.Temperature_Log_Writer.writerow(["Time","VTI Temperature","Sample_Temperature","1st Stage Temp","2nd Stage Temp","Magnet 1","Magnet 2", "He Pot", "Switch Heater"])
        
            
       
    
    def close_function(self):
        """
        Funciton to call when the monitoring window is exited.

        """
        print("This will exit the multithreading gracefully")
        self.Temp_PipeRecv.send("STOP")
        self.Current_Log.close()
        self.IsMonitoring=False#use this to close anything that isnt in the pipes
        self.Window.destroy()
        
    def Reconnect(self):
        """
        Reconnect to temperature controller, open Pipes and start graph
        REMEMBER: Any Button commands can't have arguments otherwise they get called immediately.

        Parameters
        ----------
        TCon_Address : Str or Int
            GPIB or Serial Address for the Temperature controller
        TMon_Address : STR or INT, optional
            GPIB or Serial Address for the Temperature monitor/Level Meter

        """
        TCon_Address=self.Com.get()
        self.Open_Pipes(TCon_Address)#,TMon_Address)
        time.sleep(2.5)#wait for pipe to initialise
        self.UpdateWindow()
# =============================================================================
# UPDATE WINDOW FUNCTIONS
# =============================================================================
    def Get_Pipe_Data(self):
        """   
        Check if the pipe has anything in it
        Loads data from the pipe and adds it to the datasets and writes to LogFile
        Stolen from Base Autolab

        """
        Start_T = time.time()
        
        while(self.IsMonitoring==True):#TODO: Test 
            # Timeout if it spends too long reading the que, likely because is very full
            if time.time()-Start_T>5:
                print("Timeout, Queue might be too large!")
                break
            
            #Check if there is something to recieve in the pipe
            if not self.Temp_PipeRecv.poll():
               break
            
            #get data from pipe
            Data = self.Temp_PipeRecv.recv()
            #If data isn't a string append to rawdata list
            try:
                types=[type(ob) for ob in Data]
                if str not in types:
                    #if they're all numbers then its temperature data, otherwise its a command
                    self.current_Data=Data
                
                elif Data=="Esc":
                    #self.MeasureFinished()
                    break
                elif Data=="ClearGraph":
                    self.Temperature_Data = []
                    continue
            except TypeError as e:
                #if Data is a single int/float, the types generator wont work. 
                #because strings are lists of string characters, strings work fine.
                #But Exceptions are not indexable. If the Handler throws an exception we can catch it here to MakeToast
                self.IsMonitoring=False#if we receive an exception, stop monitoring
                if isinstance(Data,Exception):
                    #Should catch any Exception object (Any exception, TypeError, AttrError...)
                    #that is sent down the pipe.
                    #Allows for Error-finding that won't get swamped by other statements on the Terminal.
                    tk.messagebox.showerror("Found an error!",Data.args[0])
                    
                
                else:
                    print(e)
                    
        self.Temperature_Log_Writer.writerow([*self.current_Data])
    
    
    def UpdateWindow(self):
        """
        This is the general window that updates anything that needs updating.
        Avoid running long process here, must be quick as possible Again, Base Autolab Stuff
        """
        # Get data from the worker by reading the que
        self.Get_Pipe_Data()
        self.UpdateGraph()
        self.UpdateStatus()
        if self.IsMonitoring==True:
            #Get_Pipe Data also Writes to File, so we want to stop that when we close the TMon.
            #This Halts the Calling of Update Window if the IsMonitoring Bool is False
            self.after(2500,self.UpdateWindow)
    
    def UpdateStatus(self):
        """
        Take the data from the Pipe and update the tk.Messages in StatusFrame w. relevant data
        NB: Assumes self.current_Data is the live data, and the data is in the format;
        [current Time,VTI Temperature, Sample Temperature,
                                       "1st Stage","2nd Stage","Magnet 1", "Magnet 2","Helium Pot",
                                       "Switch Heater", isramping bool, is stablebool]
        May want to make this more modular for other systems.
        
        """
        self.VTI_Readout["text"]=str(self.current_Data[1])
        self.Sample_Readout["text"]=str(self.current_Data[2])
        #NB; May want to make this more modular if we end up using this 
        modular_index=(self.Temperature_Keys.index(self.Modular_Selection.get()))+1
        #+1 to skip the time parameter in the pipe
        self.Modular_Readout["text"]=str(self.current_Data[modular_index])
        
        
    def UpdateGraph(self):
        """
        Take the data from the pipe and plot. Iterate over the list and plot a line for each 
        Dataset available

        """

        try:
            if len(self.Time_Data) <=10000:
                self.Time_Data.append(self.current_Data[0])
                self.Temperature_Data.append(self.current_Data[1::])
                
            else:
                del(self.Time_Data[0])
                del(self.Temperature_Data[0])
                self.Time_Data.append(self.current_Data[0])
                self.Temperature_Data.append(self.current_Data[1::])
            
            
            for x in range (0,2):#Temp A, Temp B and Temperatures 1-6 On the 218
                key=self.Temperature_Keys[x]
                self.Plot_Dict[key][0].set_xdata(self.Time_Data)
                self.Plot_Dict[key][0].set_ydata([el[x] for el in self.Temperature_Data])
                time.sleep(0.1)
            self.fig.canvas.draw()
            self.ax.relim()
            self.ax.autoscale()
        except Exception as e:
            print(e)
            print("Error In Graph Update")
            self.IsMonitoring=False
            self.Temp_PipeRecv.send("STOP")
            self.Window.destroy()
            #if the graph throws an error it keeps compounding. Close window to avoid crashes/weird states.
            #TODO: Make this error handling a little more graceful.

# =============================================================================
# READ CONTROLLER FUNCTIONS
# =============================================================================
    def Read_Controller_Zone(self):
        """
        Read the Controller and populate the GUI with the current elements in Zone mode

        """
        currentModel=self.TC_Model.index(self.Model.get())
        self.setpoint_entry.delete(0,tk.END)#clear the relevant GUI element
        self.Temp_PipeRecv.send("T; G")#sends the GET command
        while self.Temp_PipeRecv.poll():#waits for response
            self.setpoint_entry.insert(tk.END, str(self.Temp_PipeRecv.recv()))#updates GUI element
            break
        if currentModel==0:
            self.ramp_entry.delete(0,tk.END)
            self.Temp_PipeRecv.send("RAMP; G")#update Ramp
            while self.Temp_PipeRecv.poll():
                self.ramp_entry.insert(tk.END, str(self.Temp_PipeRecv.recv()))
                break
            self.Temp_PipeRecv.send("RNG; G")#update Heater Range
            while self.Temp_PipeRecv.poll():
                response=int(self.Temp_PipeRecv.recv())#should be 0-5.
                self.Range_var.set(self.Heater_Range[response])
                #Because we formatted the range list in the same manner as the ranges in the Lakeshore,
                #We can just take the response from here as the range. Hopefully. Maybe.
                break
        elif currentModel==1:
            self.Temp_PipeRecv.send("GAS; G")#update Gas Flow
            while self.Temp_PipeRecv.poll():
                self.Gas_Entry.set(float(self.Temp_PipeRecv.recv()))
                break
            
    def Read_Controller_PID(self):
        """
        Read the controller and Populate the GUI in Manual PID Mode.

        """
        currentModel=self.TC_Model.index(self.Model.get())
        self.setpoint_entry.delete(0,tk.END)
        self.Temp_PipeRecv.send("T; G")#sends the GET command
        while self.Temp_PipeRecv.poll():#waits for response
            self.setpoint_entry.insert(tk.END, str(self.Temp_PipeRecv.recv()))#updates GUI element
            break
        #Update PIDS. Should be the same over both Temperature controllers
        self.P_entry.delete(0,tk.END)
        self.I_entry.delete(0,tk.END)
        self.D_entry.delete(0,tk.END)
        self.Temp_PipeRecv.send("PID; G")
        
        while self.Temp_PipeRecv.poll():#waits for response
           PIDs=self.Temp_PipeRecv.recv()
           self.P_entry.insert(tk.END,PIDs[0])
           self.I_entry.insert(tk.END,PIDs[1])
           self.D_entry.insert(tk.END,PIDs[2])
           break
       #Controller Specific stuffs
        if currentModel==0:
            self.Temp_PipeRecv.send("RNG; G")#update Heater Range
            while self.Temp_PipeRecv.poll():
                response=int(self.Temp_PipeRecv.recv())#should be 0-5.
                self.Range_var.set(self.Heater_Range[response])
                #Because we formatted the range list in the same manner as the ranges in the Lakeshore,
                #We can just take the response from here as the range. Hopefully. Maybe.
                break
        elif currentModel==1:
            self.Temp_PipeRecv.send("GAS; G")#update Gas flow
            while self.Temp_PipeRecv.poll():
                self.Gas_Entry.set(float(self.Temp_PipeRecv.recv()))
                break
           
    def Read_Controller_Manual(self):
        """
        Read controller and populate the GUI in Manual Power mode.
        NB: with the OI503 this will work even in Zone Mode. Not with the Lakeshores.
        
        """
        currentModel=self.TC_Model.index(self.Model.get())
        self.Temp_PipeRecv.send("MO; G")#update Manual Power
        while self.Temp_PipeRecv.poll():
            self.power_Entry.set(float(self.Temp_PipeRecv.recv()))
            break
        #Controller Specific stuffs
        if currentModel==0:
            self.Temp_PipeRecv.send("RNG; G")#update Heater Range
            while self.Temp_PipeRecv.poll():
                response=int(self.Temp_PipeRecv.recv())#should be 0-5.
                self.Range_var.set(self.Heater_Range[response])
                #Because we formatted the range list in the same manner as the ranges in the Lakeshore,
                #We can just take the response from here as the range. Hopefully. Maybe.
                break
        elif currentModel==1:
            self.Temp_PipeRecv.send("GAS; G")#update Gas flow
            while self.Temp_PipeRecv.poll():
                self.Gas_Entry.set(float(self.Temp_PipeRecv.recv()))
                break
            
            
# =============================================================================
# ACT ON CONTROLLER FUNCTIONS        
# =============================================================================
    def set_Setpoint_Zone(self):
        """
        Set the setpoint in Zone Mode and sanitises setpoint and Ramping inputs. Assume that the controller is in Zone
        If ramping is set to true, also activate the Ramping mode.
        """
        currentModel=self.TC_Model.index(self.Model.get()) #allows us to update Gas
        if currentModel==0:
            try:
                ramp_rate=float(self.ramp_entry.get())
                if self.ramp_enable.get()==True and 0.001<=ramp_rate<=100:
                    self.Temp_PipeRecv.send("RAMP; S; {}".format(ramp_rate))
                elif self.ramp_enable.get()==True:
                    print("Invalid Ramp Rate! Ramp rate not applied!")
                    self.Temp_PipeRecv.send("NORAMP")
                else:
                    self.Temp_PipeRecv.send("NORAMP")
            except ValueError:
                if self.ramp_enable.get()==True:
                    print("Invalid Ramp rate Entered! Ramp Not enabled!")
                    self.Temp_PipeRecv.send("NORAMP")
                else:
                    self.Temp_PipeRecv.send("NORAMP")#If you've entered the Bee movie script into the Ramp_enable but havent ticked it, I dont care.
        elif currentModel==1:
              try:
                  Gas_to_send=float(self.Gas_Entry.get())
                  self.Temp_PipeRecv.send("GAS; S; {}".format(Gas_to_send))
              except Exception as e:
                  print(e)
                  #again, not sure how you throw this but...          
            
        try:
            setpoint=float(self.setpoint_entry.get())
            if setpoint < 300 and setpoint >= 0:
                #make sure temperature is in Kelvin and that temperature is OK for a cryostat
                self.Temp_PipeRecv.send("T; S; {}".format(setpoint))
            else:
                print("Invalid Setpoint given. Has to be in Kelvin and Less than 300 K")
                
        except ValueError:
            print("Invalid Temperature Setpoint given! Has to be able to be cast as a float!")
            
    def set_Setpoint_PID(self):
        """
        Set the Setpoint in Manual PID mode and Stanises inputs for PID.
        Assume that the controller is in Manual Mode
        """
        currentModel=self.TC_Model.index(self.Model.get())#OI503 and LS have different PID limits. Catch this.
        try:
            P=float(self.P_entry.get())
            I=float(self.I_entry.get())
            D=float(self.D_entry.get())
            if currentModel==0:
                if 0.1 <= P <= 1000 and 0.1<= I <= 1000 and 0<= D<= 200:
                    self.Temp_PipeRecv.send("PID; S; {0},{1},{2}".format(P,I,D))
                else:
                    print("Invalid PID values! P and I have to be less than 1000, and D under 200")
                    print("Recived PID of {0},{1},{2}".format(P,I,D))
            elif currentModel==1:
                if  0<= I <= 140 and 0<= D<= 273:
                    self.Temp_PipeRecv.send("PID; S; {0},{1},{2}".format(P,I,D))
                    #TODO: Make is so that PIDS can be broadcast seperately. Low priority. 
                    #Would rather use a "read" command to populate PID GUI elements from OPS POV.
                else:
                    print("Invalid PID values! I has to be less than 140, and D under 273")
                    print("Recived PID of {0},{1},{2}".format(P,I,D))
        except ValueError:
            print("PIDs could not be cast as Float! PIDS unchanged!")
        
        if currentModel==0:    
            try:
                Range_to_send=self.Heater_Range.index(self.Range_var.get())
                self.Temp_PipeRecv.send("RNG; S; {}".format(Range_to_send))
            except ValueError:
                print("No Range Entered, Range Not changed!")
        elif currentModel==1:
            try:
                Gas_to_send=float(self.Gas_Entry.get())
                self.Temp_PipeRecv.send("GAS; S; {}".format(Gas_to_send))
                #Todo:Test this. 
            except Exception as e:
                print(e)
                #again, not sure how you throw this but...
                
            
        try:
            setpoint=float(self.setpoint_entry.get())
            if setpoint < 300 and setpoint >= 0:
                #make sure temperature is in Kelvin and that temperature is OK for a cryostat
                self.Temp_PipeRecv.send("T; S; {}".format(setpoint))
            else:
                print("Invalid Setpoint given. Has to be in Kelvin and Less than 300 K")
                
        except ValueError:
            print("Invalid Temperature Setpoint given! Has to be able to be cast as a float!")
            
    def set_Manual_Power(self):
        currentModel=self.TC_Model.index(self.Model.get())
        if currentModel==0:    
            try:
                Range_to_send=self.Heater_Range.index(self.Range_var.get())
                self.Temp_PipeRecv.send("RNG; S; {}".format(Range_to_send))
            except ValueError:
                print("No Range Entered, Range Not changed!")
        elif currentModel==1:
            try:
                Gas_to_send=float(self.Gas_Entry.get())
                self.Temp_PipeRecv.send("GAS; S; {}".format(Gas_to_send))
            except Exception as e:
                print(e)
                #again, not sure how you throw this but...
        
        try:
            power_to_send=float(self.power_Entry.get())
            self.Temp_PipeRecv.send("PO; S; {}".format(power_to_send))
        except Exception as e:
            print(e)#not quite sure how you fuck this up but just in case
            
    def Alloff(self):
        """
        Turns all the heaters off and sets Setpoint and Manual Output Power to 0. 
        ULTIMATE PANIC BUTTON. MASH FOR SAFE SYSTEM* 
        
        *Doesnt control anyfuckups you've done with the gas flow

        """
        self.Temp_PipeRecv.send("ALLOFF")
        self.Temp_PipeRecv.send("PO; S; 0")
        self.Temp_PipeRecv.send("T; S; 0")

# =============================================================================
# CHANGE MODE FUNCTIONS
# =============================================================================

    def ChangeMode(self,var,index,mode):
        """
        Code to change the mode in both GUI elements and Applied mode in the Heater controller. 
        SHOULD only activate if the value changes, not if the menu was open so SHOULD be invuln to
        Monkey BS
        Paramters are TK Nonsense. Not used.
        
        """
        NewMode=self.Mode_Select.index(self.Mode.get())
        currentModel=self.TC_Model.index(self.Model.get())
        if NewMode==0:#Zone Mode
            self.P_entry.grid_remove()
            self.I_entry.grid_remove()
            self.D_entry.grid_remove()
            self.power_Entry.grid_remove()
            self.power_Label.grid_remove()#Remove Unecessary GUI Elements
            self.setpoint_entry.grid()#re-show necessary GUI elements.
            if currentModel==0:
                self.ramp_button.grid()
                self.ramp_entry.grid()#only show this if we're using a Lakeshore.
            elif currentModel==1:
                self.ramp_enable=False
                #explicitly set this. Probably unneccessary, as Ramp isnt live on the OI Temperature_controller
            self.Temp_PipeRecv.send("HMD; S; Z")
            self.setpoint_Button.configure(command=self.set_Setpoint_Zone)#make sure correct values are being passed
            self.read_button.configure(command=self.Read_Controller_Zone)
        
        elif NewMode==1 :#Open Loop Control
            self.P_entry.grid_remove()
            self.I_entry.grid_remove()
            self.D_entry.grid_remove()
            self.ramp_button.grid_remove()
            self.ramp_entry.grid_remove()
            self.setpoint_entry.grid_remove()
            self.power_Entry.grid()
            self.power_Label.grid()
            self.Temp_PipeRecv.send("HMD; S; MO")
            self.setpoint_Button.configure(command=self.set_Manual_Power)
            self.read_button.configure(command=self.Read_Controller_Manual)
        
        elif NewMode==2:#Manual PID mode
            self.power_Entry.grid_remove()
            self.power_Label.grid_remove()
            self.ramp_button.grid_remove()
            self.ramp_entry.grid_remove()
            self.setpoint_entry.grid()
            self.P_entry.grid()
            self.I_entry.grid()
            self.D_entry.grid()
            self.Temp_PipeRecv.send("HMD; S; MP")
            self.setpoint_Button.configure(command=self.set_Setpoint_PID)
            self.read_button.configure(command=self.Read_Controller_PID)
            
    def ChangeModel(self,var,index,mode):
        """
        Code to setup the GUI to work with a new model of temperature controller
        Added to Trace on the Model variable so should ONLY be called when the option is changed
        Parameters are TK stuff, not used.        

        """
        tk.messagebox.showinfo(title="Changing Temperature Controller", message="Changing temperature controller. CLosing pipes")
        self.IsMonitoring=False
        self.Temp_PipeRecv.send("STOP")
        self.Current_Log.close()
        self.StartButton.configure(command=self.Reconnect,text="Reconnect",bg="red")
        NewModel=self.TC_Model.index(self.Model.get())
        currentMode=self.Mode_Select.index(self.Mode.get())
        if NewModel==0:#Lakeshore350
            self.Gas_Entry.grid_remove()#uneeded GUI element
            self.Gas_Label.grid_remove()
            
            self.range_Entry.grid()
            if currentMode==0: #zone Mode, so ramp is now enabled
                self.ramp_button.grid()
                self.ramp_entry.grid()
        elif NewModel==1:
            self.ramp_button.grid_remove()
            self.ramp_entry.grid_remove()
            self.ramp_enable=False#again, explicitly set out of paranoia
            self.range_Entry.grid_remove()
            self.Gas_Label.grid()
            self.Gas_Entry.grid()#show Gas slider.
                