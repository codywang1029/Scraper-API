'''
Created on Oct 14, 2018

@author: Kexiang Wang
'''
from graph.movie_actor_graph import MovieActorGraph

if __name__ == '__main__':
    graph=MovieActorGraph(json_file="data.json")
    print(graph.year_gross_correlation())