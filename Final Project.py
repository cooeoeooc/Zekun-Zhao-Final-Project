import sqlite3
import  requests
from bs4 import BeautifulSoup
import time
import random
import json
import re
import secrets


class Movie:
    def __init__(self,url,rank,name,year,id):
        #self.rating=rating
        self.url=url
        self.rank=rank
        self.name=name
        self.year=year
        self.id=id
def load_cache(CACHE_FILENAME):
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict,CACHE_FILENAME):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()



def make_url_request_using_cache(url, cache):
    if url in cache: # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url)
        cache[url] = response.text # notice that we save response.text to our cache dictionary. We turn it into a BeautifulSoup object later, since BeautifulSoup objects are nor json parsable. 
        save_cache(cache,CACHE_FILENAME)
        return cache[url] # in both cases, we return cache[url]
'''
   Check the cache for a saved result for this url. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    
    Parameters
    ----------
    url: string
        The URL for the website
        
    cache: a cache file
    
    
    Returns
    -------
    cache[url]
        the results of the query as a dictionary loaded from cache
        JSON
'''
CACHE_FILENAME = "movie_cache.json"
cache_file=load_cache(CACHE_FILENAME)


def make_url_request_using_cache_api(url, cache):
    '''
   Check the cache for a saved result for this url. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    
    Parameters
    ----------
    url: string
        The URL for the website
        
    cache: a cache file
    
    
    Returns
    -------
    cache[url]
        the results of the query as a dictionary loaded from cache
        JSON
'''
    if url in cache: # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url)
        cache[url] = response # notice that we save response.text to our cache dictionary. We turn it into a BeautifulSoup object later, since BeautifulSoup objects are nor json parsable. 
        save_cache(cache,CACHE_FILENAME)
        return cache[url] # in both cases, we return cache[url]
    




def get_imdb_top250():
    '''
    generate a list of tuple, the tuple formed by url, rank, name, year, id of Top 250 IMBD movies.
    
    parameter: None
    
    '''
    global id_ls
    id_ls=[]
    movie_instance_ls=[]
    movie_list_of_tuple=[]
    base_url='imdb.com'
    top_url='https://www.imdb.com/chart/top'
    url_text=make_url_request_using_cache(top_url,cache_file)
    soup=BeautifulSoup(url_text,'html.parser')
    #print(soup) soup is good
    movie_parent=soup.find("div",class_='seen-collection')
    #print(movie_parent) this one is good
    movie_ls=movie_parent.find_all('td',class_='titleColumn')
    #print(movie_ls) #this one is  good
    for movie in movie_ls:
        movie_info=movie.get_text().replace(".",'').split('\n')
        movie_rank=movie_info[1].lstrip()
        movie_name=movie_info[2].lstrip()
        movie_year=movie_info[3].strip('(').strip(')')
        movie_id_tag=movie.find('a')['href']
        movie_id=movie_id_tag.split('/')[2]
        id_ls.append(movie_id)
        movie_url=base_url+movie_id_tag
        movie_instance=Movie(movie_url,movie_rank,movie_name,movie_year,movie_id)
        movie_instance_ls.append(movie_instance)
    #this part editor later
    for movie in movie_instance_ls:
        #print(movie.url)
        movie_tuple=(movie.rank,movie.name,movie.year,movie.url,movie.id)
        #print(movie_tuple)
        movie_list_of_tuple.append(movie_tuple)
    #print(movie_list_of_tuple)# this one is good
    return movie_list_of_tuple

api_key=secrets.API_KEY

def save_imdb_sqlite(movie_list_of_tuple):
    '''
    save list of tuple into sql database
    ------
    parameter:
    list of tuple, containing infomation from the Internet
    
    return: a database
    '''
    
    
    conn=sqlite3.connect('imdb.db')
    c=conn.cursor()
    
    return None


def make_request_api(url):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    response=requests.get(url)
    #print(response)# good response checked
    return response.json()


def make_request_with_cache_omdb_api(imdb_id_list):
    

    '''Check the cache for a saved result for this search_url. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    
    Parameters
    ----------
    imdb_id_list:list of string, which can be used to form search url

    
    
    Returns
    -------
    list of tuple:
    a list of tuple, which contains information of IMDB TOP 250 movies.
            '''
    omdb_row_tuple_list=[]
    cache_file=load_cache(CACHE_FILENAME)
    base_url='http://www.omdbapi.com/?'
    for imdb_id in imdb_id_list:
        search_url=base_url+"i="+imdb_id+"&"+"apikey="+api_key
        #print(search_url)
 
        if imdb_id in cache_file:
            print('Using cache')
            #print(cache_file[imdb_id]) #prove correct
            #print(type(cache_file[imdb_id]))
            result=cache_file[imdb_id]
        else:
            print("Fetching")
            new_request=make_request_api(search_url)
            cache_file[imdb_id]=new_request
            save_cache(cache_file,CACHE_FILENAME)
            #print(type(cache_file[imdb_id])) #prove correct
            result=cache_file[imdb_id]
        try:    
            movie_name=result['Title']
        except:
            movie_name="none"
        try:
            movie_runtime=result['Runtime']
        except:
            movie_runtime='none'
        try:
            movie_Director=result['Director']
        except:
            movie_Director="none"
        try:
            movie_imdb_rating=result['imdbRating']
        except:
            movie_imdb_rating='none'
        try:
            movie_rotten_tomatoes_rating=result['Ratings'][1]['Value']
        except:
            movie_rotten_tomatoes_rating='none'
        try:
            movie_imdbID=result['imdbID']
        except:
            movie_imdbID='none'
        try:
            movie_prodcution=result['Production']
        except:
            movie_prodcution='none'
        try:
            movie_rated=result['Rated']
        except:
            movie_rated='none'
        try:
            movie_Metascore=result['Metascore']
        except:
            movie_Metascore='none'
        try:
            movie_genre=result['Genre']
        except:
            movie_genre='none'
        try:
            movie_country=result['Country']
        except:
            movie_country='none'
        try:
            movie_language=result['Language']
        except:
            movie_language='none'
            
        omdb_row_tuple=(movie_imdbID,movie_name,movie_rated,movie_runtime,movie_Director,movie_imdb_rating,movie_rotten_tomatoes_rating,movie_Metascore,movie_prodcution,movie_genre
                        ,movie_country,movie_language)
        omdb_row_tuple_list.append(omdb_row_tuple)
        
    #print(omdb_row_tuple_list)
    return omdb_row_tuple_list


def create_imdb_database(imdb_list_of_tuple):
    '''
    generate imdb database using information from IMDB
    -----
    parameter: list of tuple, which contains movies' information scraped from IMDB
    ------
    return:
    None
    '''
    conn=sqlite3.connect('IMDB_OMDB.sqlite')
    c=conn.cursor()
    c.execute('''DROP TABLE IF EXISTS "IMDB"''')
    #creat table
    c.execute('''CREATE TABLE IF NOT EXISTS "IMDB"(
        [Rank] integer PRIMARY KEY AUTOINCREMENT UNIQUE,
        MovieName text, 
        MovieReleaseYear text,
        MovieUrl text,
        MovieID text)''')
    #Insert data in the database
    c.executemany('INSERT INTO IMDB VALUES(?,?,?,?,?)',imdb_list_of_tuple)
    conn.commit()#Save changes
    conn.close
    return None
        
def create_omdb_database(omdb_list_of_tuple):
    '''
    generate imdb database using information from OMDB
    -----
    parameter: list of tuple, which contains movies' information get from OMDB API
    ------
    return:
    None
    '''
    conn=sqlite3.connect('IMDB_OMDB.sqlite')
    c=conn.cursor()
    c.execute('''DROP TABLE IF EXISTS "OMDB"''')
    #creat table
    c.execute('''CREATE TABLE IF NOT EXISTS "OMDB"(
        Movie_ID text PRIMARY KEY,
        MovieName text, 
        MovieRated text,
        MovieRuntime text,
        MovieDirector text,
        Movie_IMDB_Rating text,
        Movie_Rotten_Tomatoes_Rating text,
        Movie_Metascore text,
        Movie_prodcution text,
        Movie_Genre text,
        Movie_Country text,
        Movie_Language text)''')
    #Insert data in the database
    c.executemany('INSERT INTO OMDB VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',omdb_list_of_tuple)
    conn.commit()#Save changes
    conn.close
    return None
    

    
        
        
        
if __name__ == "__main__":
    IMDB_tuple_list=get_imdb_top250()
    omdb_list_of_tuple=make_request_with_cache_omdb_api(id_ls)
    create_imdb_database(IMDB_tuple_list)
    create_omdb_database(omdb_list_of_tuple)    