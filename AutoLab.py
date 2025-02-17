# -*- coding: utf-8 -*-
"""
Created on Thu May  5 11:20:16 2022

@author: eenmv

GUI for automating measurements with python.

Currently using Matplotlib to generate graphs might be too slow!

Measurements scripts written in python.
These inherit the instrument objects from the main program

Task:
    - More documentation
    - More Comments
    - Add missing error handling
    - Make Resource manager fully multiprocessing compatible
    - Add more graph settings in utility tab
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import font as tkFont

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib import ticker
import re

import numpy as np
import sys
import os
import datetime
import time
import importlib
from pathlib import Path

from multiprocessing import Process, Queue, Pipe

import pyvisa

#Autolab liberies
import Instruments

import Utility

#import Workers

#Main class and window

class Window(tk.Frame):
    """
    Main window for AutoLab
    This class should handle GUI
    """
    
    Data = []
    
    def __init__(self, master,Resources):
        """
        Initial setup of widgets and the general window position
        """
        super().__init__(master)
        #self.pack()
        
        #Setup multiprocesing
        self.DataStream = Queue()
        #generate the pipes for sending and receiving data (Faster thatn Queues)
        self.PipeRecv, self.PipeSend = Pipe(duplex=True)
        
        self.Measure = None
        self.MeasureActive = False
        
        self.Resources = Resources
        
        ###################################
        ##########  Setup Frames  #########
        ###################################
        
        # Find either Setup.txt or SetupExample.txt
        if os.path.isfile(os.getcwd()+"\\Setup.txt"):
            setupFilename = "Setup.txt"
        else:
            print("\n\n    WARNING: Defaulting to the example setup file!   \n\n")
            setupFilename = "SetupExample.txt"
        
        #######  menu frame   #############
        
        self.MenuFrameSetup()
        
        ######### Utility frame and Tabs ###########
        
        self.UtilFrame = tk.Frame()
        self.UtilFrame.grid(column=1, row=4, columnspan=1, rowspan=1)
        self.UtilFrame['borderwidth'] = 2
        self.UtilFrame['relief'] = 'raised'
        self.UtilFrame['padx'] = 5
        self.UtilFrame['pady'] = 5
        #self.UtilFrame['bg'] = "purple"
        
        #Create untility tabs
        self.UtilTabs = ttk.Notebook(self.UtilFrame,height = 100,width = 595)
        self.UtilTabs.pack(side="bottom")
        self.utilTabModules = {}
        
        #Add tabs to the utility tab wigdet
        self.FileUtiltab = Utility.FileUtil.Util(self.UtilTabs)
        self.utilTabModules[self.FileUtiltab.name] = self.FileUtiltab
        #self.CreateFileUtilTab()
        
        self.GraphUtilTab = Utility.GraphUtil.Util(self.UtilTabs)
        self.utilTabModules[self.GraphUtilTab.name] = self.GraphUtilTab
        #self.CreateGraphUtilTab()
        
        self.SetupUtilTabs(setupFilename)
        
        ############## File frame ##################
        
        self.fileSysFrame = tk.Frame()
        self.fileSysFrame.grid(column=0, row=1, columnspan=1, rowspan=1)
        self.fileSysFrame['borderwidth'] = 2
        self.fileSysFrame['relief'] = 'raised'
        self.fileSysFrame['padx'] = 5
        self.fileSysFrame['pady'] = 5
        #self.fileSysFrame['bg'] = "green"
        
        #PathLabel = tk.Label(self.fileSysFrame,text="Path")
        #PathLabel.grid(column=0,row=0,sticky="w")
        
        self.pathInput = tk.Entry(self.fileSysFrame,width = 80)
        self.pathInput.grid(column=0,row=0)
        
        self.path = tk.StringVar()
        #Defaults to current directory
        self.path.set(os.getcwd())
        self.pathInput["textvariable"] = self.path
        
        #filenameLabel = tk.Label(self.fileSysFrame,text="Filename")
        #filenameLabel.grid(column=0,row=1,sticky="w")
        
        self.filenameInput = tk.Entry(self.fileSysFrame,width = 80)
        self.filenameInput.grid(column=0,row=1)
        
        self.filename = tk.StringVar()
        #Defaults to test.txt
        self.filename.set(r"test.txt")
        self.filenameInput["textvariable"] = self.filename
        
        self.headerInput = tk.Text(self.fileSysFrame,width = 60,height = 4)
        self.headerInput.grid(column=0,row=2)
        
        header = "Measuremented started at {}, this should get filled in when saved"
        self.headerInput.insert("1.0",header)
        
        
        ############## Graph frame + Graph utility ##################
        
        self.GraphFrame = tk.Frame()
        self.GraphFrame.grid(column=1, row=1, columnspan=1, rowspan=3)
        self.GraphFrame['borderwidth'] = 2
        self.GraphFrame['relief'] = 'raised'
        self.GraphFrame['padx'] = 5
        self.GraphFrame['pady'] = 5
        
        
        
        self.CreateGraph()
        
        
        ############## Measurement frame ###################
        
        self.MeasFrame = tk.Frame()
        self.MeasFrame.grid(column=0, row=2, columnspan=1, rowspan=2)
        self.MeasFrame['borderwidth'] = 2
        self.MeasFrame['relief'] = 'raised'
        self.MeasFrame['padx'] = 5
        self.MeasFrame['pady'] = 5
        #self.MeasFrame['bg'] = "blue"
        
        MeasLabel = tk.Label(self.MeasFrame,text="Measurement Setup")
        MeasLabel.pack(side="top")
        
        self.MeasTabs = ttk.Notebook(self.MeasFrame,height = 330,width = 480)
        self.MeasTabs.pack(side="bottom")
        
        self.CreateMeasTab()
        
        self.SetupInstruments(setupFilename)
        
        
        ############# Start/stop/busy frame ######################
        
        self.RunFrame = tk.Frame()
        self.RunFrame.grid(column=0, row=4, columnspan=1, rowspan=1)
        self.RunFrame['borderwidth'] = 2
        self.RunFrame['relief'] = 'raised'
        self.RunFrame['padx'] = 5
        self.RunFrame['pady'] = 5
        #self.RunFrame['bg'] = "purple"
        

        self.RunWorkerButton = tk.Button(self.RunFrame,
                                         text = "Run",
                                         bg = "green",
                                         command = self.RunMeasure,
                                         font=tkFont.Font(size=30)
                                         )
        
        self.RunWorkerButton.grid(column=0, row=0,padx=40)
        
        self.StopWorkerButton = tk.Button(self.RunFrame,
                                         text = "Stop",
                                         bg = "red",
                                         command = self.StopMeasure,
                                         font=tkFont.Font(size=30)
                                         )
        
        self.StopWorkerButton.grid(column=1, row=0,padx=40)
        
        self.Icons = {}
        
        self.Icons["IDLE"] = tk.PhotoImage(file=r"Icons\Indicator_IDLE_small.png")
        self.Icons["ACTIVE"] = tk.PhotoImage(file=r"Icons\Indicator_ACTIVE_small.png")
        self.Icons["ACTIVE_DARK"] = tk.PhotoImage(file=r"Icons\Indicator_ACTIVE_DARK_small.png")
        self.Icons["ERROR"] = tk.PhotoImage(file=r"Icons\Indicator_ERROR_small.png")
        
        self.IndicatorLabel = tk.Label(self.RunFrame)
        self.IndicatorLabel["image"] = self.Icons["IDLE"]
        self.IndicatorLabel.grid(column=2, row=0)
        
        self.IndicatorFlashState = 0
        
        #self.UtilLabel = tk.Label(self.UtilFrame,text="Utilities")
        #self.UtilLabel.pack(side="top")
        

        
        self.UpdateWindow()
    
    ############################################
    ####### Updating Window and graph ##########
    ############################################
    
    def UpdateWindow(self):
        """
        This is the general window that updates anything that needs updating.
        Avoid running long process here, must be quick as possible
        """
        
        
        if self.MeasureActive:
            # Update measurement stuff
            
            # flash the active icon
            FlashCycles = 4 # Number of cycles to switch flash on
            #TODO: Grey-Out things in the top-bar while measurement is running.
            if self.IndicatorFlashState<FlashCycles:
                self.IndicatorLabel["image"] = self.Icons["ACTIVE"]
            else:
                self.IndicatorLabel["image"] = self.Icons["ACTIVE_DARK"]

            self.IndicatorFlashState += 1
            if self.IndicatorFlashState>FlashCycles*2:
                self.IndicatorFlashState = 0
                
            
            
            # Get data from the worker by reading the que
            self.GetData()
            Finished = self.CheckMeasureFinished()
            if Finished:
                print("Measurement finished with exitcode {}".format(self.MeasHandler.Worker.exitcode))
                self.MeasureFinished()
                self.MeasureActive = False
        else:
            self.IndicatorLabel["image"] = self.Icons["IDLE"]
        
        
        if self.GraphUtilTab.CurrentGraph ==  self.GraphUtilTab.GraphSelectOption.get():
            self.UpdateGraph()
        else:
            #re create graph is new graph type
            self.GraphUtilTab.CurrentGraph = self.GraphUtilTab.GraphSelectOption.get()
            self.CreateGraph()
        
        self.after(250,self.UpdateWindow)
    
    #########################################
    ####### Setup utilites section ##########
    #########################################
    
    def MenuFrameSetup(self):
        """
        Setup menu options at the top of the window. add extra functionality here.
        """
        
        menuFrame = tk.Frame()
        menuFrame.grid(column=0, row=0, columnspan=2,sticky="w")
        menuFrame['relief'] = 'raised'
        
        
        menuFrame.grid_columnconfigure(0, weight=1)
        self.LoadMeasWorkerButton = tk.Button(menuFrame,text = "Load Script",command = self.LoadMeasWorker)
        self.LoadMeasWorkerButton.grid(column=0, row=0,sticky="w")
       
        self.refreshButton=tk.Button(menuFrame,text="Refresh Comms",command=self.refresh_Address_list)
        self.refreshButton.grid(column=5,row=0,sticky="e",padx=20)#button to re-poll rm.list_resources
        
        self.rescriptButton=tk.Button(menuFrame,text="Refresh Scripts",command=self.refresh_Workers)
        self.rescriptButton.grid(column=1,row=0,padx=20)#button to re-fresh the loaded script
        
    
    def SetupUtilTabs(self,SetupFile):
        
        print("Loading Utilities")
        rm=pyvisa.ResourceManager()
        self.address_list=rm.list_resources()
        rm.close()#Create a list of Valid GPIB/COMS ports. Useful for passing to workers/utils
        
        file = open(SetupFile,"r")
        
        instSection = False
        
        for line in file:
            
            #Check if we have entered the instrument section of the setup file
            if line.startswith("#"):
                if line.startswith("#Utilities"):
                    instSection = True
                else:
                    instSection = False
            
            
            # If in the instrument section of setup file try to load each instrument
            elif instSection:
                #try to find instrument in Instruments module
                #Load that instrument with given channel and name
                try:
                    tabStr = line.replace("\n","") # remove end of charactor
                    print(tabStr)
                    utilTabModule = getattr(Utility, tabStr)
                    
                    utilTabInst = utilTabModule.Util(self.UtilTabs,parent=self)
                    
                    self.utilTabModules[utilTabInst.name] = utilTabInst
                     
                except Exception as e:
                    print(e)
                
        
        file.close()
    
    ####################################################
    ####### Setup instruments from setup file ##########
    ####################################################
    
    def SetupInstruments(self,SetupFile):
        
        print("Loading instruments")
        
        file = open(SetupFile,"r")
        
        instSection = False
        
        for line in file:
            
            #Check if we have entered the instrument section of the setup file
            if line.startswith("#"):
                if line.startswith("#Instruments"):
                    instSection = True
                else:
                    instSection = False
            
            
            # If in the instrument section of setup file try to load each instrument
            elif instSection:
                #try to find instrument in Instruments module
                #Load that instrument with given channel and name
                try:
                    self.Resources.LoadInst(line)
                    
                except Exception as e:
                    print(e)
                
                
        file.close()
    
    def refresh_Address_list(self):
        """
        quick routine to re-poll the resource list.
        TODO: Test this on a live rig

        """
        rm=pyvisa.ResourceManager()
        self.address_list=rm.list_resources()
        rm.close()
        
    def refresh_Workers(self):
        """
        
        Re-build the Measurement GUI by calling importlib.reload, and then Re-creating the WorkerBook and Handler

        """
        try:                
            self.WorkerBook.destroy()
            importlib.reload(self.MeasWorkerScript)
            self.WorkerBook = ttk.Notebook(self.MeasTabs,height = 330,width = 480)
            #as before, creates a holder-frame that can be destroyed while keeping the overall archetecture intact
            self.WorkerBook.pack(side="bottom")
            self.MeasHandler = self.MeasWorkerScript.Handler(self.WorkerBook,self)
            #rebuild Handler Gui/Backend with refreshed Script
            self.MeasWorker = self.MeasWorkerScript.Worker
            #now refresh the ancilliary things in the GraphUtilTab
            try:
                self.GraphUtilTab.Initialise_Dropdowns(self.MeasHandler.Header_List)
            except AttributeError:
                #if tehre is no Header list, you're stuck with the old Textboxes, enjoy!
                self.GraphUtilTab.Initialise_Textboxes()
            print("Refreshed Current Worker Script!")
        except AttributeError:
            print("Cannot Refresh an Empty Script!")
        
        
    ############################################
    ####### Matplotlib Graphing stuff ##########
    ############################################

    def CreateGraph(self,width=6,Height=4.62,dpi=50):
        """
        Create a matplotlib figure inside the graphing frame for ploting data
        """
        
        #self.Data = [[0,0e-5,0e-5],[1,1e-5,1e-5],[2,2e-5,4e-5],[3,3e-5,9e-5],[4,4e-5,16e-5]]
        
        #Create figure to place in widget
        self.GraphUtilTab.CreateGraph()
        
        self.fig = self.GraphUtilTab.fig
#        self.Plot1 = self.GraphUtilTab.Plot1
#        self.Plot2 = self.GraphUtilTab.Plot2
#        self.ax = self.GraphUtilTab.ax
#        self.axtwin = self.GraphUtilTab.axtwin
        try:
            self.GraphFrameInner.destroy()
            self.update()
        except:
            pass
        
        self.GraphFrameInner = tk.Frame(self.GraphFrame)
        self.GraphFrameInner.pack()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.GraphFrameInner)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        toolbar = NavigationToolbar2Tk(self.canvas, self.GraphFrameInner)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def UpdateGraph(self):
        """Update the graph widget with the latest data, using the selected settings
        """
        
        self.GraphUtilTab.UpdateGraph(self.Data)
        
        try:
            self.fig.canvas.draw()
        except:
            print("Couldn't update graph")
        
    ########################################
    ####### Setup Measure section ##########
    ########################################
    
    def CreateMeasTab(self):
        """Simply generates the measurement tab and add pages to it
        """
        #self.MeasWorkerFrame = tk.Frame(self.MeasTabs)
        #self.MeasTabs.add(self.MeasWorkerFrame,text="Main Script")

        
    def LoadMeasWorker(self):
        """
        Tries to load the expirement script from worker and 
        assign it to self.MeasWorkerScript and similar.
        """
        
        print("loading main script")
        #Get filename of Expirement GUI and worker
        filename = fd.askopenfile(initialdir = os.getcwd()+"\\Workers") #Open dialog box at desired folder
        if filename==None:
            print("Please Select a Script, dangus.")
            return
        
        else: #now pressing the Cancel button shouldnt do anything, rather than breaking the script
            #DESTROY this previous wokerframe if it exist
            try:                
                self.WorkerBook.destroy()
       
                importlib.reload(self.MeasWorkerScript)
                #this will apply any changes made to the scripts as they are loaded.
                self.update()
            except AttributeError as e:
                #should only really throw attribute error on initial bootup, as WorkerBook is not initialised
                print(e)
                pass

            self.WorkerBook = ttk.Notebook(self.MeasTabs,height = 330,width = 480)
            #as before, creates a holder-frame that can be destroyed while keeping the overall archetecture intact
            self.WorkerBook.pack(side="bottom")
            
            file_path = filename.name #this now contains the path to the relevant script
            filename = filename.name[( len(os.getcwd())+1 ):-3]
            Module_ID = filename.replace("/",".")
            #importlib.import_module requires an ID in the format Package.subpackage.module, this supplies this nicely
            self.MeasWorkerScript = importlib.import_module(Module_ID,file_path)
            #Only the Module we need has been loaded now, rather than everything in Workers
            #also means we can call importlib.reload on it to apply changes
            # for module in modules[1:]:
            #     MeasWorkerScript = getattr(MeasWorkerScript, module)
            
            self.MeasHandler = self.MeasWorkerScript.Handler(self.WorkerBook,self)
            try:
                self.GraphUtilTab.Initialise_Dropdowns(self.MeasHandler.Header_List)
            except AttributeError:
                #if tehre is no Header list, you're stuck with the old Textboxes, enjoy!
                self.GraphUtilTab.Initialise_Textboxes()
            
            self.MeasWorker = self.MeasWorkerScript.Worker           
            
            print("Finished loading worker")
            return
        
    
    ################################################################
    ##### Starting, stopping and moditoring measure section ########
    ################################################################
    
    def RunMeasure(self):
        """Starts the measurement Worker
        Calls the MeasHandler.Start and gives it the Pipe to send data back and forth
        """
        
        #Reset all of graphing data lists
        self.Data = []
        self.xData = []
        self.y1Data = []
        self.y2Data = []
        
        try:
            filename = self.filenameInput.get()
            if self.CreateFile(filename):
                print("File created")
            else:
                raise()
        except Exception as e:
            print(e)
            print("Failed to create file")
            return
             
        # try to start the measurement worker, raise error if it failed
        try:
            if self.MeasHandler.Start(self.PipeSend):
                print("Measurement Started")
            else:
                raise Exception("Failed to start measurement")
                return
        except Exception as e:
            print(e)
            self.CloseSaveFile()
            return
        
        self.MeasureActive = True
    
    def GetData(self):
        """
        Check if the pipe has anything in it
        Loads data from the pipe and adds it to the datasets
        """
        #start timeout timer for reading the pipe contents, 5sec max
        Start_T = time.time()
        
        while(True):
            # Timeout if it spends too long reading the que, likely because is very full
            if time.time()-Start_T>5:
                print("Timeout, Queue might be too large!")
                break
            
            #Check if there is something to recieve in the pipe
            if not self.PipeRecv.poll():
                break
            
            #get data from pipe
            Data = self.PipeRecv.recv()#this should be a short list of data to be plotted/written to file
            
            #TODO make flags for drawning to graph
            #TODO unwraping multiple points
            #If data isn't a string append to rawdata list for plotting
            try:
                types=[type(ob) for ob in Data]

                if str not in types:
                    self.Data.append(Data)
                    #This is the Data to be PLotted On-Screen, not what is saved to the save-file
                    
                # TODO add more key work commands, NewFile, ClearGraph,

                elif Data=="Esc":
                    self.MeasureFinished()
                    break
                elif Data=="ClearGraph":
                    self.Data = []
                    self.xData = []
                    self.y1Data = []
                    self.y2Data = []
                    continue
                elif Data=="NewFile":
                    self.CloseSaveFile()
                    self.CreateFile(self.filenameInput.get())
                    #now have new save file but want the plotted data to reflect whats in the file, 
                    #so duplicate the above fn.
                    self.Data = []
                    self.xData = []
                    self.y1Data = []
                    self.y2Data = []
                    continue
                
            except TypeError as e:
                #if Data is a single int/float, the types generator wont work. 
                #because strings are lists of string characters, strings work fine.
                #But Exceptions are not indexable. If the Handler throws an exception we can catch it here to MakeToast
                
                if isinstance(Data,Exception):
                    #Should catch any Exception object (Any exception, TypeError, AttrError...)
                    #that is sent down the pipe.
                    #Allows for Error-finding that won't get swamped by other statements on the Terminal.
                    #TODO: This works, but doesnt allow information to be sent about WHAT caused the exception. 
                    #Have to think about that because just sending a VISAError is not useful.
                    print("Found an error!")
                    print(Data)
                else:
                    print(e)
                    print("Received Data that couldnt be iterated over, not sure what you're doing! Aborting.")
                    print(Data)
                self.MeasureFinished()
                break
                
            
            ##### Save data to save file ####
            
            #Convert Data list to string and remove the brackets. This is what gets saved, so strings are OK.
            if type(Data)==list:
            #assume by this point data Has been sanitised, so can pass to routines w. impunity
                try:
                    self.MeasHandler.Update(Data)
                    #pass Data to the measurement Handler in order to update GUI elements within the Worker
                except AttributeError:
                    pass
                #Handle the case where there is no Update routine
                    
                save_Data = str(Data)
                save_Data = save_Data.replace(", ",self.delimiterOption)
                save_Data = save_Data[1:-1]+"\n" #removes brackets on either end and ameks new line
            
                #write Data to string
                self.file.write( str(save_Data) )

    
    def CheckMeasureFinished(self):
        """
        Checks if the measurement has finished without disturding it, in theory
        """
        try:
            self.MeasHandler.Worker.join(timeout=0.1)
            Alive = self.MeasHandler.Worker.is_alive()
            if not Alive:
                return True
            else:
                return False
        except:
            return True
        
        
            
    def MeasureFinished(self):
        """
        Handles when measurement is finished
        """
        
        print("Measurement finished")
        
        try:
            self.MeasHandler.Worker.join()
            self.MeasHandler.Stop()
        except Exception as e:
            print("Could not close worker")
            print(e)
        self.MeasureActive = False
        self.CloseSaveFile()
        
    def StopMeasure(self):
        """
        Force stop the measurement
        """
        
        #Send stop command
        #Call the stop function in the worker in case it needs to do anything after
        self.PipeRecv.send("STOP")
        HasStopped = self.MeasHandler.Stop()
        
        if HasStopped:
            print("Measurement stopped succesfully")
            #Dump queue contents
            print("Dumping contents of Pipes")
            print("PipeRecv:")
            while self.PipeRecv.poll():
                Data = self.PipeRecv.recv()
                print(Data)
            print("PipeSend:")
            while self.PipeSend.poll():
                Data = self.PipeSend.recv()
                print(Data)
            
            print("Boths pipes have been emptied")
            
            self.MeasureActive = False
            self.CloseSaveFile()
        
        else:
            print("Failed to stop process! It's out of control!")
                
        
        
    ##################################################
    ####### Save filename managemant section ##########
    ##################################################
    
    def CreateFile(self,filename):
        """
        Creates and opens file with filename inputted
        
        TODO:
            - Change this to ask if you want to overide file if trying to.
        """
        path = self.pathInput.get()
        header = self.headerInput.get("1.0",tk.END)
        
        #Makes the directory if it doesn't exist
        Path(path).mkdir(parents=True, exist_ok=True)
        filenamePath = path + "\\" + filename
        
        try:
            Overide = self.FileUtiltab.fileMakeOption.get()
            if Overide=="O":
                Overide = True
                AutoEnum = False
            else:
                Overide = False
                AutoEnum = True
        except Exception as e:
            print(e)
            print("failed to read make file options checkbox value")
            return False
        
        # CHeck delimiter option from file ultility window
        try:
            self.delimiterOption = self.FileUtiltab.delimiterOption.get()
        except Exception as e:
            print(e)
            print("Failed to get delimiterOption")
        
        
        if Overide:
            #Make/replaces file
            self.file = open(filenamePath,"w")
            self.file.seek(0)
            self.file.truncate()
        else:
            #Check if file exist before
            fileExist = os.path.isfile(filenamePath)
            
            if (AutoEnum==False) & (fileExist==True):
                print("File already exist! Overide off and AutoEnumatation is also off")
                print("Not sure what you expected me to do about it!")
                #Return False for failed file creation,
                # TODO change this to error handling
                # TODO create dialog box to ask to overide current file
                return False
            
            elif (AutoEnum==False) & (fileExist==False):
                # Make file
                self.file = open(filenamePath,"w")
                self.file.seek(0)
                self.file.truncate()
                
            elif AutoEnum==True:
                
                fileExist = True
                N = 0
                
                enumFilename = filenamePath
                
                while(fileExist):
                    
                    N += 1
                    EnumStr = str(N).zfill(3)
                    enumFilename = filenamePath[:-4] +"_"+ EnumStr + filenamePath[-4:]
                    fileExist = os.path.isfile(enumFilename)
                    if N>999:
                        print("timeout finding Enumeration")
                        return False
                
                filenamePath = enumFilename
                
                print("made file with number: {}".format(N))
                self.file = open(filenamePath,"w")
                self.file.seek(0)
                self.file.truncate()
        
        #Inset header file here
        #Add current date and time if needed
        self.file.write(header.format( str(datetime.datetime.now() ).split(".")[0] ) )
        self.file.write("\n#HeaderEnd\n")
        #write metadata

        for key in self.WorkerBook.children.keys():
            try:
                #iterate through all children of the main WorkerBook and attempt to call Export_MetaData
                #Export_MetaData should return a dictionary
                #currently just write dictionary to file.
                #TODO: Have metadata written to some other config file to be loaded on bootup
                if re.search("frame", key)==None: 
                    #children includes the tk frames and the scripts within.
                    #we just want the scripts
                    try:
                        self.file.write(str(self.WorkerBook.children[key].Export_MetaData()))
                        self.file.write("\n")
                        
                    except AttributeError:#Handle the case were no Export_Metadata method exists
                        pass
            except Exception as e:
                print(e)
        self.file.write("\n#MetadataEnd\n\n")
        #return True for succesful file creation
        return True
        
    
    def SaveToFile(self):
        pass
    
    def CloseSaveFile(self):
        """Closes Save file
        """
        self.file.close()
        print("Save file has been closed")


class ResourcesObj(object):
    """
    This handles all the communication for the instruments and external resources.
    Better to have one singular object as serial ports and comms don't like multiple
    callers.
    """
    def __init__(self):
        """
        Takes a setup file
        """
        self.rm = pyvisa.ResourceManager()
        
        self.insts = {}
    
    def LoadInst(self,line):
        """
        Load Instrument
        """
        
        try:
            line = line.replace("\n","")
            splt = line.split(",")
            InstClass = getattr(Instruments,splt[0])
            
            #Every instrument class should take a ResourceManager object and a channel name
            Inst = InstClass(self.rm, int(splt[1]) )
            
            self.AddInst(Inst,splt[2])
            print("Succesfully connected to "+splt[2])
            
        except Exception as e:
            raise e
    
    def AddInst(self, inst, name):
        """
        Takes Name and Instument object.
        Adds to Dict of Instuments.
        """
        
        self.insts[name] = inst
    
    def CloseAll(self):
        while( len(self.insts)>0 ):
            Name, inst = self.insts.popitem()
            try:
                inst.__del__()
            except:
                print("Failed to close {}".format(Name))


if __name__=="__main__":
    
    #Stores all the pyvisa connections    
    Resources = ResourcesObj()
    
    #Make and start main window
    root = tk.Tk()
    Experiment = Window(root,Resources)
    root.title("Autolab")

    Experiment.mainloop()
    