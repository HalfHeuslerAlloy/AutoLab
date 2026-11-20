# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 09:32:04 2026

@author: csk42
Module to create a tk Treeview for dynamic setup of sweeps/ramps
Create a frame in which this lives to add in buttons/sliders ect
without impacting the overall design
"""

import tkinter as tk
from tkinter import ttk
#Stolen from https://coderslegacy.com/how-to-make-ttk-treeview-editable-python/
class EntryPopup(ttk.Entry):
    def __init__(self, parent, iid, column, text, **kw):
        super().__init__(parent.RampFrame, **kw)
        self.tv = parent.Tree  # reference to parent window's treeview
        self.iid = iid  # row id
        self.column = column 

        self.insert(0, text) 
        self['exportselection'] = False  # Prevents selected text from being copied to  
                                         # clipboard when widget loses focus
        self.focus_force()  # Set focus to the Entry widget
        self.select_all()   # Highlight all text within the entry widget
        self.bind("<Return>", self.on_return) # Enter key bind
        self.bind("<Control-a>", self.select_all) # CTRL + A key bind
        self.bind("<Escape>", lambda *ignore: self.destroy()) # ESC key bind
        
    def on_return(self, event):
        '''Insert text into treeview, and delete the entry popup'''
        rowid = self.tv.focus()  # Find row id of the cell which was clicked
        vals = self.tv.item(rowid, 'values')  # Returns a tuple of all values from the row with id, "rowid"
        vals = list(vals)  # Convert the values to a list so it becomes mutable
        vals[self.column] = self.get()  # Update values with the new text from the entry widget
        self.tv.item(rowid, values=vals)  # Update the Treeview cell with updated row values
        self.destroy()  # Destroy the Entry Widget
        
    def select_all(self, *ignore):
        ''' Set selection on the whole text '''
        self.selection_range(0, 'end')
        return 'break' # returns 'break' to interrupt default key-bindings

class Dynamic_Ramps(tk.Frame):
    
    def __init__(self, master, columns={"Target":["Float",0],"Rate":["Float",0.5],"Switch":["Bool",False]}):
        super().__init__(master)
        self.RampFrame=tk.Frame(master)
        
        self.Tree = ttk.Treeview(self.RampFrame, columns=list(columns.keys()), show='headings')
        default_values_list=[]
        for key in columns.keys():
            self.Tree.heading(str(key),text=str(key))
            default_values_list.append(columns[key][1])
            #get the default values and populate the 1st row with the default values
        print(default_values_list)
        self.Tree.bind("<Double-1>",lambda event: self.onDoubleClick(event))
        self.Tree.insert("","end",values=default_values_list)
        self.Tree.pack(fill="both",expand=True)
        
    def onDoubleClick(self, event):
        try:
            self.entryPopup.destroy()
        except AttributeError:
            pass
        
        #get row/column
        rowid=self.Tree.identify_row(event.y)
        column=self.Tree.identify_column(event.x)
        
        if not rowid:#if header is clicked, RowId will return blank
            return
        
        x,y,width,height=self.Tree.bbox(rowid,column)
        #y-axis offset
        pady=height//2
        
        text=self.Tree.item(rowid,'values')[int(column[1:])-1]
        self.entryPopup = EntryPopup(self, rowid, int(column[1:])-1, text)
        self.entryPopup.place(x=x, y=y+pady, width=width, height=height, anchor='w')
        
    def get_Column(self,column_name):
        """
        Return the values in the given TreeView

        Parameters
        ----------
        column_name : Str
            Name of the Column in question

        Returns
        -------
        A list of the values within the column

        """
        column_values = []
        for id in self.Tree.get_children():
            column_values.append(self.Tree.item(id, "values")[self.Tree["columns"].index(column_name)])
        return column_values
        
    def get_Row(self,row_index):
        """
        Return the values of a given row index

        Parameters
        ----------
        row_index : Int
            Index of the row in question

        Returns
        -------
        The values of the row

        """
        print("get_children return value: ", self.Tree.get_children())
        return self.Tree.item(self.Tree.get_children()[row_index], "values")