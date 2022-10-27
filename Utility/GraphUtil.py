# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 16:02:22 2022

@author: eenmv
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

import numpy as np

class Util(tk.Frame):
    """
    Test utility function
    """
    
    #Name of utility so it can e refer to later as part of a dictionary
    name = "Graph"
    
    CurrentGraph = "1D"
    
    def __init__(self, master):
        
        super().__init__(master)
        
        GraphUtilTab = tk.Frame(master)
        master.add(GraphUtilTab,text="Graph Settings")
        
        self.XaxisEntryLabel = tk.Label(GraphUtilTab,text="X")
        self.XaxisEntryLabel.grid(column=0, row=0)
        self.XaxisEntry = tk.Entry(GraphUtilTab,width = 10)
        self.XaxisEntry.insert(tk.END,"0")
        self.XaxisEntry.grid(column=0, row=1)
        
        self.Y1axisEntryLabel = tk.Label(GraphUtilTab,text="Y1")
        self.Y1axisEntryLabel.grid(column=1, row=0)
        self.Y1axisEntry = tk.Entry(GraphUtilTab,width = 10)
        self.Y1axisEntry.insert(tk.END,"1")
        self.Y1axisEntry.grid(column=1, row=1)
        
        self.Y2axisEntryLabel = tk.Label(GraphUtilTab,text="Y2")
        self.Y2axisEntryLabel.grid(column=2, row=0)
        self.Y2axisEntry = tk.Entry(GraphUtilTab,width = 10)
        self.Y2axisEntry.insert(tk.END,"2")
        self.Y2axisEntry.grid(column=2, row=1)
        
        self.Autoscale = tk.IntVar()
        self.Autoscale.set(True)
        AutoscaleCheck = tk.Checkbutton(GraphUtilTab,text="Autoscale",variable=self.Autoscale)
        AutoscaleCheck.grid(column=0, row=2)
        
        #Graph type selection
        
        GraphSelectFrame = tk.Frame(GraphUtilTab)
        GraphSelectFrame.grid(column = 3, row = 1)
        
        self.GraphSelectOption = tk.StringVar(None,"1D")
        
        Graph1DOption = ttk.Radiobutton(GraphSelectFrame,
                                              text="1D Grpah",
                                              variable=self.GraphSelectOption,
                                              value="1D")
        Graph1DOption.pack(anchor="w")
        
        Graph2DOption = ttk.Radiobutton(GraphSelectFrame,
                                          text="2D Graph",
                                          variable=self.GraphSelectOption,
                                          value="2D")
        Graph2DOption.pack(anchor="w")
        
    def CreateGraph(self):
        """Creates the figure to put inside the graphic section of Autolab
        Determine if either 1d or 2d graph type
        """
        
        # Check if 2D first so if there is an evaluation error it will default to 1D
        if self.GraphSelectOption.get() == "2D":
            
            #Change entry labels
            self.XaxisEntryLabel["text"]  = "X"
            self.Y1axisEntryLabel["text"] = "Y"
            self.Y2axisEntryLabel["text"] = "Z"
            
            self.CreateGraph2D()
            
        else:
            
            #Change entry labels
            self.XaxisEntryLabel["text"]  = "X"
            self.Y1axisEntryLabel["text"] = "Y1"
            self.Y2axisEntryLabel["text"] = "Y2"
            
            self.CreateGraph1D()
            
            
        
    
    def CreateGraph1D(self,width=6,height=4.62,dpi=50):
        """Creates the figure to put inside the graphic section of Autolab
        """
        
        xData = []
        y1Data = []
        y2Data = []
        
        self.fig = Figure(figsize=(width, height), dpi=100)
        self.fig.set_facecolor("white")
        
        self.ax = self.fig.add_subplot(111)
        self.axtwin = self.ax.twinx()
        
        self.Plot1, = self.ax.plot(xData, y1Data,"#000000",antialiased=False,linewidth=0.5)
        self.Plot2, = self.axtwin.plot(xData, y2Data,"#E69F00",antialiased=False,linewidth=0.5)
        
        self.ax.set_facecolor("white")
        self.ax.grid(color="grey")
        
        self.ax.tick_params(axis='y', colors='#000000')
        self.axtwin.tick_params(axis='y', colors='#E69F00')
        
        #self.ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        #self.axtwin.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        
        formatter = ticker.ScalarFormatter(useMathText=True)
        formatter.set_scientific(True) 
        formatter.set_powerlimits((-2,2))
        
        self.ax.yaxis.set_major_formatter(formatter)
        self.axtwin.yaxis.set_major_formatter(formatter)
    
    def CreateGraph2D(self,width=6,height=4.62,dpi=50):
        
        self.fig = Figure(figsize = (width, height),dpi = 100)
        self.fig.set_facecolor("white")
        
        self.ax = self.fig.add_subplot(111)
        
        self.Plot2D = self.ax.imshow([[0]],extent=[0,1,0,1],aspect='auto')
        
        self.fig.colorbar(self.Plot2D, ax = self.ax)
    
    def UpdateGraph(self,Data):
        """Updates the graph with given data and selected columns
        """
        
        if self.CurrentGraph == "1D":
            self.UpdateGraph1D(Data)
        else:
            self.UpdateGraph2D(Data)
        
    def UpdateGraph1D(self,Data):
        
        try:
            
            xAxisSel = int(self.XaxisEntry.get())
            Str = self.Y1axisEntry.get()
            y1AxisSel = [int(i) for i in Str.replace(" ","").split(",")]
            Str = self.Y2axisEntry.get()
            y2AxisSel = [int(i) for i in Str.replace(" ","").split(",")]
            
            xData = [float(i[xAxisSel]) for i in Data]
            
            y1Data = []
            for Sel in y1AxisSel:
                y1Data.append([float(i[Sel]) for i in Data])
        
            y2Data = []
            for Sel in y2AxisSel:
                y2Data.append([float(i[Sel]) for i in Data])
            
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
        
        if bool(self.Autoscale.get()):
            try:
                self.ax.relim()
                self.ax.autoscale()
                self.axtwin.relim()
                self.axtwin.autoscale()
            except Exception as e:
                print("Couldn't autosclae graph")
                print(e)
        
        
    def UpdateGraph2D(self,Data):
        """Updates the Graph with the selected data
        """
        
        try:
            
            xAxisSel = int(self.XaxisEntry.get())
            Str = self.Y1axisEntry.get()
            yAxisSel = [int(i) for i in Str.replace(" ","").split(",")]
            Str = self.Y2axisEntry.get()
            zAxisSel = [int(i) for i in Str.replace(" ","").split(",")]
            
            xData = [float(i[xAxisSel]) for i in Data]
            
            yData = []
            for Sel in yAxisSel:
                yData.append([float(i[Sel]) for i in Data])
            
            yData = yData[0]
        
            zData = []
            for Sel in zAxisSel:
                zData.append([float(i[Sel]) for i in Data])
                
            zData = zData[0]
            
        except Exception as e:
            
            print(e)
            
            xAxisSel = 0
            yAxisSel = 1
            zAxisSel = 2
            print("Invalid column selection")
            return
        
        if len(xData) == 0:
            xData = [0]
            yData = [0]
            zData = [0]
        
        try:
            
            meshgrid = self.MeshNearest(xData,yData,zData)
            
            self.Plot2D.set_data(meshgrid)
            
            if bool(self.Autoscale.get()):
                try:
                    
                    minX = min(xData)
                    maxX = max(xData)
                    if minX == maxX:
                        minX = 0
                        maxX = 1
                    
                    minY = min(yData)
                    maxY = max(yData)
                    if minY == maxY:
                        minY = 0
                        maxY = 1
                    
                    self.Plot2D.autoscale()
                    self.Plot2D.set_extent([minX,maxX,
                                            minY,maxY])
    
                    self.ax.relim()
                    self.ax.autoscale()
                    
                except Exception as e:
                    print("Couldn't autosclae graph")
                    print(e)
            
            #self.ax.redraw_in_frame()
        
        except Exception as e:
            print(e)
            print("Failed to plot data")
    
    def MeshNearest(self,dataX,dataY,dataZ):
        """Converts a list of X, Y and Z data to a mesh grid
        Uses nearest neighboor, tries to guess good grid dimensions
        
        returns n*m grid
        """
        
        #Check if there is data to work with
        if len(dataX)==0:
            return np.array([[0]])
        
        dataX = np.array(dataX)
        dataY = np.array(dataY)
        dataZ = np.array(dataZ)
        
        # Get max difference
        minX = min(dataX)
        maxX = max(dataX)
        if minX == maxX:
            deltaX = 1
            nX = 1
        else:
            deltaX = abs(max(dataX[1:] - dataX[:-1]))
            nX = round( (maxX-minX)/deltaX ) + 1
        
        minY = min(dataY)
        maxY = max(dataY)
        if minY == maxY:
            deltaY = 1
            nY = 1
        else:
            deltaY = abs(max(dataY[1:] - dataY[:-1]))
            nY = round( (maxY-minY)/deltaY ) + 1
        
        if nX*nY>1000000:
            print("2D plot is too large, number of cells greater that 1,000,000")
            return np.array([[0]])
        
        #make array
        meshgrid = np.zeros([int(nY),int(nX)])
        
        #Move Z data to meshgrid
        for i in range(len(dataZ)):
            x = dataX[i]
            y = dataY[i]
            z = dataZ[i]
            
            iX = int(round( (x-minX)/deltaX ))
            iY = int(nY-1) - int(round((y-minY)/deltaY ))
            
            #print(nX,nY,iX,iY)
            
            meshgrid[iY,iX] = z
        
        return meshgrid
            
            

if __name__=="__main__":
    
    #Make and start main window
    root = tk.Tk()
    UtilTabs = ttk.Notebook(root,height = 100,width = 595)
    UtilTabs.pack()
    UtilTab = Util(UtilTabs)
    UtilTab.mainloop()