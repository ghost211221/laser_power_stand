""" Class for optical structure that being explored during experiment.
    Laser hits structure and signal from structure is measured
"""
from random import uniform
class UUT():
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(UUT, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.__power = 0
        
    @property
    def power(self):
        return uniform(0.9, 1.0) * self.__power
    
    @power.setter
    def power(self, power):
        self.__power = power
