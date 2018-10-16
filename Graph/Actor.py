'''
Created on Oct 6, 2018

@author: kwang66
'''

class Actor(object):
    '''
    holds information about an actor
    '''
    def __init__(self, name, age, total_gross, movies):
        self.name=name
        self.age=age
        self.total_gross=total_gross
        self.movies=[]
        for movie in movies:
            self.movies.append(movie.replace(" ","_"))
        
        
    def print_actor(self):
        print(self.name+" "+str(self.age)+": ",end='')
        print(self.movies)
    
    def is_in_same_movie(self,other):
        for movie in self.movies:
            if (movie in other.movies):
                return True
        return False
    
    def dictify(self):
        dict={}
        dict["name"]=self.name
        dict["age"]=self.age
        dict["total_gross"]=self.total_gross
        dict["movies"]=self.movies
        return dict