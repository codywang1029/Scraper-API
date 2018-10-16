'''
Created on Oct 6, 2018

@author: Kexiang Wang(kwang66)
'''
import requests
import logging

import json
import time
import random
from bs4 import BeautifulSoup
from graph.actor import Actor
from graph.movie import Movie
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry



def encode_actor(actor):
    '''encode Actor instance to json'''
    if isinstance(actor, Actor):
        return {"name":actor.name,"age":actor.age,"movies":actor.movies}
    else:
        logging.error("Trying to serialize a non-Actor instance")
        
        
def encode_movie(movie):     
    '''encode Movie instance to json'''
    if isinstance(movie, Movie):
        return {"name":movie.name,"year":movie.year,"box_office":movie.gross,"actors":movie.actors}
    else:
        logging.error("Trying to serialize a non-Movie instance")
           
def parse_age(age_str):
    '''convert the str '(age xx)' to age int'''
    age=age_str[-3:-1]
    age=int(age)
    return age

def parse_gross(gross_str):
    '''convert box office string to a float'''
    gross=0
    for x in gross_str:
        if (not str(x).isdigit()):
            gross_str=gross_str[1:]
        else:
            break
    
    new_str=""
    for i in range(0,len(gross_str)):
        char=gross_str[i]
        if (char.isdigit()):
            new_str=new_str+char
        if (char==' '):
            try:
                gross=float(new_str)
            except ValueError:
                return 0
            if (gross_str[i+1]=='m'):
                gross=gross*1000000
            return gross
    return float(new_str)

def read_year(p):
    '''read a paragraph and take the first 4-digit string as the year of a movie'''
    year=""
    for i in range(0,len(p)):
        if (str(p[i]).isdigit()):
            if (i+4<len(p)):
                if (str(p[i+1]).isdigit() and str(p[i+2]).isdigit() and str(p[i+3]).isdigit()):
                    year=p[i]+p[i+1]+p[i+2]+p[i+3]
                    return year
    return ""
    
def parse_actor(soup):
    '''Parser for actor. Read name, age, movies of an actor page.
    @return: actor instance, list of possible movie links'''
    name_tag=soup.find('h1',{"class":"firstHeading"})
    name=name_tag.text
    age_tag=soup.find('span',{"class":"noprint ForceAgeToShow"})
    age=parse_age(age_tag.text)
    film_tag=soup.find('span',text="Filmography")
    if (film_tag==None):
        film_tag=soup.find('span',text="Selected filmography")
        if (film_tag==None):
            film_tag=soup.find('span',text="Partial filmography")
            if (film_tag==None):          
                logging.warn("The actor %s has no filmography.",name)
                return None,[]   
    film_table=soup.find('table',{"class":"wikitable"})
    if (film_table==None):
        logging.warn("%s: Bad page format to parse film list",name)
        return None,[]
    movies = film_table.find_all('a')
    movie_list = list(map(lambda x:x.text,movies))
    potential_movies=[]
    for film in movies:
        try:
            href = film['href']
            potential_movies.append(href)
        except KeyError:
            logging.error("ignoring movies with no href")
    actor = Actor(name,age,0,movie_list)
    return actor,potential_movies

def parse_movie(soup):
    '''Parser for movie. Read name, year, box office, movies of a movie page.
    @return: movie instance, list of possible actor links'''
    name_tag=soup.find('h1',{"class":"firstHeading"})
    name=name_tag.text
    box_office_tag = soup.find('th',text="Box office")
    if (box_office_tag==None):
        logging.warn("The film %s has no box office.",name)
        return None,[]
    boxOffice = box_office_tag.next_sibling.text
    try:
        gross = parse_gross(boxOffice)
    except ValueError:
        logging.error("The movie %s has a bad formatted box office",name)
        return None,[]
    first_p = soup.find_all('p')
    i=0
    year = read_year(first_p)
    while (year=="" and i<min(5,len(first_p)-1)):
        year = read_year(first_p[i].text)
        i=i+1
    try:
        year=int(year)
    except ValueError:
        logging.warn("The movie %s has a bad formatted year",name)
        return None,[]
    cast_tag = soup.find('span',{"id":"Cast"})
    if(cast_tag==None):
        logging.warn("The film %s has no Cast.",name)
        return None,[]
    while(cast_tag.name!='ul'):
        cast_tag=cast_tag.next_element
    cast_list = cast_tag.find_all('a')
    filtered_list = []
    for elem in cast_list:
        try:
            if (elem.text == elem['title']):
                filtered_list.append(elem)
        except KeyError:
            logging.error("ingoring <a> without title")
    cast_list = list(map(lambda x:x.text,filtered_list))
    potential_actors = list(map(lambda x:x['href'],filtered_list))
    movie = Movie(name,year,gross,cast_list)
    return movie,potential_actors

def run(actors,movies,visited_urls,potential_actors,potential_movies,actor_json,movie_json):
    headers = requests.utils.default_headers()
    headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    url = "https://en.wikipedia.org/wiki/The_Shawshank_Redemption"
    bad_urls_file = open("bad_urls.txt","r")
    bad_url=set()
    for line in bad_urls_file:
        bad_url.add(line[:-1])
    while (actors<=250 or movies<=125):
        if (url in visited_urls or url in bad_url):
            if (potential_actors==[] and potential_movies==[]):
                url = "https://en.wikipedia.org/wiki/La_La_Land_(film)"
            if (potential_movies==[]):
                url = potential_actors.pop(random.randint(0,len(potential_actors)-1))
            elif(potential_actors==[]):
                url = potential_movies.pop(random.randint(0,len(potential_movies)-1))
            else:
                if (actors>movies*2):
                    url = potential_movies.pop(random.randint(0,len(potential_movies)-1))
                else:
                    url = potential_actors.pop(random.randint(0,len(potential_actors)-1))
            url="https://en.wikipedia.org"+url
            continue
        logging.info("Current Progress(Actor: %d, Movie: %d)",actors,movies)
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        try:
            page = session.get(url)
        except:
            return actors,movies,visited_urls,potential_actors,potential_movies
        visited_urls.append(url)
        soup = BeautifulSoup(page.content,"lxml")
        age_tag=soup.find('span',{"class":"noprint ForceAgeToShow"})
        if (age_tag==None):
            movie,actors_in_movie=parse_movie(soup)
            if (len(potential_actors)<len(actors_in_movie)):
                potential_actors=actors_in_movie
            if (movie != None):
                movie_json.write(",")
                json.dump(movie, movie_json,default=encode_movie)
                movies=movies+1
            else:
                bad_url.add(url)
        else:
            actor,movies_of_actor=parse_actor(soup)
            if (len(potential_movies)<len(movies_of_actor)):
                potential_movies=movies_of_actor
            if (actor != None):
                actor_json.write(",")
                json.dump(actor, actor_json,default=encode_actor)
                actors=actors+1
            else:
                bad_url.add(url)
        
        #time.sleep(0)
    bad_urls_file = open("bad_urls.txt","w+")
    for url in bad_url:
        try:
            bad_urls_file.write(url+"\n")
        except:
            logging.error("Cannot Write %s", url+"\n")
    return actors,movies,visited_urls,potential_actors,potential_movies

if __name__ == '__main__':
    start_time = time.time()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.info("Scraper Starts...")
    actors=0
    movies=0
    visited_urls=[]
    potential_actors=[]
    potential_movies=[]
    movie_json = open("movie.json","w+")
    actor_json = open("actor.json","w+")
    movie_json.write("[{}")
    actor_json.write("[{}")
    actors,movies,visited_urls,potential_actors,potential_movies=run(actors,movies,visited_urls,potential_actors,potential_movies,actor_json,movie_json)
    while (actors<=250 or movies<=125):
        logging.info("Trying to restart")
        actors,movies,visited_urls,potential_actors,potential_movies=run(actors,movies,visited_urls,potential_actors,potential_movies,actor_json,movie_json)
    run_time=(time.time()-start_time)/60
    movie_json.write("]")
    actor_json.write("]")
    logging.info("Scraper Stops Successfully. Scraped %d Actors, %d Movies. Took %f minutes",actors,movies,run_time)

