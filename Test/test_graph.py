'''
Created on Oct 7, 2018

@author: kwang66
'''

import unittest
import random
from graph.movie_actor_graph import MovieActorGraph
from astropy.units import year


class TestGraphMethods(unittest.TestCase):
    
    def test_constructor(self):
        graph = MovieActorGraph(json_file="")
        self.assertFalse(len(graph.movieList)==0)
        self.assertFalse(len(graph.actorList)==0)
        self.assertFalse(len(graph.edgeList)==0)
        
    def test_get_movie(self):
        graph = MovieActorGraph(json_file="")
        movie = graph.get_movie(graph.movieList[0].name)
        self.assertEqual(movie.name, graph.movieList[0].name)
        self.assertEqual(movie.year, graph.movieList[0].year)
        self.assertEqual(movie.gross, graph.movieList[0].gross)
        for actor in movie.actors:
            self.assertTrue(actor in graph.movieList[0].actors)
        
    def test_get_movies_of_actor(self):
        graph = MovieActorGraph(json_file="")
        actor = graph.actorList[0]
        listOfMovie = graph.get_movies_of_actor(actor.name)
        for edge in graph.edgeList:
            if (edge.movie in listOfMovie and edge.actor.name==actor.name):
                listOfMovie.remove(edge.movie)
        self.assertEqual([], listOfMovie)
        
    def test_get_actors_of_movie(self):
        graph = MovieActorGraph(json_file="")
        movie = graph.movieList[0]
        listOfActors = graph.get_actors_of_movie(movie.name)
        for edge in graph.edgeList:
            if (edge.actor in listOfActors and edge.movie.name==movie.name):
                listOfActors.remove(edge.actor)
        self.assertEqual([], listOfActors)
    
    def test_get_most_grossing(self):
        graph = MovieActorGraph(json_file="")
        grossingActors = graph.get_most_grossing(10)
        self.assertEqual(10, len(grossingActors))
        moreActors = graph.get_most_grossing(100)[10:]
        for actor in moreActors:
            self.assertTrue(actor[1]<=grossingActors[9][1])
    
    def test_get_oldest(self):
        graph = MovieActorGraph(json_file="")
        oldActors = graph.get_oldest(5)
        self.assertEqual(5, len(oldActors))
        moreActors = graph.get_oldest(100)[5:]
        for actor in moreActors:
            self.assertTrue(actor[1]<=oldActors[4][1])
            
    def test_get_movie_by_year(self):
        graph = MovieActorGraph(json_file="")
        year2000 = graph.get_movie_by_year(2000)
        for movie in year2000:
            self.assertEqual(2000, movie.year)
    
    def test_get_actor_by_year(self):
        graph = MovieActorGraph(json_file="")
        year2010 = graph.get_actor_by_year(2010)
        for actor in year2010:
            movies = graph.get_movies_of_actor(actor.name)
            found=False
            for movie in movies:
                if (movie.year==2010):
                    found=True
                    break
            if (not found): 
                self.fail("actor"+actor.name+" was not in any 2010 movie")
    
    def test_get_hub(self):
        graph = MovieActorGraph(json_file="")
        hub=graph.get_hub()
        hub_conn=0
        for actor in graph.actorList:
            if (hub.is_in_same_movie(actor)):
                hub_conn=hub_conn+1
        for actor in graph.actorList:
            curr_conn=0
            for other in graph.actorList:
                if (actor.is_in_same_movie(other)):
                    curr_conn=curr_conn+1
            self.assertTrue(curr_conn<=hub_conn)
    
    def test_most_rising(self):
        graph = MovieActorGraph(json_file="")
        rising = graph.get_rising_actor(5)
        self.assertEqual(5, len(rising))
        moreActors = graph.get_rising_actor(100)[5:]
        for actor in moreActors:
            self.assertTrue(actor[1]<=rising[4][1])
    
    def test_diff(self):
        graph = MovieActorGraph(json_file="")
        actor=graph.actorList[random.randint(0,len(graph.actorList)-1)]
        diff = graph.get_diff(actor)
        movies=graph.get_movies_of_actor(actor)      
        movies=sorted(movies,key=lambda x:x.year, reverse=True)
        if (len(movies)<2):
            return 0
        most_recent=None
        second_recent=None
        for edge in graph.edgeList:
            if (edge.actor.name == actor and edge.movie.name==movies[0].name):
                most_recent=edge.weight
            if (edge.actor.name == actor and edge.movie.name==movies[1].name):
                second_recent=edge.weight
        self.assertEqual(most_recent-second_recent,diff)
    
    def test_age_gross(self):
        graph = MovieActorGraph(json_file="")
        age_gross=graph.age_gross_correlation()
        dictionary={}
        for item in age_gross:
            dictionary[item[0]]=item[1]
        group_num={}
        for actor in graph.actorList:
            age_group=actor.age-actor.age%10
            if (age_group in group_num.keys()):
                group_num[age_group]=group_num[age_group]+1
            else:
                group_num[age_group]=1
        for actor in graph.actorList:
            age = actor.age-actor.age%10
            self.assertTrue(dictionary[age]>=(actor.total_gross/group_num[age]))
    
    def test_year_gross(self):
        graph = MovieActorGraph(json_file="")
        year_gross=graph.year_gross_correlation()
        dictionary={}
        for item in year_gross:
            dictionary[item[0]]=item[1]
        group_num={}
        for movie in graph.movieList:
            year=movie.year-movie.year%5
            if (year in group_num.keys()):
                group_num[year]=group_num[year]+1
            else:
                group_num[year]=1
        for movie in graph.movieList:
            year = movie.year-movie.year%5
            self.assertTrue(dictionary[year]>=(movie.gross/group_num[year]))
      
if __name__ == '__main__':
    unittest.main()