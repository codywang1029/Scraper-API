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
from Graph.Actor import Actor
from Graph.Movie import Movie
from itertools import cycle
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry



def encodeActor(actor):
    '''encode Actor instance to json'''
    if isinstance(actor, Actor):
        return {"name":actor.name,"age":actor.age,"movies":actor.movies}
    else:
        logging.error("Trying to serialize a non-Actor instance")
        
        
def encodeMovie(movie):     
    '''encode Movie instance to json'''
    if isinstance(movie, Movie):
        return {"name":movie.name,"year":movie.year,"gross":movie.gross,"actors":movie.actors}
    else:
        logging.error("Trying to serialize a non-Movie instance")
           
def parseAge(ageStr):
    '''convert the str '(age xx)' to age int'''
    age=ageStr[-3:-1]
    age=int(age)
    return age

def parseGross(grossStr):
    '''convert box office string to a float'''
    gross=0
    for x in grossStr:
        if (not str(x).isdigit()):
            grossStr=grossStr[1:]
        else:
            break
    
    newStr=""
    for i in range(0,len(grossStr)):
        char=grossStr[i]
        if (char.isdigit()):
            newStr=newStr+char
        if (char==' '):
            try:
                gross=float(newStr)
            except ValueError:
                return 0
            if (grossStr[i+1]=='m'):
                gross=gross*1000000
            return gross
    return float(newStr)

def readYear(p):
    '''read a paragraph and take the first 4-digit string as the year of a movie'''
    year=""
    for i in range(0,len(p)):
        if (str(p[i]).isdigit()):
            if (i+4<len(p)):
                if (str(p[i+1]).isdigit() and str(p[i+2]).isdigit() and str(p[i+3]).isdigit()):
                    year=p[i]+p[i+1]+p[i+2]+p[i+3]
                    return year
    return ""
    
def parseActor(soup):
    '''Parser for actor. Read name, age, movies of an actor page.
    @return: actor instance, list of possible movie links'''
    nameTag=soup.find('h1',{"class":"firstHeading"})
    name=nameTag.text
    ageTag=soup.find('span',{"class":"noprint ForceAgeToShow"})
    age=parseAge(ageTag.text)
    FilmTag=soup.find('span',text="Filmography")
    if (FilmTag==None):
        FilmTag=soup.find('span',text="Selected filmography")
        if (FilmTag==None):
            FilmTag=soup.find('span',text="Partial filmography")
            if (FilmTag==None):          
                logging.warn("The actor %s has no filmography.",name)
                return None,[]   
    filmTable=soup.find('table',{"class":"wikitable"})
    if (filmTable==None):
        logging.warn("%s: Bad page format to parse film list",name)
        return None,[]
    movies = filmTable.find_all('a')
    movieList = list(map(lambda x:x.text,movies))
    potentialMovies=[]
    for film in movies:
        try:
            href = film['href']
            potentialMovies.append(href)
        except KeyError:
            logging.error("ignoring movies with no href")
    actor = Actor(name,age,movieList)
    return actor,potentialMovies

def parseMovie(soup):
    '''Parser for movie. Read name, year, box office, movies of a movie page.
    @return: movie instance, list of possible actor links'''
    nameTag=soup.find('h1',{"class":"firstHeading"})
    name=nameTag.text
    boxOfficeTag = soup.find('th',text="Box office")
    if (boxOfficeTag==None):
        logging.warn("The film %s has no box office.",name)
        return None,[]
    boxOffice = boxOfficeTag.next_sibling.text
    try:
        gross = parseGross(boxOffice)
    except ValueError:
        logging.error("The movie %s has a bad formatted box office",name)
        return None,[]
    firstP = soup.find_all('p')
    i=0
    year = readYear(firstP)
    while (year=="" and i<min(5,len(firstP)-1)):
        year = readYear(firstP[i].text)
        i=i+1
    try:
        year=int(year)
    except ValueError:
        logging.warn("The movie %s has a bad formatted year",name)
        return None,[]
    castTag = soup.find('span',{"id":"Cast"})
    if(castTag==None):
        logging.warn("The film %s has no Cast.",name)
        return None,[]
    while(castTag.name!='ul'):
        castTag=castTag.next_element
    castList = castTag.find_all('a')
    filteredList = []
    for elem in castList:
        try:
            if (elem.text == elem['title']):
                filteredList.append(elem)
        except KeyError:
            logging.error("ingoring <a> without title")
    castList = list(map(lambda x:x.text,filteredList))
    potentialActors = list(map(lambda x:x['href'],filteredList))
    movie = Movie(name,year,gross,castList)
    return movie,potentialActors

def run(actors,movies,visitedUrls,potentialActors,potentialMovies,actorJson,movieJson):
    headers = requests.utils.default_headers()
    headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    url = "https://en.wikipedia.org/wiki/The_Shawshank_Redemption"
    badUrlsFile = open("badUrls.txt","r")
    badUrl=set()
    for line in badUrlsFile:
        badUrl.add(line[:-1])
    while (actors<=250 or movies<=125):
        if (url in visitedUrls or url in badUrl):
            if (potentialActors==[] and potentialMovies==[]):
                url = "https://en.wikipedia.org/wiki/La_La_Land_(film)"
            if (potentialMovies==[]):
                url = potentialActors.pop(random.randint(0,len(potentialActors)-1))
            elif(potentialActors==[]):
                url = potentialMovies.pop(random.randint(0,len(potentialMovies)-1))
            else:
                if (actors>movies*2):
                    url = potentialMovies.pop(random.randint(0,len(potentialMovies)-1))
                else:
                    url = potentialActors.pop(random.randint(0,len(potentialActors)-1))
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
            return actors,movies,visitedUrls,potentialActors,potentialMovies
        visitedUrls.append(url)
        soup = BeautifulSoup(page.content,"lxml")
        ageTag=soup.find('span',{"class":"noprint ForceAgeToShow"})
        if (ageTag==None):
            movie,actorsInMovie=parseMovie(soup)
            if (len(potentialActors)<len(actorsInMovie)):
                potentialActors=actorsInMovie
            if (movie != None):
                movieJson.write(",")
                json.dump(movie, movieJson,default=encodeMovie)
                movies=movies+1
            else:
                badUrl.add(url)
        else:
            actor,moviesOfActor=parseActor(soup)
            if (len(potentialMovies)<len(moviesOfActor)):
                potentialMovies=moviesOfActor
            if (actor != None):
                actorJson.write(",")
                json.dump(actor, actorJson,default=encodeActor)
                actors=actors+1
            else:
                badUrl.add(url)
        
        time.sleep(0)
    badUrlsFile = open("badUrls.txt","w+")
    for url in badUrl:
        try:
            badUrlsFile.write(url+"\n")
        except:
            logging.error("Cannot Write %s", url+"\n")
    return actors,movies,visitedUrls,potentialActors,potentialMovies

if __name__ == '__main__':
    startTime = time.time()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.info("Scraper Starts...")
    actors=0
    movies=0
    visitedUrls=[]
    potentialActors=[]
    potentialMovies=[]
    movieJson = open("movie.json","w+")
    actorJson = open("actor.json","w+")
    movieJson.write("[{}")
    actorJson.write("[{}")
    actors,movies,visitedUrls,potentialActors,potentialMovies=run(actors,movies,visitedUrls,potentialActors,potentialMovies,actorJson,movieJson)
    while (actors<=250 or movies<=125):
        logging.info("Trying to restart")
        actors,movies,visitedUrls,potentialActors,potentialMovies=run(actors,movies,visitedUrls,potentialActors,potentialMovies,actorJson,movieJson)
    runTime=(time.time()-startTime)/60
    movieJson.write("]")
    actorJson.write("]")
    logging.info("Scraper Stops Successfully. Scraped %d Actors, %d Movies. Took %f minutes",actors,movies,runTime)

