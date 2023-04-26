# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 11:14:18 2023

@author: eencsk
"""

class lakeshore218(object):
    def __init__(self, rm, Address):
        """
        Initialise the LS218 Monitor
        
        Parameters
        ---
        rm pyvisa resource manader
        Address: String or Int: Either a int (will address as COM:Address)
        or a string from pyvisa.listresources

        """
        if Address[:3] == "ASRL":
            self.VI=rm.open_resource(Address)
        else:
            try:
                int(Address)
                self.VI=rm.open_resource('COM'+str(Address))
            except ValueError:
                raise Exception("Invalid Lakeshore218 Address. Expected an Int or a string beginning ASRL, got {}".format(Address))
                
        