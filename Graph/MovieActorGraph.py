'''
Created on Oct 7, 2018

@author: kwang66
'''

from Graph.Movie import Movie
from Graph.Actor import Actor
from Graph.Edge import Edge
import operator
import json
from audioop import reverse

class MovieActorGraph(object):
    '''
    read json from movie.json, actor.json and build a graph based on that
    '''


    def __init__(self):
        '''
        Constructor
        '''
        actorJson = open("../Scraper/actor.json")
        movieJson = open("../Scraper/movie.json")
        actorData = json.load(actorJson)[1:]
        movieData = json.load(movieJson)[1:]
        self.makeActorList(actorData)
        self.makeMoiveList(movieData)
        self.makeEdge()
        
        
    def makeActorList(self,actorData):
        self.actorList=[]
        for actor in actorData:
            actorInstance = Actor(actor["name"],actor["age"],actor["movies"])
            self.actorList.append(actorInstance)
            
    def makeMoiveList(self,movieData):
        self.movieList=[]
        for movie in movieData:
            movieInstance = Movie(movie["name"],movie["year"],movie["gross"],movie["actors"])
            self.movieList.append(movieInstance)
            
    def makeEdge(self):
        self.edgeList=[]
        for movie in self.movieList:
            numActor = len(movie.actors)
            if (numActor==0):
                continue
            weightBase= (1+numActor)*numActor/2
            for actor in self.actorList:
                if (movie.name in actor.movies and actor.name in movie.actors):
                    weight = (numActor-movie.actors.index(actor.name)-1)/weightBase
                    weight = weight*movie.gross
                    edge = Edge(actor,movie,weight)
                    self.edgeList.append(edge)
    
    def getMovie(self,movieName):
        for movie in self.movieList:
            if (movie.name==movieName):
                return movie
        return None
    
    def getMoviesOfActor(self,actorName):
        moviesOfActor=[]
        for edge in self.edgeList:
            if (edge.actor.name==actorName):
                moviesOfActor.append(edge.movie)
        return moviesOfActor

    def getActorsOfMovie(self,movieName):
        actorOfMovie=[]
        for edge in self.edgeList:
            if (edge.movie.name==movieName):
                actorOfMovie.append(edge.actor)
        return actorOfMovie
    
    def getMostGrossing(self,listCapacity):
        actorIncomeDict={}
        for edge in self.edgeList:
            if (edge.actor.name not in actorIncomeDict.keys()):
                actorIncomeDict[edge.actor.name]=edge.weight
            else:
                actorIncomeDict[edge.actor.name]=actorIncomeDict[edge.actor.name]+edge.weight
        actorIncomeDict=sorted(actorIncomeDict.items(), key=lambda kv:kv[1],reverse=True)
        actorIncomeDict=actorIncomeDict[:min(listCapacity,len(actorIncomeDict))]
        return actorIncomeDict
    
    def getOldest(self,listCapacity):
        ageDict={}
        for actor in self.actorList:
            ageDict[actor.name]=actor.age
        ageDict = sorted(ageDict.items(), key=lambda kv:kv[1],reverse=True)
        ageDict = ageDict[:min(listCapacity,len(ageDict))]
        return ageDict
    
    def getMovieByYear(self,year):
        movies=[]
        for movie in self.movieList:
            if (movie.year==year):
                movies.append(movie)
        return movies
    
    def getActorByAge(self,age):
        actors=[]
        for actor in self.actorList:
            if (actor.age==age):
                actors.append(actor)
        return actors