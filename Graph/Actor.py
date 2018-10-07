'''
Created on Oct 6, 2018

@author: kwang66
'''

class Actor(object):
    '''
    holds information about an actor
    '''
    def __init__(self, name, age, movies):
        self.name=name
        self.age=age
        self.movies=movies
        
    def printActor(self):
        print(self.name+" "+str(self.age)+": ",end='')
        print(self.movies)
        