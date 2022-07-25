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
    - Add Utility for magnet, lockin controls
    - Arroyo driver and also utility control
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


import numpy as np
import sys
import os
import datetime
import time

from multiprocessing import Process, Queue, Pipe

import pyvisa

#Autolab liberies
import Instruments

import Utility

import Workers

class Window(tk.Frame):
    """
    Main window for AutoLab
    This class should handle GUI
    """
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
        
        #######  Setup Frames  #########
        
        #menu frame        
        self.menuFrameSetup()
        
        
        
        #File frame
        self.fileSysFrame = tk.Frame()
        self.fileSysFrame.grid(column=0, row=1, columnspan=1, rowspan=1)
        self.fileSysFrame['borderwidth'] = 2
        self.fileSysFrame['relief'] = 'raised'
        self.fileSysFrame['padx'] = 5
        self.fileSysFrame['pady'] = 5
        #self.fileSysFrame['bg'] = "green"
        
        filenameLabel = tk.Label(self.fileSysFrame,text="Filename")
        filenameLabel.grid(column=0,row=0,sticky="w")
        
        
        self.GraphFrame = tk.Frame()
        self.GraphFrame.grid(column=1, row=1, columnspan=1, rowspan=3)
        self.GraphFrame['borderwidth'] = 2
        self.GraphFrame['relief'] = 'raised'
        self.GraphFrame['padx'] = 5
        self.GraphFrame['pady'] = 5
        #self.GraphFrame['bg'] = "black"
        
        self.CreateGraph()
        #self.GraphCanvas = tk.Canvas(self.GraphFrame,width=500,height=500)
        #self.GraphCanvas.pack()
        
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
        
        self.SetupInstruments("Setup.txt")

        
        
        self.UtilFrame = tk.Frame()
        self.UtilFrame.grid(column=1, row=4, columnspan=1, rowspan=1)
        self.UtilFrame['borderwidth'] = 2
        self.UtilFrame['relief'] = 'raised'
        self.UtilFrame['padx'] = 5
        self.UtilFrame['pady'] = 5
        #self.UtilFrame['bg'] = "purple"
        
        
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
        
        
        #Create untility tabs
        self.UtilTabs = ttk.Notebook(self.UtilFrame,height = 100,width = 495)
        self.UtilTabs.pack(side="bottom")
        self.utilTabModules = {}
        
        #Add tabs to the utility tab wigdet
        self.FileUtiltab = Utility.FileUtil.Util(self.UtilTabs)
        self.utilTabModules[self.FileUtiltab.name] = self.FileUtiltab
        #self.CreateFileUtilTab()
        
        self.GraphUtilTab = Utility.GraphUtil.Util(self.UtilTabs)
        self.utilTabModules[self.GraphUtilTab.name] = self.GraphUtilTab
        #self.CreateGraphUtilTab()
        
        self.SetupUtilTabs("Setup.txt")
        
        
        
        self.filenameInput = tk.Entry(self.fileSysFrame,width = 80)
        self.filenameInput.grid(column=0,row=1)
        
        self.headerInput = tk.Text(self.fileSysFrame,width = 60,height = 3)
        self.headerInput.grid(column=0,row=2)

        
        self.filename = tk.StringVar()
        #Defaults to current directory
        self.filename.set(os.getcwd() + r"\test.txt")
        self.filenameInput["textvariable"] = self.filename
        
        header = "Measuremented started at {}, this should get filled in when saved"
        self.headerInput.insert("1.0",header)
        
        
        
        self.UpdateWindow()
    
    ############################################
    ####### Updating Window and graph ##########
    ############################################
    
    def UpdateWindow(self):
        """
        This is the general window that updates anything that needs updating.
        Avoid running long process here, must be quick as possible
        """
        
        #self.xData.append(self.xData[-1]+0.01)
        #self.y1Data.append(2 * np.sin(2 * np.pi * self.xData[-1]))
        #self.y2Data.append(2 * np.cos(2 * np.pi * self.xData[-1]))
        
        if self.MeasureActive:
            # Update measurement stuff
            
            # flash the active icon
            FlashCycles = 4 # Number of cycles to switch flash on
            
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
        
        self.UpdateGraph()
        
        self.after(250,self.UpdateWindow)
    
    #########################################
    ####### Setup utilites section ##########
    #########################################
    
    def menuFrameSetup(self):
        """
        Setup menu options at the top of the window. add extra functionality here.
        """
        
        menuFrame = tk.Frame()
        menuFrame.grid(column=0, row=0, columnspan=2,sticky="w")
        menuFrame['relief'] = 'raised'
        
        
        self.LoadMeasWorkerButton = tk.Button(menuFrame,text = "Load Script",command = self.LoadMeasWorker)
        self.LoadMeasWorkerButton.grid(column=0, row=0,sticky="w")
    
    def SetupUtilTabs(self,SetupFile):
        
        print("Loading Utilities")
        
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
                    
                    utilTabInst = utilTabModule.Util(self.UtilTabs)
                    
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
        
    ############################################
    ####### Matplotlib Graphing stuff ##########
    ############################################

    def CreateGraph(self,width=5,Height=4.5,dpi=100):
        """
        Create a matplotlib figure inside the graphing frame for ploting data
        """
        
#        self.xData = np.arange(0, 3, .01)
#        self.y1Data = list(2 * np.sin(2 * np.pi * self.xData))
#        self.y2Data = list(2 * np.cos(2 * np.pi * self.xData))
#        self.xData = list(self.xData)
        
        self.Data = []
        self.xData = []
        self.y1Data = []
        self.y2Data = []
        
        self.fig = Figure(figsize=(width, Height), dpi=100)
        self.fig.set_facecolor("white")
        
        self.ax = self.fig.add_subplot(111)
        self.axtwin = self.ax.twinx()
        
        self.Plot1, = self.ax.plot(self.xData, self.y1Data,"#000000",antialiased=False,linewidth=0.5)
        self.Plot2, = self.axtwin.plot(self.xData,self.y2Data,"#E69F00",antialiased=False,linewidth=0.5)
        
        self.ax.set_facecolor("white")
        self.ax.grid(color="grey")
        
        self.ax.tick_params(axis='y', colors='#000000')
        self.axtwin.tick_params(axis='y', colors='#E69F00')
        
        
        canvas = FigureCanvasTkAgg(self.fig, master=self.GraphFrame)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        toolbar = NavigationToolbar2Tk(canvas, self.GraphFrame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def UpdateGraph(self):
        
        try:
            
            xAxisSel = int(self.GraphUtilTab.XaxisEntry.get())
            Str = self.GraphUtilTab.Y1axisEntry.get()
            y1AxisSel = [int(i) for i in Str.replace(" ","").split(",")]
            Str = self.GraphUtilTab.Y2axisEntry.get()
            y2AxisSel = [int(i) for i in Str.replace(" ","").split(",")]
            
            xData = [float(i[xAxisSel]) for i in self.Data]
            
            y1Data = []
            for Sel in y1AxisSel:
                y1Data.append([float(i[Sel]) for i in self.Data])
        
            y2Data = []
            for Sel in y2AxisSel:
                y2Data.append([float(i[Sel]) for i in self.Data])
            
        except Exception as e:
            
            print(e)
            
            xAxisSel = 0
            y1AxisSel = 1
            y2AxisSel = 2
            print("Invalid column selection")
            return
        
        self.Plot1.set_xdata(xData)
        self.Plot1.set_ydata(y1Data[0])
        self.Plot2.set_xdata(xData)
        self.Plot2.set_ydata(y2Data[0])
        
#        self.Plot1.set_data(*y1Data)
#        self.Plot2.set_data(*y2Data)
        
        try:
            self.ax.relim()
            self.ax.autoscale()
            self.axtwin.relim()
            self.axtwin.autoscale()
            
            self.fig.canvas.draw()
        except Exception as e:
            print("Couldn't update graph")
            print(e)
    
    #########################################
    ####### Setup utilites section ##########
    #########################################
    
    def CreateFileUtilTab(self):
        """Creates the utilities tab for controlling how the file should be saved
        """
        FileUtilTab = tk.Frame(self.UtilTabs)
        self.UtilTabs.add(FileUtilTab,text="Save Settings")
        
        #TODO - Make this an either/or option
        self.OverrideFile = tk.IntVar()
        OverrideFile = tk.Checkbutton(FileUtilTab,text="Override",variable=self.OverrideFile)
        OverrideFile.pack()
        self.AutoEnumerate = tk.IntVar()
        AutoEnumerate = tk.Checkbutton(FileUtilTab,text="Auto Enumerate",variable=self.AutoEnumerate)
        AutoEnumerate.pack()
        
    ########################################
    ####### Setup Measure section ##########
    ########################################
    
    def CreateMeasTab(self):
        """Simply generates the measurement tab and add pages to it
        """
        self.MeasWorkerFrame = tk.Frame(self.MeasTabs)
        self.MeasTabs.add(self.MeasWorkerFrame,text="Main Script")
    
        
    def LoadMeasWorker(self):
        """
        Tries to load the main script with name MeasWorker
        """
        
        print("loading main script")
        
        #DESTROY this previous wokerframe if it exist
        try:
            self.WorkerFrame.destroy()
            self.update()   
        except:
            pass
        
        self.WorkerFrame = tk.Frame(self.MeasWorkerFrame)
        self.WorkerFrame.grid(column=0, row=1, columnspan=3, rowspan=3)
        
        #Get filename of Expirement GUI and worker
        filename = fd.askopenfile(initialdir = os.getcwd()+"\\Workers")
        filename = filename.name[( len(os.getcwd())+1 ):-3]
        filename = filename.replace("/",".")
        module = filename.split(".")[1]
        if filename==None:
            return
        
        #Load GUI and worker from filename
        #self.MeasWorkerScript = __import__(filename, fromlist=[''])
        
        self.MeasWorkerScript = getattr(Workers, module)
        
        self.MeasHandler = self.MeasWorkerScript.Handler(self.WorkerFrame)
        
        self.MeasWorker = self.MeasWorkerScript.Worker
        
        
        
        print("Finished loading worker")
        
    
    ################################################################
    ####### Starting, stop and moditoring measure section ##########
    ################################################################
    
    def RunMeasure(self):
        
        #Reset all of graphing data lists
        self.Data = []
        self.xData = []
        self.y1Data = []
        self.y2Data = []
        
        if self.CreateFile():
            print("File created")
        else:
            print("Failed to create file")
            return
        
        
        # try to start the measure, raise error if it failed
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
        Check if the queue has anything in it
        Loads data from the queue and adds it to the datasets
        """
        Start_T = time.time()
        
        while(True):
            
            #Check if there is something to recieve in the pipe
            if not self.PipeRecv.poll():
                break
            
            #get data from pipe
            Data = self.PipeRecv.recv()
            
            if type(Data)!=str:
                self.Data.append(Data)
                
            elif Data=="Esc":
                self.MeasureFinished()
                break
            
            ##### Save data to save file ####
            
            #Convert Data list to string and remove the brackets
            # TODO add option for tab or comma delimter file
            if type(Data)==list:
                Data = str(Data)
                Data = Data[1:-1]+"\n"
            
            #write Data to string
            self.file.write( str(Data) )
            
            if time.time()-Start_T>5:
                print("Timeout, Queue might be too large!")
                break
    
    def CheckMeasureFinished(self):
        """
        Checks if the measurement has finished without disturding it
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
            
            print("Boths pipes have been emptied has been emptied")
            
            self.MeasureActive = False
            self.CloseSaveFile()
        
        else:
            print("Failed to stop process! It's out of control!")
                
        
        
    ##################################################
    ####### Save filename managemant section ##########
    ##################################################
    
    def CreateFile(self):
        """
        Creates and opens file with filename inputted
        
        TODO:
            - Change this to ask if you want to overide file if trying to.
        """
        
        filename = self.filenameInput.get()
        header = self.headerInput.get("1.0",tk.END)
        
        try:
            Overide = bool(self.FileUtiltab.OverrideFile.get())
        except Exception as e:
            print(e)
            print("failed to read overide checkbox value")
            return
        try:
            AutoEnum = bool(self.FileUtiltab.AutoEnumerate.get())
        except Exception as e:
            print(e)
            print("failed to read AutoEnuerate checkbox value")
            return
        
        
        if Overide:
            #Make/replaces file
            self.file = open(filename,"w")
            self.file.seek(0)
            self.file.truncate()
        else:
            #Check if file exist before
            fileExist = os.path.isfile(filename)
            
            if (AutoEnum==False) & (fileExist==True):
                print("File already exist! Overide off and AutoEnumatation is also off")
                print("Not sure what you expected me to do about it!")
                #Return False for failed file creation,
                # TODO change this to error handling
                # TODO create dialog box to ask to overide current file
                return False
            
            elif (AutoEnum==False) & (fileExist==False):
                # Make file
                self.file = open(filename,"w")
                self.file.seek(0)
                self.file.truncate()
                
            elif AutoEnum==True:
                
                fileExist = True
                N = 0
                
                enumFilename = filename
                
                while(fileExist):
                    
                    N += 1
                    EnumStr = str(N).zfill(3)
                    enumFilename = filename[:-4] +"_"+ EnumStr + filename[-4:]
                    fileExist = os.path.isfile(enumFilename)
                    if N>999:
                        print("timeout finding Enumeration")
                        return False
                
                filename = enumFilename
                
                print("made file with number: ".format(N))
                self.file = open(filename,"w")
                self.file.seek(0)
                self.file.truncate()
        
        #Inset header file here
        #Add current date and time if needed
        self.file.write(header.format( str(datetime.datetime.now() ) ) )
        self.file.write("\n#HeaderEnd\n\n")
        
        #return True for succesful file creation
        return True
        
    
    def SaveToFile(self):
        pass
    
    def CloseSaveFile(self):
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
    Experiment.mainloop()