'''
Created on Oct 14, 2018

@author: Kexiang Wang
'''

from flask import Flask, request, jsonify,make_response,abort
from graph.movie_actor_graph import MovieActorGraph
from graph.actor import Actor
from graph.movie import Movie

api = Flask(__name__)
graph = MovieActorGraph(json_file="data.json")

@api.route('/actors')
def get_filtered_actor():
    '''
    get list of actors that satisfy the filter
    '''
    name=""
    age=-1
    if ("name" in request.args.keys()):
        name=request.args["name"]
    if ("age" in request.args.keys()):
        age=int(request.args["age"])
    name_result=[]
    if (name != ""):
        for actor in graph.actorList:
            if (name in actor.name):
                name_result.append(actor)
    age_result=[]
    if (age!=-1):
        for actor in graph.actorList:
            if (int(age) == actor.age):
                age_result.append(actor)
    result=[]
    if (age!=-1 and name!=""):
        for actor1 in name_result:
            for actor2 in age_result:
                if (actor1.name==actor2.name):
                    result.append(actor1)
    elif(name==""):
        result=age_result
    else:
        result=name_result  
    if (result == []):
        abort(404)
    dict_list=[]
    for actor in result:
        main_dict={}
        dict=actor.dictify()
        main_dict[actor.name]=dict
        dict_list.append(main_dict)
    return jsonify(dict_list)

@api.route('/movies')
def get_filtered_movie():
    '''
    get list of movies that satisfy the filter
    '''
    name=""
    year=-1
    if ("name" in request.args.keys()):
        name=request.args["name"]
    if ("year" in request.args.keys()):
        year=int(request.args["year"])
    name_result=[]
    if (name != ""):
        for movie in graph.movieList:
            if (name in movie.name):
                name_result.append(movie)
    year_result=[]
    if (year!=-1):
        for movie in graph.movieList:
            if (int(year) == movie.year):
                year_result.append(movie)
    result=[]
    if (year!=-1 and name!=""):
        for movie1 in name_result:
            for movie2 in year_result:
                if (movie1.name==movie2.name):
                    result.append(movie1)
    elif(name==""):
        result=year_result
    else:
        result=name_result
    if (result == []):
        abort(404) 
    dict_list=[]
    for movie in result:
        main_dict={}
        dict=movie.dictify()
        main_dict[movie.name]=dict
        dict_list.append(main_dict)
    return jsonify(dict_list)

@api.route('/actors/<name>', methods=['GET'])
def get_actor_by_name(name):
    actor=graph.get_actor(name)
    if (actor==None):
        abort(404)
    return jsonify(actor.dictify())

@api.route('/movies/<name>', methods=['GET'])
def get_movie_by_name(name):
    movie=graph.get_movie(name)
    if (movie==None):
        abort(404)
    return jsonify(movie.dictify())


@api.route('/actors/<name>',methods=['PUT'])
def update_actor(name):
    actor=graph.get_actor(name)
    if (actor==None):
        abort(404)
    if not request.json:
        abort(400)
    data=request.json
    if ('name' in data):
        if (type(data['name']) != str):
            abort(400)
        else:
            actor.name=data['name']
    if ('age' in data):
        if (type(data['age']) != int):
            abort(400)
        else:
            actor.age=data['age']
    if 'movies' in data:
        actor.movies=data['movies']
    if ("total_gross" in data):
        if (type(data['total_gross']) != float and type(data['total_gross'])!=int):
            abort(400)
        else:
            actor.total_gross=data['total_gross']
    return jsonify(actor.dictify())

@api.route('/movies/<name>',methods=['PUT'])
def update_movie(name):
    movie=graph.get_movie(name)
    if (movie==None):
        abort(404)
    if not request.json:
        abort(400)
    data=request.json
    if ('name' in data):
        if (type(data['name']) != str):
            abort(400)
        else:
            movie.name=data['name']
    if ('year' in data):
        if (type(data['year']) != int):
            abort(400)
        else:
            movie.age=data['year']
    if 'actors' in data:
        movie.actors=data['actors']
    if ("box_office" in data):
        if (type(data['box_office']) != float and type(data['box_office'])!=int):
            abort(400)
        else:
            movie.gross=data['box_office']
    return jsonify(movie.dictify())

@api.route('/actors',methods=['POST'])
def post_actor():
    data=request.json
    if (not data):
        abort(400,"no data")
    if ("name" not in data or type(data['name']) != str):
        abort(400,"Bad name")
    if ("age" not in data or type(data['age']) != int):
        abort(400,"Bad age")
    if ("movies" not in data):
        abort(400,"No movies")
    total_gross=request.json.get('total_gross',0)
    actor=Actor(request.json['name'].replace(" ","_"),request.json['age'],total_gross,request.json["movies"])
    graph.add_actor(actor)
    return jsonify(actor.dictify()),201

@api.route('/movies',methods=['POST'])
def post_movie():
    data=request.json
    if (not data):
        abort(400)
    if ("name" not in data or type(data['name']) != str):
        abort(400)
    if ("year" not in data or type(data['year']) != int):
        abort(400)
    if ("actors" not in data):
        abort(400)
    if ("box_office" not in data):
        abort(400)
    movie=Movie(request.json['name'].replace(" ","_"),request.json['year'],request.json["box_office"],request.json["actors"])
    graph.add_movie(movie)
    return jsonify(movie.dictify()),201

@api.route('/actors/<name>',methods=['DELETE'])
def delete_actor(name):
    actor=graph.get_actor(name)
    if (actor==None):
        abort(404)
    graph.delete_actor(actor)
    return jsonify({"success":"deleted"})

@api.route('/movies/<name>',methods=['DELETE'])
def delete_movie(name):
    movie=graph.get_movie(name)
    if (movie==None):
        abort(404)
    graph.delete_movie(movie)
    return jsonify({"success":"deleted"})

@api.route('/actors/hub',methods=['GET'])
def get_hub():
    actor=graph.get_hub()
    return jsonify(actor.dictify())

@api.route('/actors/age_gross',methods=['GET'])
def get_age_grossing_correlation():
    correlation=graph.age_gross_correlation()
    return jsonify(correlation)

@api.route('/movies/year_gross',methods=['GET'])
def get_year_grossing_correlation():
    correlation=graph.year_gross_correlation()
    return jsonify(correlation)
 
@api.route('/actors/rising/<int:list_capacity>',methods=['GET'])
def get_most_rising(list_capacity):
    rising = graph.get_rising_actor(list_capacity)
    return jsonify(rising)
 
@api.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Content Not found'}), 404)



    

if __name__ == '__main__':
    api.run(debug=True)