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

def encodeActor(actor):
    if isinstance(actor, Actor):
        return {"type":"actor","name":actor.name,"age":actor.age,"movies":actor.movies}
    else:
        logging.error("Trying to serialize a non-Actor instance")
        
        
def encodeMovie(movie):     
    if isinstance(movie, Movie):
        return {"type":"movie","name":movie.name,"year":movie.year,"gross":movie.gross,"actors":movie.actors}
    else:
        logging.error("Trying to serialize a non-Movie instance")
           
def parseAge(ageStr):
    age=ageStr[-3:-1]
    age=int(age)
    return age

def parseGross(grossStr):
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
    year=""
    for i in range(0,len(p)):
        if (str(p[i]).isdigit()):
            if (i+4<len(p)):
                if (str(p[i+1]).isdigit() and str(p[i+2]).isdigit() and str(p[i+3]).isdigit()):
                    year=p[i]+p[i+1]+p[i+2]+p[i+3]
                    return year
    return ""
    
def parseActor(soup):
    nameTag=soup.find('h1',{"class":"firstHeading"})
    name=nameTag.text
    ageTag=soup.find('span',{"class":"noprint ForceAgeToShow"})
    age=parseAge(ageTag.text)
    FilmTag=soup.find('span',{"id":"Filmography"})
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
            logging.info("ignoring movies with no href")
    actor = Actor(name,age,movieList)
    return actor,potentialMovies

def parseMovie(soup):
    nameTag=soup.find('h1',{"class":"firstHeading"})
    name=nameTag.text
    boxOfficeTag = soup.find('th',text="Box office")
    if (boxOfficeTag==None):
        logging.warn("The film %s has no box office.",name)
        return None,[]
    boxOffice = boxOfficeTag.next_sibling.text
    gross = parseGross(boxOffice)
    firstP = soup.p
    year = readYear(firstP.text)
    if (year==""):
        firstP = soup.find_all('p')
        year = readYear(firstP[1].text)
        if (year==""):
            logging.warn("The movie %s has a bad formatted year",name)
            return None,[]
    try:
        year=int(year)
    except ValueError:
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
            logging.info("ingoring <a> without title")
    castList = list(map(lambda x:x.text,filteredList))
    potentialActors = list(map(lambda x:x['href'],filteredList))
    movie = Movie(name,year,gross,castList)
    return movie,potentialActors

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.info("Scraper Starts...")
actors=[]
movies=[]
visitedUrls=[]
potentialActors=[]
potentialMovies=[]
movieJson = open("movie.json","w+")
actorJson = open("actor.json","w+")
movieJson.write("[{}")
actorJson.write("[{}")
headers = requests.utils.default_headers()
headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
url = "https://en.wikipedia.org/wiki/Bloodworth"

while (len(actors)<=250 or len(movies)<=125):
    if (url in visitedUrls):
        if (potentialMovies==[]):
            url = potentialActors.pop(random.randint(0,len(potentialActors)-1))
        elif(potentialActors==[]):
            url = potentialMovies.pop(random.randint(0,len(potentialMovies)-1))
        else:
            if (len(actors)>len(movies)*2):
                url = potentialMovies.pop(random.randint(0,len(potentialMovies)-1))
            else:
                url = potentialActors.pop(random.randint(0,len(potentialActors)-1))
        url="https://en.wikipedia.org"+url
        continue
    visitedUrls.append(url)
    logging.info("Current Progress(Actor: %d, Movie: %d)  Parsing: %s",len(actors),len(movies),url)
    page = requests.get(url,headers=headers)
    soup = BeautifulSoup(page.content,"lxml")
    ageTag=soup.find('span',{"class":"noprint ForceAgeToShow"})
    if (ageTag==None):
        movie,actorsInMovie=parseMovie(soup)
        if (len(potentialActors)<len(actorsInMovie)):
            potentialActors=actorsInMovie
        if ((movie != None) and (movie.name not in movies)):
            movieJson.write(",")
            json.dump(movie, movieJson,default=encodeMovie)
            movies.append(movie.name)
    else:
        actor,moviesOfActor=parseActor(soup)
        if (len(potentialMovies)<len(moviesOfActor)):
            potentialMovies=moviesOfActor
        if ((actor != None) and(actor.name not in actors)):
            actorJson.write(",")
            json.dump(actor, actorJson,default=encodeActor)
            actors.append(actor.name)
    if (potentialMovies==[]):
        url = potentialActors.pop(random.randint(0,len(potentialActors)-1))
    elif(potentialActors==[]):
        url = potentialMovies.pop(random.randint(0,len(potentialMovies)-1))
    else:
        if (len(actors)>len(movies)*2):
            url = potentialMovies.pop(random.randint(0,len(potentialMovies)-1))
        else:
            url = potentialActors.pop(random.randint(0,len(potentialActors)-1))
    url="https://en.wikipedia.org"+url
    
    time.sleep(random.uniform(0.5,0.6))

movieJson.write("]")
actorJson.write("]")
logging.info("Scraper Stops Successfully. Scraped %d Actors, %d Movies",len(actors),len(movies))
