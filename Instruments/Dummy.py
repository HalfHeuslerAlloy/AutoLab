import numpy as np

class Dummy(object):
    """
    Just a simply test instrument. Call be used for testing
    Contains:
        - A,B,C,D
        - Random
        - Polynomial from A B C D channels
    """
    def __init__(self,rm,channel):
        self.channel = channel
        
        self.A = 0
        self.B = 0
        self.C = 0
        self.D = 0
        
        self.Rand = np.random.rand()
        
    def __del__(self):
        pass
    
    def SetA(self,N):
        self.A = N
    def SetB(self,N):
        self.B = N
    def SetC(self,N):
        self.C = N
    def SetD(self,N):
        self.D = N
    
    def Poly(self,X):
        return self.A*X**3 + self.B*X**2 + self.C*X + self.D