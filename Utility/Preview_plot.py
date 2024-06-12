# -*- coding: utf-8 -*-
"""
Created on Tue May 21 14:57:40 2024

@author: eencsk

Script to create Onecode style miniplots to add to the main-script as a preview
PLot hard-coded to show 100 points Max, its just a preview. 
nb: Doesnt work GREAT with .pack, probably best to put this in a .grid position manager and have it off to one side
"""

import tkinter as tk
import numpy as np
from matplotlib.figure import Figure
from scipy.interpolate import interp1d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #tool to draw the graph into TK.

class Preview_plot():
    
    def __init__(self, parent_Frame:tk.Frame, data):
        """
        

        Parameters
        ----------
        parent_Frame : tk.Frame
            Frame to embed plot into
        data : Array-like
            Array containing the x and Y data. data[0,::] 
            data[1,::] should contain the Y data.

        """
        self.fig = Figure(figsize=(2.5,2.5), dpi=100)
        self.fig.set_facecolor("white")
        self.ax = self.fig.add_subplot(111)
        neo_data=self.sanitise(data)
        
        self.ax.set_facecolor("black")
        self.ax.grid(color="grey")
        self.ax.tick_params(axis='y', colors='#000000')
        
        
        self.Plot1 = self.ax.scatter(neo_data[0],neo_data[1],s=3,c="#77003c")
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_Frame)
        self.canvas.draw()
        self.TK_widget=self.canvas.get_tk_widget()
        #now have TK widget containing the data from the plot that can be .grid or .pack into the Parent_Frame
        
        
    def sanitise(self,data):
        """
        Takes the input data and trims it to be 100 points long and
        Makes sure x and y are of equal length. Assumes data can be parsed as float.

        Parameters
        ----------
        data : Array-like
            Data to be cleaned.

        Returns
        -------
        A numpy array of floats max size [2,100]

        """
        point_no=100# want a maximum of 100 points on the graph.
        
        
        #Now make sure 2 arrays are same size
        try:
            x_len=data[0].size
            y_len=data[1].size
        except AttributeError:#I know that someone is going to give this a list of lists at some point. Catch
            x_len=len(data[0])
            y_len=len(data[1])
            
        if x_len != y_len:
            raise ValueError("Expected Lists of equal Length, X is {0} Y is {1}.".format(x_len,y_len))
            
        else:
            if x_len>point_no :
                x_dat=np.sort(data[0])#should work for both list and np.arrays. Bonus; Returns a np.array!
                x_new=np.linspace(x_dat[0],x_dat[-1],point_no)
                #generate 100 evenly spaced points to interpolate along
                interp_func=interp1d(data[0],data[1])
                y_new=interp_func(x_new)
                return(np.array([x_new,y_new]))
            else:
                #if data is shorter than 100 pts =, dont care
                return(np.array([data[0],data[1]]))
            
    
    def Update_Data(self,data):
        """
        Change the data in the plot to a new Data set
        
        Parameters
        ----------
        data : Array-like
            Array containing the x and Y data. data[0,::] 
            data[1,::] should contain the Y data.


        """
                
        cleaned_data=self.sanitise(data)
        self.Plot1.set_xdata(cleaned_data[0])
        self.Plot1.set_ydata(cleaned_data[1])
        self.fig.canvas.draw()
        self.ax.relim()
        self.ax.autoscale()
            