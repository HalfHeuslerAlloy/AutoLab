from zhinst.toolkit import Session
# For narrowband lockin, use package version zhinst 26.7.2

import time

class ZurichHF2LI(object):
    """
    Zurich HF2LI Lockin
    """
    def __init__(self,deviceName="DEV1830"):
        # Connect to the instrument
        self.session = Session("localhost", hf2=True)
        self.device = self.session.connect_device(deviceName)
        
        # Enable the lockins
        self.device.demods[0].enable(1)
        self.device.demods[0].enable()
        self.device.demods[3].enable(1)
        self.device.demods[3].enable()
        
        # Get the lockin scaling factor
        #self.scale = self.device.auxouts[0].scale
        #self.scale = self.device.getInt("/{0}/auxouts/0/scale".format(self.device))
        
        #self.dt = self.device.getDouble(f"/{device_id}/system/properties/timebase")

        # Set scale of all DAQ outs
        self.scale = self.device.auxouts[0].scale()
        self.device.auxouts[1].scale(self.scale)
        self.device.auxouts[2].scale(self.scale)
        self.device.auxouts[3].scale(self.scale)
        
        self.sensitivity = 1.0 / self.scale
        
        # Get the value of the time constant for lockin 1
        self.tc = self.device.demods[0].timeconstant()
        # Force lockin 2 to be identical
        self.device.demods[3].timeconstant(self.tc)
        
        # self.tc2 = self.device.demods[3].timeconstant()

        
    def __del__(self):
        pass
    
    def SetTimeConstant(self, tc):
        # Set the value of the time constant for lockin 1
        self.tc = self.device.demods[0].timeconstant(tc)
        # Force lockin 2 to be identical
        self.device.demods[3].timeconstant(tc)
    
    def GetSingleLockinValue(self, waitTc = True):
        self.device.demods[0].sample.subscribe()
        if waitTc :
            time.sleep(self.tc)
        self.device.demods[0].sample.unsubscribe()
        poll_result = self.session.poll()
        demod_sample = poll_result[self.device.demods[0].sample]
      
        x = demod_sample['x'][0]
        y = demod_sample['y'][0]
        
        return x, y
    
    def GetDoubleLockinValues(self, waitTc = True):
        self.device.demods[0].sample.subscribe()
        self.device.demods[3].sample.subscribe()
        if waitTc :
            time.sleep(self.tc)
        self.device.demods[0].sample.unsubscribe()
        self.device.demods[3].sample.unsubscribe()
        poll_result = self.session.poll()
        demod_sample1 = poll_result[self.device.demods[0].sample]
        demod_sample2 = poll_result[self.device.demods[3].sample]
      
        x1 = demod_sample1['x'][0]
        y1 = demod_sample1['y'][0]
        
        x2 = demod_sample2['x'][0]
        y2 = demod_sample2['y'][0]
        
        return x1, y1, x2, y2


if __name__== "__main__":
    zi = ZurichHF2LI()
    
    x1, y1, x2, y2 = zi.GetDoubleLockinValues()
    
    print("X1: {0}, Y1: {1}\nX2: {2}, Y2: {3}".format(x1, y1, x2, y2))

