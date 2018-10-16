'''
Created on Oct 7, 2018

@author: kwang66
'''

from graph.movie import Movie
from graph.actor import Actor
from graph.edge import Edge
import json

class MovieActorGraph(object):
    '''
    read json from movie.json, actor.json and build a graph based on that
    '''


    def __init__(self,json_file=""):
        '''
        Constructor
        '''
        if (json_file==""):
            actor_json = open("../scraper/actor.json")
            movie_json = open("../scraper/movie.json")
            actor_data = json.load(actor_json)[1:]
            movie_data = json.load(movie_json)[1:]
        else:
            data_json = open("../scraper/data.json",encoding='utf-8')
            data = json.load(data_json)
            actor_data=data[0]
            movie_data=data[1]
            actor_data=actor_data.values()
            movie_data=movie_data.values()
        self.make_actor_list(actor_data)
        self.make_moive_list(movie_data)
        self.make_edge()
            
    def make_actor_list(self,actor_data):
        '''
        construct self.actorList using actor json data
        '''
        self.actorList=[]
        for actor in actor_data:
            if (actor["movies"]==[]):
                continue
            if (actor["age"]<0):
                continue
            name = actor["name"].replace(" ","_")
            actorInstance = Actor(name,actor["age"], 0, actor["movies"])
            self.actorList.append(actorInstance)
            
    def make_moive_list(self,movie_data):
        '''
        construct self.movieList using movie json data
        '''
        self.movieList=[]
        for movie in movie_data:
            if (movie["actors"]==[]):
                continue
            gross=movie["box_office"]
            if (gross==0 or movie["year"]<1900):
                continue
            if (gross<1000):
                gross=gross*1000000
            name = movie["name"].replace(" ","_")
            movieInstance = Movie(name,movie["year"],gross,movie["actors"])
            self.movieList.append(movieInstance)
            
    def make_edge(self):
        '''
        construct edgeList using self.movieList and self.actorList
        Each edge connects a actor and a movie and weight
        weight is an approximate value of how much the actor earned in the movie
        weight is partially determined by how top the actor appear in the movie's cast list
        '''
        self.edgeList=[]
        for movie in self.movieList:
            num_actor = len(movie.actors)
            if (num_actor==0):
                continue
            weight_base= (1+num_actor)*num_actor/2
            for actor in self.actorList:
                if (movie.name in actor.movies and actor.name in movie.actors):
                    weight = (num_actor-movie.actors.index(actor.name)-1)/weight_base
                    weight = weight*movie.gross
                    edge = Edge(actor,movie,weight)
                    self.edgeList.append(edge)
                    actor.total_gross=actor.total_gross+weight
                    
    def add_actor(self,actor):
        '''
        add an actor into structure and update edges
        '''                
        self.actorList.append(actor)
        total_gross=0
        for movie in self.movieList:
            num_actor = len(movie.actors)
            if (num_actor==0):
                continue
            weight_base= (1+num_actor)*num_actor/2
            if (movie.name in actor.movies and actor.name in movie.actors):
                weight = (num_actor-movie.actors.index(actor.name)-1)/weight_base
                weight = weight*movie.gross
                edge = Edge(actor,movie,weight)
                self.edgeList.append(edge)
                total_gross=total_gross+weight
        if (actor.total_gross==0):
            actor.total_gross=total_gross
    
    def add_movie(self,movie):
        '''
        add an movie into structure and update edges
        ''' 
        self.movieList.append(movie)
        num_actor = len(movie.actors)
        if (num_actor==0):
            return
        weight_base= (1+num_actor)*num_actor/2
        for actor in self.actorList:
            if (movie.name in actor.movies and actor.name in movie.actors):
                weight = (num_actor-movie.actors.index(actor.name)-1)/weight_base
                weight = weight*movie.gross
                edge = Edge(actor,movie,weight)
                self.edgeList.append(edge)
                actor.total_gross=actor.total_gross+weight
                       
    def delete_actor(self,actor):
        for edge in self.edgeList:
            if (edge.actor.name==actor.name):
                self.edgeList.remove(edge)
                edge=None
        self.actorList.remove(actor)
        
    def delete_movie(self,movie):
        for edge in self.edgeList:
            if (edge.movie.name==movie.name):
                self.edgeList.remove(edge)
                edge=None 
        self.movieList.remove(movie)
    
    def get_movie(self,movie_name):
        '''
        get information of a movie given its name
        '''
        for movie in self.movieList:
            if (movie.name==movie_name):
                return movie
        return None
    
    def get_actor(self,actor_name):
        for actor in self.actorList:
            if (actor.name==actor_name):
                return actor
        return None
    
    def get_movies_of_actor(self,actorName):
        '''
        get filmography of an actor
        '''
        moviesOfActor=[]
        for edge in self.edgeList:
            if (edge.actor.name==actorName):
                moviesOfActor.append(edge.movie)
        return moviesOfActor

    def get_actors_of_movie(self,movieName):
        '''
        get cast of a movie
        '''
        actorOfMovie=[]
        for edge in self.edgeList:
            if (edge.movie.name==movieName):
                actorOfMovie.append(edge.actor)
        return actorOfMovie
    
    def get_most_grossing(self,list_capacity):
        '''
        get the top X earning actors, where X is the list_capacity
        '''
        actorIncomeDict={}
        for edge in self.edgeList:
            if (edge.actor.name not in actorIncomeDict.keys()):
                actorIncomeDict[edge.actor.name]=edge.weight
            else:
                actorIncomeDict[edge.actor.name]=actorIncomeDict[edge.actor.name]+edge.weight
        actorIncomeDict=sorted(actorIncomeDict.items(), key=lambda kv:kv[1],reverse=True)
        actorIncomeDict=actorIncomeDict[:min(list_capacity,len(actorIncomeDict))]
        return actorIncomeDict
    
    def get_oldest(self,list_capacity):
        '''
        get the oldest X actors, where X is the list_capacity
        '''
        ageDict={}
        for actor in self.actorList:
            ageDict[actor.name]=actor.age
        ageDict = sorted(ageDict.items(), key=lambda kv:kv[1],reverse=True)
        ageDict = ageDict[:min(list_capacity,len(ageDict))]
        return ageDict
    
    def get_movie_by_year(self,year):
        '''
        get all movies of a specific year
        '''
        movies=[]
        for movie in self.movieList:
            if (movie.year==year):
                movies.append(movie)
        return movies
    
    def get_actor_by_year(self,year):
        '''
        get all actors who was in a movie in a given year
        '''
        actors=[]
        for edge in self.edgeList:
            if (edge.movie.year==year):
                actors.append(edge.actor)
        return actors
    
    
    
    def get_hub(self):
        '''
        get one actor who have the most connection with other actors.
        "Two actors have a connection if they have acted in the same movie together."----course website
        '''
        global_hub=None
        global_max=0
        for actor in self.actorList:
            connection=0
            for other in self.actorList:
                if (actor.is_in_same_movie(other)):
                    connection=connection+1
            if (connection>global_max):
                global_max=connection
                global_hub=actor
        return global_hub
    
    def age_gross_correlation(self):
        '''
        return a sorted list of (age,income) tuple.
        income = (total income of an age group)/(number of people in the age group)
        '''
        group_num={}
        age_gross={}
        actor_income = self.get_most_grossing(len(self.actorList))
        for item in actor_income:
            actor_name=item[0]
            income=item[1]
            actor=self.get_actor(actor_name)
            age_group=actor.age-actor.age%10
            if (age_group in age_gross.keys()):
                age_gross[age_group]=age_gross[age_group]+income
                group_num[age_group]=group_num[age_group]+1
            else:
                age_gross[age_group]=income
                group_num[age_group]=1
        average={}
        for key in group_num.keys():
            average[key]=age_gross[key]/group_num[key]
        average=sorted(average.items(), key=lambda kv:kv[1],reverse=True)
        return average
    
    def year_gross_correlation(self):
        '''
        return a sorted list of (age,gross) tuple.
        gross = (total income of an year group)/(number of movies in the year group)
        '''
        year_gross={}
        group_num={}
        for movie in self.movieList:
            year_group=movie.year-movie.year%5
            if (year_group in year_gross.keys()):
                year_gross[year_group]=year_gross[year_group]+movie.gross
                group_num[year_group]=group_num[year_group]+1
            else:
                year_gross[year_group]=movie.gross
                group_num[year_group]=1
        
        average={}
        for key in group_num.keys():
            average[key]=year_gross[key]/group_num[key]
        average=sorted(average.items(), key=lambda kv:kv[1],reverse=True)
        return average
    
    def get_rising_actor(self,list_capacity):
        '''
        get the most <list_capacity> rising actors.
        an actor is rising if the income from his most recent movie is much larger than
        what he/she got from his/her second recent movie.
        '''
        diff_dict={}
        for actor in self.actorList:
            diff_dict[actor.name]=self.get_diff(actor.name)
        diff_dict=sorted(diff_dict.items(), key=lambda kv:kv[1],reverse=True)
        diff_dict=diff_dict[:min(list_capacity,len(diff_dict))]
        return diff_dict
    
    def get_diff(self,actor):
        '''
        get the difference of income between one actor's most recent movie and his/her second
        most recent movie.
        '''
        movies=self.get_movies_of_actor(actor)      
        movies=sorted(movies,key=lambda x:x.year, reverse=True)
        if (len(movies)<2):
            return 0
        most_recent=None
        second_recent=None
        for edge in self.edgeList:
            if (edge.actor.name == actor and edge.movie.name==movies[0].name):
                most_recent=edge.weight
            if (edge.actor.name == actor and edge.movie.name==movies[1].name):
                second_recent=edge.weight
        return most_recent-second_recent
    
        