'''
Created on Oct 7, 2018

@author: kwang66
'''

import unittest
from Graph.MovieActorGraph import MovieActorGraph


class TestGraphMethods(unittest.TestCase):
    
    def testConstructor(self):
        graph = MovieActorGraph()
        self.assertFalse(len(graph.movieList)==0)
        self.assertFalse(len(graph.actorList)==0)
        self.assertFalse(len(graph.edgeList)==0)
        
    def testGetMovie(self):
        graph = MovieActorGraph()
        movie = graph.getMovie(graph.movieList[0].name)
        self.assertEqual(movie.name, graph.movieList[0].name)
        self.assertEqual(movie.year, graph.movieList[0].year)
        self.assertEqual(movie.gross, graph.movieList[0].gross)
        for actor in movie.actors:
            self.assertTrue(actor in graph.movieList[0].actors)
        
    def testGetMoviesOfActor(self):
        graph = MovieActorGraph()
        actor = graph.actorList[0]
        listOfMovie = graph.getMoviesOfActor(actor.name)
        for edge in graph.edgeList:
            if (edge.movie in listOfMovie and edge.actor.name==actor.name):
                listOfMovie.remove(edge.movie)
        self.assertEqual([], listOfMovie)
        
    def testGetActorsOfMovie(self):
        graph = MovieActorGraph()
        movie = graph.movieList[0]
        listOfActors = graph.getActorsOfMovie(movie.name)
        for edge in graph.edgeList:
            if (edge.actor in listOfActors and edge.movie.name==movie.name):
                listOfActors.remove(edge.actor)
        self.assertEqual([], listOfActors)
    
    def testGetMostGrossing(self):
        graph = MovieActorGraph()
        grossingActors = graph.getMostGrossing(10)
        self.assertEqual(10, len(grossingActors))
        moreActors = graph.getMostGrossing(100)[10:]
        for actor in moreActors:
            self.assertTrue(actor[1]<=grossingActors[9][1])
    
    def testGetOldest(self):
        graph = MovieActorGraph()
        oldActors = graph.getOldest(5)
        self.assertEqual(5, len(oldActors))
        moreActors = graph.getOldest(100)[5:]
        for actor in moreActors:
            self.assertTrue(actor[1]<=oldActors[4][1])
            
    def testGetMovieByYear(self):
        graph = MovieActorGraph()
        year2000 = graph.getMovieByYear(2000)
        for movie in year2000:
            self.assertEqual(2000, movie.year)
    
    def testGetActorByYear(self):
        graph = MovieActorGraph()
        year2010 = graph.getActorByYear(2010)
        for actor in year2010:
            movies = graph.getMoviesOfActor(actor.name)
            found=False
            for movie in movies:
                if (movie.year==2010):
                    found=True
                    break
            if (not found): 
                self.fail("actor"+actor.name+" was not in any 2010 movie")

if __name__ == '__main__':
    unittest.main()