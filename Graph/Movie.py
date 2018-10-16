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
        self.actors=[]
        for actor in actors:
            self.actors.append(actor.replace(" ","_"))
        
        
    def print_movie(self):
        print(self.name+" "+str(self.year)+" "+str(self.gross),end=': ')
        print(self.actors)
        
    def dictify(self):
        dict={}
        dict["name"]=self.name
        dict["year"]=self.year
        dict["actors"]=self.actors
        dict["box_office"]=self.gross
        return dict