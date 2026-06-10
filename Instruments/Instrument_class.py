# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 11:35:57 2025
Generic Class for Instruments. Generic instrument terms (Read/Write/Query) should be defined here so that code
Errors can be processed easier.

POssibly bad coding practice. I'm using the exceptions raised by the drivers as flow control but since its for errors anyway, 
Speed isnt an issue.

Note; This cements self.VI as the syntax for direct write to instruments.

@author: eencsk
"""
import inspect
from pyvisa.errors import VisaIOError
from pyvisa.constants import StopBits, Parity

class Instrument(object):
    
    def __init__(self,rm,channel,GPIB=True, Baud_Rate=9600, Data_Bits=8, Parity=Parity.none, Stop_bits=StopBits.one):
        """
        

        Parameters
        ----------
        rm : pyvisa.resource_manager
            the resource manage used to connect to the instruments
        channel : int or Str, optional
            Address of device.
            If int, just the GPIB address, if Str, the full address, as pulled from
            RM.List_Resources
        GPIB : Bool, optional, default is True
            Whether to use GPIB (T) or COM (F) to connect to the instrument.
        Baud_Rate,Data_Bits,Parity and stop_bits are the 
        COM parameters for serial connections


        """
        self.rm=rm#hold the pointer to the RM in memory so that it can be called later
        
        if GPIB ==True:
            if type(channel) != type(" "):
                self.VI = rm.open_resource('GPIB0::' + str(channel) + '::INSTR')
            else:
                self.VI = rm.open_resource(channel)
                
        else:
            if channel == type(" "): #If the address is not a string the slice in next line dont work!
                
                if channel[:3] == "ASRL":
                    self.VI=rm.open_resource(channel,baud_rate=Baud_Rate,data_bits=Data_Bits,
                                             parity=Parity,stop_bits=Stop_bits)
                else:
                    raise Exception("Invalid COM Address, Expected an Int or String Beginning ASRL, got {}".format(channel))
            else:
                try:
                    self.VI=rm.open_resource('COM'+str(channel),baud_rate=Baud_Rate,data_bits=Data_Bits,
                                             parity=Parity,stop_bits=Stop_bits)
                except ValueError:
                    raise Exception("Invalid COM Address. Expected an Int or a string beginning ASRL, got {}".format(channel))
            
    def __del__(self):
        try:
            self.VI.close()
        except AttributeError:
            pass #if connection is unsuccessful, program may try to delete the instrument object
            #this raises an Attribute Error (No VI to close!) Catch this.
    def List_Resources(self):
        """
        Bugfixing Code fragment to write out the List_Resources
        At Call-time. Having strange errors and wonder if the bus
        might be dropping out

        Returns
        -------
        None.

        """

        print(self.rm.list_resources())
    
    def Write (self,message):
        """
        Write a message to an instrument

        Parameters
        ----------
        message : Str
            Message to be written to the instrument. Should be sanitised before reaching this point

        Returns
        -------
        None.

        """
        timeout=0#iterator. 
        while timeout < 5:
            try:
                self.VI.write(message)
            
            except VisaIOError as e:#if the bus is being flaky, this may trigger. attempt message 5 times until calling it
                timeout+=1#increment timeout
                if timeout==5:
                    raise Exception (e)
                
            except Exception as e:
                exception_arg=e.args[0]
                #contains the actual exception message. Its the only thing printed in the anaconda prompt otherwise
                try:
                    frame=inspect.currentframe().f_back
                    #gets the caller of this write function. This should be your instrument module
                    trace=inspect.getframeinfo(frame)
                    module_name=trace.filename
                    #As the instruments are named accordingly, the filename should show up the correct name
                finally:
                    del frame #done to prevent memory leaks due to reccurent frame references
                    
                exception_message="Error occured Writing "+ message + " in "+module_name+": "+exception_arg
                self.List_Resources()
                break#if another error occurs, break the timeout loop.
                raise Exception(exception_message)
            else:
                break #break the while loop if no error found
    
    def Query (self, message):
        """
        Send a Message and Query a response from the instrument.

        Parameters
        ----------
        message : Str
            Message to be written to the instrument. Should be sanitised before reaching this point

        Returns
        -------
        The Response from the instrument

        """
        timeout=0
        while timeout < 5:
            try:
                result=self.VI.query(message)
            
            except VisaIOError as e:#if the bus is being flaky, this may trigger. attempt message 5 times until calling it
                timeout+=1#increment timeout
                if timeout==5:
                    raise Exception (e)
                
                
            except Exception as e:
                exception_arg=e.args[0]
                #contains the actual exception message. Its the only thing printed in the anaconda prompt otherwise
                try:
                    frame=inspect.currentframe().f_back
                    #gets the caller of this write function. This should be your instrument module
                    trace=inspect.getframeinfo(frame)
                    module_name=trace.filename
                    #As the instruments are named accordingly, the filename should show up the correct name
                finally:
                    del frame #done to prevent memory leaks due to reccurent frame references
                    
                exception_message="Error occured Querying "+ message + " in "+module_name+": "+exception_arg
                self.List_Resources()
                raise Exception(exception_message)
            else:
                return(result)
            
      
    def Read(self):
        """
        Reads a message from the instrument

        Returns
        -------
        The read message

        """
        timeout=0
        while timeout < 5:
            
            try:
                result=self.VI.read()
            except VisaIOError as e:#if the bus is being flaky, this may trigger. attempt message 5 times until calling it
                timeout+=1#increment timeout
                if timeout==5:
                    raise Exception (e)
        
            except Exception as e:
                exception_arg=e.args[0]
                #contains the actual exception message. Its the only thing printed in the anaconda prompt otherwise
                try:
                    frame=inspect.currentframe().f_back
                    #gets the caller of this write function. This should be your instrument module
                    trace=inspect.getframeinfo(frame)
                    module_name=trace.filename
                    #As the instruments are named accordingly, the filename should show up the correct name
                finally:
                    del frame #done to prevent memory leaks due to reccurent frame references
                    
                exception_message="Error occured Reading in "+module_name+": "+exception_arg
                self.List_Resources()
                raise Exception(exception_message)
            else:
                return(result)
            
    def getSTB(self):
        """
        Uses Pyvisa's inbuilt method to ping the status byte of the instrument

        Returns
        -------
        The status byte as a string in binary

        """
        timeout=0
        while timeout < 5:
            try:
                result=(format(self.VI.stb,"b"))
            except VisaIOError as e:#if the bus is being flaky, this may trigger. attempt message 5 times until calling it
                timeout+=1#increment timeout
                print("Timeout Detected")
                if timeout==5:
                    raise Exception (e)
            
            except Exception as e:
                exception_arg=e.args[0]
                #contains the actual exception message. Its the only thing printed in the anaconda prompt otherwise
                try:
                    frame=inspect.currentframe().f_back
                    #gets the caller of this write function. This should be your instrument module
                    trace=inspect.getframeinfo(frame)
                    module_name=trace.filename
                    #As the instruments are named accordingly, the filename should show up the correct name
                finally:
                    del frame #done to prevent memory leaks due to reccurent frame references
                    
                exception_message="Error occured in getting StatusByte from "+module_name+": "+exception_arg
                self.List_Resources()
                raise Exception(exception_message)
            else:
                return(result)