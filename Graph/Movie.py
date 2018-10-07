'''
Created on Oct 6, 2018

@author: kwang66
'''

class Movie(object):
    '''
    holds information about a movie
    '''
    def __init__(self, name, year, gross, actors):
        self.name=name
        self.year=year
        self.gross=gross
        self.actors=actors
        
        
    def printMovie(self):
        print(self.name+" "+str(self.year)+" "+str(self.gross),end=': ')
        print(self.actors)