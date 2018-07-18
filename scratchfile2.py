# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 14:00:00 2018

@author: lwb1u18
"""

class dog():
    def __init__(self,breed,age,name):
        self.breed = breed
        self.age=age
        self.name=name
    
    def run(self):
        print(self.name, 'Ran!!')
    
bob = dog('poodle',11, 'bob')
bob.age = 15
dog('poodle',15,bob)


    
