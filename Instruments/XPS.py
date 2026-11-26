import os
from pathlib import Path
from newportxps import NewportXPS
import math
import csv
import numpy as np

class XPS(object):
    """
    XPS Instrument.
    Functions mostly taken from: https://github.com/Leeds-THz/TDSpy/blob/dev/XPSHelper.py
    """
    def __init__(self,ip, user = "Administrator", password = "Administrator"):
        # 'known_hosts' filepath
        kfFilepath = "{}\\.ssh\\known_hosts.".format(os.path.expanduser('~'))

        # Check if the 'known_hosts' file exists
        if not os.path.exists(kfFilepath):
            # Create directory if it doesn't exist
            Path(os.path.dirname(kfFilepath)).mkdir(parents=True, exist_ok=True)
            # Gets the ssh keys from the xps and store to 'known_hosts'
            os.system("ssh-keyscan {} > {}".format(ip, kfFilepath))

        # Connects to the XPS and creates an object
        self.xps = NewportXPS(ip, username=user, password=password)
        
        self.isDSeries = any([m in self.xps.firmware_version for m in ['XPS-D', 'HXP-D', 'XPS-RL']])
        
        
    def __del__(self):
        self.xps.disconnect()
        pass
    
    def GotoDelay(self, stage, delay, zeroOffset, passes, reverse):
        # Get max velocity settings
        maxVeloAcc = self.xps._xps.PositionerMaximumVelocityAndAccelerationGet(self.xps._sid, stage)
    
        # Set velocity to max
        err, msg = self.xps._xps.PositionerSGammaParametersSet(self.xps._sid, stage, maxVeloAcc[1], maxVeloAcc[2], 0.005, 0.05)
    
        # Check for errors
        if err != 0:
            return err, msg
    
        # Move stage to start pos
        self.xps.move_stage(stage, ConvertPsToMm(delay, zeroOffset, passes, reverse))
    
        return err, msg

    def GetXPSErrorString(self, errorCode):
        # Check for errors
        if errorCode != 0:
            # Get XPS error string
            _, errString = self.xps._xps.ErrorStringGet(self.xps._sid, errorCode)
    
            return errString
        else:
            return "No XPS Error"
        
    def GetGatheringFile(self, localFile = None):
        # Delete existing gathering file
        if localFile == None:
            localFile = 'Gathering.dat'
        
        if os.path.exists(localFile):
            os.remove(localFile)
    
        gatheringLocation = ""
        
        if self.isDSeries:
            gatheringLocation = '/Admin/Public/Gathering/Gathering.dat'
        else:
            gatheringLocation = 'Public/Gathering//Gathering.dat'
    
        self.xps.ftpconn.connect()
    
        #self.xps.ftpconn._conn.get('/Admin/Public/Gathering/Gathering.dat', localFile)
    
        self.xps.ftpconn.save(gatheringLocation, localFile)
    
        self.xps.ftpconn.close()
    
    
    def InitXPSGathering(self, stage, startDelay, stepDelay, stopDelay, zeroOffset, passes, reverse, bandwidth, tc, tcToWait = 4, extraGPIO = True, analogueGain=1):
        scanStageSpeed = GetBandwidthStageSpeed(bandwidth, tc, tcToWait, passes) # mm/s
        scanSteps = ConvertPsToMm(stepDelay, 0, passes, False) # mm
        scanPeriod = scanSteps / scanStageSpeed # s
    
        expectedPoints = int(math.floor(((stopDelay - startDelay) / stepDelay) + 2))
        xpsDivisor = int(math.floor(scanPeriod * 10000))
    
        # Kill Any Gathering Currently Running
        err, msg = self.xps._xps.GatheringStop(self.xps._sid)
    
        # Check for errors
        if err != 0:
            return err, msg
        
        err, msg = self.xps._xps.GatheringReset(self.xps._sid)
    
        # Check for errors
        if err != 0:
            return err, msg
        
        if self.isDSeries:
            gpio = "GPIO4"
        else:
            gpio = "GPIO2"
    
        # Set GPIO analogue gain
        err, msg = self.xps._xps.GPIOAnalogGainSet(self.xps._sid, ["{0}.ADC1".format(gpio), "{0}.ADC2".format(gpio), "{0}.ADC3".format(gpio), "{0}.ADC4".format(gpio)], [analogueGain, analogueGain, analogueGain, analogueGain])
    
        # Check for errors
        if err != 0:
            return err, msg
    
        # Get max velocity settings
        maxVeloAcc = self.xps._xps.PositionerMaximumVelocityAndAccelerationGet(self.xps._sid, stage)
    
        # Set velocity to max
        err, msg = self.xps._xps.PositionerSGammaParametersSet(self.xps._sid, stage, maxVeloAcc[1], maxVeloAcc[2], 0.005, 0.05)
    
        # Check for errors
        if err != 0:
            return err, msg
    
        # Move stage to start pos
        self.xps.move_stage(stage, ConvertPsToMm(startDelay, zeroOffset, passes, reverse))
    
        # Set stage velocity based on required THz bandwidth
        err, msg = self.xps._xps.PositionerSGammaParametersSet(self.xps._sid, stage, scanStageSpeed, maxVeloAcc[2], 0.005, 0.05)
    
        # Check for errors
        if err != 0:
            return err, msg
    
    
        # Kill Any Gathering Currently Running
        err, msg = self.xps._xps.GatheringStop(self.xps._sid)
    
        # Check for errors
        if err != 0:
            return err, msg
        
        err, msg = self.xps._xps.GatheringReset(self.xps._sid)
    
        # Check for errors
        if err != 0:
            return err, msg
    
        # Set gathering config
        if extraGPIO:
            err, msg = self.xps._xps.GatheringConfigurationSet(self.xps._sid, ["{}.CurrentPosition".format(stage), "{0}.ADC1".format(gpio), "{0}.ADC2".format(gpio), "{0}.ADC3".format(gpio), "{0}.ADC4".format(gpio)])
        else :
            err, msg = self.xps._xps.GatheringConfigurationSet(self.xps._sid, ["{}.CurrentPosition".format(stage), "{0}.ADC1".format(gpio), "{0}.ADC2".format(gpio)])
    
        # Check for errors
        if err != 0:
            return err, msg
    
        # Set event trigger
        err, msg = self.xps._xps.EventExtendedConfigurationTriggerSet(self.xps._sid, ("{}.SGamma.MotionStart".format(stage),), ("",), ("",), ("",), ("",))
    
        # Check for errors
        if err != 0:
            return err, msg
    
        # Set event action
        err, msg = self.xps._xps.EventExtendedConfigurationActionSet(self.xps._sid, ("GatheringRun",), (str(expectedPoints),), (str(xpsDivisor),), ("",), ("",))
    
        # Check for errors
        if err != 0:
            return err, msg
    
        # Event ext. Start
        err, msg = self.xps._xps.EventExtendedStart(self.xps._sid)
    
        # Check for errors
        return err, msg
        
    
    def RunGathering(self, stage, startDelay, stepDelay, stopDelay, zeroOffset, passes, reverse, localFile = None):
        # Move to end position
        self.xps.move_stage(stage, ConvertPsToMm(stopDelay, zeroOffset, passes, reverse))
    
        # Gathering stop + save
        err, msg = self.xps._xps.GatheringStopAndSave(self.xps._sid)
    
        # Check for errors
        if err != 0:
            return err, msg
    
        # Get gathering file
        self.GetGatheringFile(localFile)
    
        return err, msg
        
    def ReadGathering(self, startDelay, stepDelay, stopDelay, zeroOffset, passes, reverse, lockinSensitivity, localFile = None, headerLines = 2, extraGPIO = True, analogueGain=1):
        if localFile == None:
            localFile = "Gathering.dat"
        
        # Empty variables to store gathering data to
        delay = []
        sigX = []
        sigY = []
        sigA = []
        sigB = []
    
        # Open gathering file
        with open(localFile, mode='r') as dataFile:
            dataReader = csv.reader(dataFile, delimiter='\t')
    
            # Skip header lines
            for i in range(headerLines):
                next(dataReader, None)
    
            # Read file row-by-row
            for row in dataReader:
                # Store data to variables
                delay.append(ConvertMmToPs(float(row[0]), zeroOffset, passes, reverse))
                sigX.append((float(row[1]) / analogueGain) * lockinSensitivity)
                sigY.append((float(row[2]) / analogueGain) * lockinSensitivity)
    
                if extraGPIO:
                    sigA.append((float(row[3]) / analogueGain) * lockinSensitivity)
                    sigB.append((float(row[4]) / analogueGain) * lockinSensitivity)
    
        # Interpolate data
        delayInterp = np.arange(startDelay, stopDelay + stepDelay, stepDelay)
        xInterp = np.interp(delayInterp, delay, sigX)
        yInterp = np.interp(delayInterp, delay, sigY)
        
        aInterp = np.interp(delayInterp, delay, sigA)
        bInterp = np.interp(delayInterp, delay, sigB)
    
        if extraGPIO:
            return {"Delay": delayInterp, "X": xInterp, "Y": yInterp, "A": aInterp, "B": bInterp}
        else:
            return {"Delay": delayInterp, "X": xInterp, "Y": yInterp}
    
        
    
####################################################################
# UNIT FUNCTIONS
####################################################################

def ConvertPsToMm(ps, zeroOffset, passes, reverse):
    c = 0.3 # Speed of light in mm/ps

    if reverse:
        return (-1 * c * (1 / passes) * (ps + zeroOffset)) 
    else:
        return (c * (1 / passes) * (ps + zeroOffset))

def ConvertMmToPs(mm, zeroOffset, passes, reverse):
    c = 0.3 # Speed of light in mm/ps

    if reverse:
        return ((mm * passes) / -c) - zeroOffset
    else:
        return ((mm  * passes) / c) - zeroOffset

def GetBandwidthStageSpeed(bandwidth, tc, tcToWait, passes):
    # This code is taken from Josh's THz scan program
    minSamplingPeriod = 1 / (bandwidth * 2) # ps
    maxStageSpeed = minSamplingPeriod / (tc * tcToWait) # ps/s
    
    return maxStageSpeed * 0.3 * (1 / passes) # mm/s
