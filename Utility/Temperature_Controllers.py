# -*- coding: utf-8 -*-
"""
Created on Thu May 29 17:13:36 2025

@author: csk42
"""
import Instruments as Inst
import pyvisa
#Export/String Packages
import time
import re

def Lakeshore_350_Controller(Pipe,TCon_add, TMon_add=None):
    """
    Multiprocessing Process for Temperature Monitoring using Lakeshores. 
    They're so good. They've basically got a unified command syntax.
    Last 2 elements in the pipe must always be the IsRamping and IsStable Bools. Make sure to Slice before plotting!
    Currently Assumes that you're doing Loop 1 connected to sensor A
        
    Special Commands that can be sent through the pipe to the Controller:
        ALLOFF=Turns the Heaters on the Controller OFF
        NORAMP, Turns Ramping Off.
        
    Standard Commands have the Syntax;
        Parameter; X; Y
        X is either S(set) or G(get). Y is the Parameter to Be entered. Assumed Sanitary at this pt.
        
    Parameters are
    HMD; Heater Mode, can be be Z (Zone), MP (Manual PID) or MO (Manual Output).
    T; Setpoint in K
    PO; Manual Power output in %
    PID: PID paramters. In this case, the Parameter is a list of len 3 containing P I and D
    RNG: Heater Range
    RAMP: Ramp rate in K/min
        
      

    Parameters
    ----------
    Pipe : Pipe
        PipeSend to pass things through
        Data is passed in the format; [current Time,VTI Temperature, Sample Temperature,
                                       "1st Stage","2nd Stage","Magnet 1", "Magnet 2","Helium Pot",
                                       "Switch Heater", isramping bool, is stablebool] 
    TCon_add : VISA address for the temperature Controller
    Backup_TConAdd: The contents of the GPIB entry from the gUI to allow Reconnecting if incorrect 
    Addresses entered.
    WARNING: AT CURRENT MOMENT, NO WAY TO RECONNECT TO TEMPERATURE MONITOR. HAVE TO CLOSE+REOPENT WINDOW
    
    TMon_add : VISA address for a Temperature Monitor.

    """
    rm = pyvisa.ResourceManager()
    Abort = False
    IsRamping=False#Bool to tag if temperature is ramping
    IsStable=False#Placeholder for Stability criteria.
    try:
        T_Con = Inst.lakeshore350(rm,TCon_add)
        if TMon_add != None:
            T_Mon=Inst.lakeshore218(rm,TMon_add)
        else:
            T_Mon=None
        print("Successfully Connected To Temperature Controller")
    except Exception as e:
        print(e)
        print("Error IN Connection")
        Pipe.send("Esc")
        Abort=True


    while Abort == False:
    
        Current_TCon_VTI=T_Con.getTempN("A")
        Current_TCon_Sample=T_Con.getTempN("B")
        if T_Mon != None:
            Current_TMon=T_Mon.getTempAll()
            
        else:
            Current_TMon=[]
        Pipe.send([time.time(),Current_TCon_VTI,Current_TCon_Sample,*Current_TMon,IsRamping,IsStable])#sends the current reading of the pipes to be read
        
        #time.sleep(0.25)
# =============================================================================
#         PIPE NOW CHECKS FOR INPUT
# =============================================================================
        if Pipe.poll():# If this isnt there, Pipe will Wait for input and do nothing
            Comm = Pipe.recv()

            if Comm=="STOP":
                Abort=True
            elif Comm =="ALLOFF":
                T_Con.allOff()
            elif Comm == "NORAMP":
                T_Con.setRampRate(1,0,0)
    # =============================================================================
    #        PIPE NOW CHECKS FOR GET COMMANDS
    # =============================================================================
            else:
                Param=re.split(";", str(Comm))
                if len(Param) ==2:#I'M VIOLATING MY OWN GUIDELINES AND YOU CANT STOP ME!!!
                #In Essence, as the "Read" Command wont send a setpoint, we can take Param of Len 2 to always be a "Get" command
                #Yes this does allow you to Send "T; Red Dragon Archfiend" as a valid get command but SHHH. 
                    if re.search("HMD",Param[0]):
                        mode=T_Con.getOutputMode(1)[0]
                        if mode==3:
                            mode="MO"
                        elif mode==2:
                            mode="Z"
                        elif mode==1:
                            mode="MP"
                        Pipe.send(mode)
                    elif re.search("T",Param[0]):
                        Pipe.send(T_Con.getTempSetpointN(1))
                    elif re.search("PO",Param[0]):
                        Pipe.send(T_Con.readMout(1))
                    elif re.search("PID",Param[0]):
                        Pipe.send([T_Con.getPID(1)])
                    elif re.search("RNG",Param[0]):
                        Pipe.send(T_Con.getRange(1))
                    elif re.search("RAMP",Param[0]):
                        Pipe.send(T_Con.getRampRate(1))
                    else:
                        print("Invalid Get Command")
    # =============================================================================
    #             PIPE NOW CHECKS FOR SET COMMANDS
    # =============================================================================
                elif len(Param)==3:
                    #again, assuming a command with 3 things would be a Set command
                    if re.search("HMD",Param[0]):
                        
                        if re.search("MO",Param[2]):
                            T_Con.setOutputMode(1,3,1,0)
                        elif re.search("Z",Param[2]):
                            T_Con.setOutputMode(1,2,1,0)
                        elif re.search("MP",Param[2]):
                            T_Con.setOutputMode(1,1,1,0)
                        
                    elif re.search("T",Param[0]):
                        T_Con.setTempSetpointN(1,float(Param[2]))
                    elif re.search("PO",Param[0]):
                        T_Con.ManOut(1,float(Param[2]))
                        Pipe.send(T_Con.readMout(1))
                    elif re.search("PID",Param[0]):
                        list_PID=Param[2].split(",")
                        #break up PID into a Len3 list. This is why you split by semicolon in the first case
                        T_Con.setPID(1,float(list_PID[0]),float(list_PID[1]),float(list_PID[2]))
                    elif re.search("RNG",Param[0]):
                        T_Con.setRange(1,int(Param[2]))
                    elif re.search("RAMP",Param[0]):
                        T_Con.setRampRate(1,1,float(Param[2]))
                    else:
                        print("Invalid Set Command")
        # =============================================================================
        #             ERROR/DO NOTHING CASE
        # =============================================================================
                else:
                    if Comm=="STOP":
                        Abort=True #think this may just be a Runtime of various things issue, so redeclare this? 
                        #TODO: This is not good practice. Fix.
                    else:
                        print("Invalid String Command Seen IN Temp. Controller! Got{}".format(Param))
                time.sleep(0.1)#allow buffer to clear before querying it again
    return()#once we've exited that While loop should be ok to return and close the fn.

def OI_503_Controller(Pipe,TCon_add, LMon_add=None):
    """
    Multiprocessing Process for Temperature Monitoring Using the OI503
    Last 2 elements in the pipe must always be the IsRamping and IsStable Bools. Make sure to Slice before plotting!
    Currently Assumes that you're doing Loop 1 connected to sensor A
        
    Special Commands that can be sent through the pipe to the Controller:
        ALLOFF=Turns the Heaters on the Controller OFF
        
    Standard Commands have the Syntax;
        Parameter; X; Y
        X is either S(set) or G(get). Y is the Parameter to Be entered. Assumed Sanitary at this pt.
        
    Parameters are
    HMD; Heater Mode, can be be Z (Zone), MP (Manual PID) or MO (Manual Output).
    T; Setpoint in K
    PO; Manual Power output in %
    PID: PID paramters. In this case, the Parameter is a list of len 3 containing P I and D
    GAS:NV Gas Percentage in % of a full turn.
    RAMP: Ramp rate in K/min:Not implimented.
        
      

    Parameters
    ----------
    Pipe : Pipe
        PipeSend to pass things through
        Data is passed in the format; [current Time,VTI Temperature, Sample Temperature,
                                       "1st Stage","2nd Stage","Magnet 1", "Magnet 2","Helium Pot",
                                       "Switch Heater", isramping bool, is stablebool] 
    TCon_add : VISA address for the temperature Controller.
    NB: Assumes that at this point the correct Address is Entered. If not, should Return and Close itself.
    
    LMon_add : VISA address for a LevelMeter.

    """
    rm = pyvisa.ResourceManager()
    Abort = False
    IsRamping=False#Bool to tag if temperature is ramping
    IsStable=False#Placeholder for Stability criteria.
    try:
        T_Con = Inst.OI_503(rm,TCon_add)
        if LMon_add != None:
            L_Mon=Inst.OI_ILM(rm,LMon_add)
        else:
            L_Mon=None
        print("Successfully Connected To Temperature Controller")
    except Exception as e:
        print(e)
        print("Error IN Connection")
        Pipe.send(e)
        Pipe.send("Esc")
        Abort=True

   
    while Abort == False:
    
        Current_TCon_VTI=T_Con.getTempN("1")
        Current_TCon_Sample=T_Con.getTempN("2")
        
        Current_LMon=[]
        if L_Mon is not None:
            Current_LMon.append(L_Mon.getLevelN(1))
            Current_LMon.append(L_Mon.getLevelN(2))#query channels 1 and 2. If there is no Lmon, should return a blank list
        Pipe.send([time.time(),Current_TCon_VTI,Current_TCon_Sample,*Current_LMon,IsRamping,IsStable])
        #sends the current reading of the pipes to be read
        
        #time.sleep(0.25)
# =============================================================================
#         PIPE NOW CHECKS FOR INPUT
# =============================================================================
        if Pipe.poll():# If this isnt there, Pipe will Wait for input and do nothing
            Comm = Pipe.recv()

            if Comm=="STOP":
                Abort=True
            elif Comm =="ALLOFF":
                T_Con.allOff()

    # =============================================================================
    #        PIPE NOW CHECKS FOR GET COMMANDS
    # =============================================================================
            else:
                Param=re.split(";", str(Comm))
                if len(Param) ==2:#I'M VIOLATING MY OWN GUIDELINES AND YOU CANT STOP ME!!!
                #In Essence, as the "Read" Command wont send a setpoint, we can take Param of Len 2 to always be a "Get" command
                #Yes this does allow you to Send "T; Firewall Dragon Darkfluid Neo Tempest THz"
                #as a valid get command but SHHH. 
                    if re.search("HMD",Param[0]):
                        mode=T_Con.examine()
                        if mode[0]==0 or mode[0]==2:
                            mode="MO"
                        elif mode[-1]==1:
                            mode="Z"
                        elif mode[-1]==0:
                            mode="MP"
                        Pipe.send(mode)
                    elif re.search("T",Param[0]):
                        Pipe.send(T_Con.getTempSetpoint())
                    elif re.search("PO",Param[0]):
                        Pipe.send(T_Con.getHeaterPower())
                    elif re.search("PID",Param[0]):
                        Pipe.send([T_Con.getPID()])
                    elif re.search("GAS",Param[0]):
                        Pipe.send(T_Con.getGasFlow())
                    elif re.search("RAMP",Param[0]):
                        print("Get ramp is not implimented atm, scream at Craig!")
                    else:
                        print("Invalid Get Command")
    # =============================================================================
    #             PIPE NOW CHECKS FOR SET COMMANDS
    # =============================================================================
                elif len(Param)==3:
                    #again, assuming a command with 3 things would be a Set command
                    if re.search("HMD",Param[0]):
                        
                        if re.search("MO",Param[2]):
                            T_Con.setOutputMode(0)#Currently just uses Manual Heater/Gas.
                        elif re.search("Z",Param[2]):
                            T_Con.setOutputMode(1)
                            #again, Manual Gas output
                            T_Con.setPIDMode(1)
                        elif re.search("MP",Param[2]):
                            T_Con.setOutputMode(1)
                            #again, Manual Gas output
                            T_Con.setPIDMode(0)
                        
                    elif re.search("T",Param[0]):
                        T_Con.setTempSetpoint(float(Param[2]))
                    elif re.search("PO",Param[0]):
                        T_Con.ManOut(float(Param[2]))
                        Pipe.send(T_Con.readMout(1))
                    elif re.search("PID",Param[0]):
                        list_PID=Param[2].split(",")
                        #break up PID into a Len3 list. This is why you split by semicolon in the first case
                        T_Con.setPID(float(list_PID[0]),float(list_PID[1]),float(list_PID[2]))
                    elif re.search("GAS",Param[0]):
                        T_Con.setGasFlow(Param[2])
                    elif re.search("RAMP",Param[0]):
                        print("Set ramp is not implimented atm, scream at Craig!")
                        #TODO:Impliment Ramp
                        #For those on a code-dive; There isnt a nice "Ramp Setpoint" included
                        #with the 503. You have to program a sweep, which is a pain from both
                        #sides. You COULD Kludge something where the setpoint is programmatically
                        #ramped at a given rate but its not a priority for me- CSK 05/25
                    else:
                        print("Invalid Set Command")
        # =============================================================================
        #             ERROR/DO NOTHING CASE
        # =============================================================================
                else:
                    if Comm=="STOP":
                        Abort=True #think this may just be a Runtime of various things issue, so redeclare this? 
                        #TODO: This is not good practice. Fix.
                    else:
                        print("Invalid String Command Seen IN Temp. Controller! Got{}".format(Param))
                time.sleep(0.1)#allow buffer to clear before querying it again
    return()