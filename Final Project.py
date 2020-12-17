from os import readlink
import sqlite3
import  requests
from bs4 import BeautifulSoup
import time
import json
import re
import secrets
import plotly
import plotly.graph_objects as go
from flask import Flask, render_template,request


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
    
    Return: a list of tuple, which contains the information of all 250 IMBD movies
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



def make_request_api(url):
    '''Make a request to the Web API using the baseurl and params
    and return a dictionary
    -----------------------
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
        try:
            movie_poster_id=result['Poster']
        except:
            movie_poster_id='none'    
        
        omdb_row_tuple=(movie_imdbID,movie_name,movie_rated,movie_runtime,movie_Director,movie_imdb_rating,movie_rotten_tomatoes_rating,movie_Metascore,movie_prodcution,movie_genre
                        ,movie_country,movie_language,movie_poster_id)
        omdb_row_tuple_list.append(omdb_row_tuple)
    #I changed here Dec 13
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
        Movie_Language text,
        Movie_Poster text)''')
    #Insert data in the database
    c.executemany('INSERT INTO OMDB VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',omdb_list_of_tuple)
    conn.commit()#Save changes
    conn.close
    return None

#from here, start the plotly function


def make_language_bar_plot():
    
    ''' link to database and based on language making bar plot

    Parameters
    ----------
    None

    Returns
    -------
    div: The bar plot of movies sorted by language, which can be used in html templates
    '''
    connection= sqlite3.connect("IMDB_OMDB.sqlite")
    xvals=['English','French','Japanese','German','Others']#this should be language
    cursor=connection.cursor()
    q_English='''
    SELECT COUNT(Movie_Language)
    FROM OMDB
    WHERE Movie_language like ('%English%')'''
    q_French='''
    SELECT COUNT(Movie_language)
    FROM OMDB
    Where Movie_language like ('%French%')
    '''
    q_Japanese='''
    SELECT COUNT(Movie_language)
    FROM OMDB
    Where Movie_language like ('%Japanese%')
    '''
    q_German='''
    SELECT COUNT(Movie_language)
    FROM OMDB
    Where Movie_language like ('%German%')
    '''
    q_Others='''
    SELECT COUNT(Movie_Language)
    FROM OMDB
    WHERE Movie_Language not like ('%English%') and Movie_Language not like ('%Japanese%') and Movie_Language not like ('%French%') and Movie_Language not like ('%German%')
    '''
    cursor.execute(q_English)
    number_EN=cursor.fetchone()[0]
   
    cursor.execute(q_Japanese)
    number_JN=cursor.fetchone()[0]
    
    cursor.execute(q_French)
    number_FR=cursor.fetchone()[0]
    
    cursor.execute(q_German)
    number_GM=cursor.fetchone()[0]
    
    cursor.execute(q_Others)
    number_OT=cursor.fetchone()[0]
    
    yvals=[number_EN,number_FR,number_JN,number_GM,number_OT]#this should be the number of movies
    #print(number_EN,number_FR,number_GM,number_JN,number_OT)
    bar_data=go.Bar(x=xvals,y=yvals)
    basic_layout=go.Layout(title='The number of movies sorted by languages')
    fig=go.Figure(data=bar_data, layout=basic_layout)
    #fig.write_html("bar.html",auto_open=True)
    div=fig.to_html(full_html=False)
    return div


def make_genre_bar_plot():
    ''' link to database and based on genre making bar plot

    Parameters
    ----------
    None

    Returns
    -------
    div: The bar plot of movies sorted by genre, which can be used in html templates
    '''
    connection= sqlite3.connect("IMDB_OMDB.sqlite")
    cursor=connection.cursor()
    
    q_drama='''
    SELECT COUNT(Movie_Genre)
    FROM OMDB
    WHERE Movie_Genre like('%Drama%')
    '''
    
    q_war='''
    SELECT COUNT(Movie_Genre)
    FROM OMDB
    WHERE Movie_Genre like('%War%')
    '''
    
    q_comedy='''
    SELECT COUNT(Movie_Genre)
    FROM OMDB
    WHERE Movie_Genre like('%Comedy%')
    '''
    
    q_action='''
    SELECT COUNT(Movie_Genre)
    FROM OMDB
    WHERE Movie_Genre like('%Action%')
    '''
    
    q_thriller='''
    SELECT COUNT(Movie_Genre)
    FROM OMDB
    WHERE Movie_Genre like('%THRILLER%')
    '''
    
    q_others='''
    SELECT COUNT(Movie_Genre)
    FROM OMDB
    WHERE Movie_Genre not like('%THRILLER%') and Movie_Genre not like('%Drama%') and Movie_Genre not like('%WAR%') and Movie_Genre not like('%Action%') and Movie_Genre not like('%Comedy%')    
    '''
    
    cursor.execute(q_drama)
    number_dr=cursor.fetchone()[0]
    
    cursor.execute(q_action)
    number_ac=cursor.fetchone()[0]
    
    cursor.execute(q_comedy)
    number_co=cursor.fetchone()[0]
    
    cursor.execute(q_thriller)
    number_th=cursor.fetchone()[0]
    
    cursor.execute(q_war)
    number_wa=cursor.fetchone()[0]
    
    cursor.execute(q_others)
    number_ot=cursor.fetchone()[0]
    
    xvals=["Drama","Action","Comedy",'Thriller','War','Others']
    yvals=[number_dr,number_ac,number_co,number_th,number_wa,number_ot]  
    bar_data=go.Bar(x=xvals,y=yvals)
    basic_layout=go.Layout(title='The number of movies sorted by genre')
    fig=go.Figure(data=bar_data, layout=basic_layout)
    div=fig.to_html(full_html=False)
    #fig.write_html("bar.html",auto_open=True)
    
    return div

def make_country_bar_plot():
    ''' link to database and based on country making bar plot

    Parameters
    ----------
    None

    Returns
    -------
    div: The bar plot of movies sorted by country, which can be used in html templates
    '''
    connection= sqlite3.connect("IMDB_OMDB.sqlite")
    cursor=connection.cursor()
    
    q_usa='''
    SELECT COUNT(Movie_Country)
    FROM OMDB
    WHERE Movie_Country like('%USA%')
    '''
    
    q_uk='''
    SELECT COUNT(Movie_Country)
    FROM OMDB
    WHERE Movie_Country like('%UK%')
    '''
    
    q_jp='''
    SELECT COUNT(Movie_Country)
    FROM OMDB
    WHERE Movie_Country like('%Japan%')
    '''
    
    q_fr='''
    SELECT COUNT(Movie_Country)
    FROM OMDB
    WHERE Movie_Country like('%France%')
    '''
    
    q_gm='''
    SELECT COUNT(Movie_Country)
    FROM OMDB
    WHERE Movie_Country like('%German%')
    '''
    
    q_ot='''
    SELECT COUNT(Movie_Country)
    FROM OMDB
    WHERE Movie_Country not like('%USA%') and Movie_Country not like('%UK%') and Movie_Country not like('%Japan%') and Movie_Country not like('%France%') and Movie_Country not like('%German%')    
    '''
    cursor.execute(q_usa)
    number_usa=cursor.fetchone()[0]
    
    
    cursor.execute(q_uk)
    number_uk=cursor.fetchone()[0]
    
    cursor.execute(q_jp)
    number_jp=cursor.fetchone()[0]
    
    cursor.execute(q_fr)
    number_fr=cursor.fetchone()[0]
    
    cursor.execute(q_gm)
    number_gm=cursor.fetchone()[0]
    
    cursor.execute(q_ot)
    number_ot=cursor.fetchone()[0]
    
    xvals=["USA","UK","Japan",'France','German','Others']
    yvals=[number_usa,number_uk,number_jp,number_fr,number_gm,number_ot]  
    bar_data=go.Bar(x=xvals,y=yvals)
    basic_layout=go.Layout(title='The number of movies sorted by Country')
    fig=go.Figure(data=bar_data, layout=basic_layout)
    div=fig.to_html(full_html=False)
    #fig.write_html("bar.html",auto_open=True)
    
    return div
  
def make_rated_bar_plot():
    ''' link to database and based on rating making bar plot

    Parameters
    ----------
    None

    Returns
    -------
    div: The bar plot of movies sorted by rating, which can be used in html templates
    '''
    
    
    connection= sqlite3.connect("IMDB_OMDB.sqlite")
    cursor=connection.cursor()
    
    q_r='''
    SELECT COUNT(MovieRated)
    FROM OMDB
    WHERE MovieRated =('R')
    '''
    
    q_pg='''
    SELECT COUNT(MovieRated)
    FROM OMDB
    WHERE MovieRated =('PG')
    '''
    
    q_pg13='''
    SELECT COUNT(MovieRated)
    FROM OMDB
    WHERE MovieRated =('PG-13')
    '''
    
    q_g= '''
    SELECT COUNT(MovieRated)
    FROM OMDB
    WHERE MovieRated =('G')
    '''
    
    q_ot=''' 
    SELECT COUNT(MovieRated)
    FROM OMDB
    WHERE MovieRated <>('PG-13') and MovieRated<>('R') and MovieRated<>('PG')and MovieRated<>('G')
    '''
    
    cursor.execute(q_pg)
    number_pg=cursor.fetchone()[0]
    
    cursor.execute(q_pg13)
    number_pg13=cursor.fetchone()[0]
    
    cursor.execute(q_r)
    number_r=cursor.fetchone()[0]
    
    cursor.execute(q_g)
    number_g=cursor.fetchone()[0]
    
    cursor.execute(q_ot)
    number_ot=cursor.fetchone()[0]
    
    xvals=["R","PG","PG-13","G","Others"]
    yvals=[number_r,number_pg,number_pg13,number_g,number_ot]
    
    bar_data=go.Bar(x=xvals,y=yvals)
    basic_layout=go.Layout(title='The number of movies sorted by Rating')
    fig=go.Figure(data=bar_data, layout=basic_layout)
    div=fig.to_html(full_html=False)
    #div=fig.write_html("bar.html",auto_open=True)
    
    return div
    
    
def make_user_interactive_search(input_id):
    '''
    using input number to search the database, and generate a string and a url to be plugged in html templates.
    
    parameter:
    -----------------
    input_id: string, represent the number of rank of the IMDB 250 list
    ----
    return:
    Movie_intro: a string contain movies' information
    Movie_poster_url: string, the url of poster
    
    
    '''
    connection= sqlite3.connect("IMDB_OMDB.sqlite")
    cursor=connection.cursor()
    
    q_info='''
    SELECT IMDB.MovieName, IMDB.MovieReleaseYear,OMDB.MovieRated,OMDB.MovieDirector,OMDB.Movie_IMDB_Rating,OMDB.Movie_Rotten_Tomatoes_Rating,OMDB.Movie_Metascore,OMDB.Movie_Poster
    FROM OMDB JOIN IMDB ON IMDB.MovieID=OMDB.Movie_ID
    WHERE IMDB.Rank={input_id1} 
    '''.format(input_id1=input_id)
    
    cursor.execute(q_info)
    Movie_info=cursor.fetchone()
    
    Movie_name=Movie_info[0]
    Movie_year=Movie_info[1]
    Movie_rating=Movie_info[2]
    Movie_Director=Movie_info[3]
    Movie_IMDB_Rating=Movie_info[4]
    Movie_rotten_tomato=Movie_info[5]
    Movie_metascore=Movie_info[6]
    Movie_poster_url=Movie_info[7]
    Movie_intro=f'<{Movie_name}> is a {Movie_year} year, {Movie_rating} rating movie. The movie is directed by {Movie_Director}. The movie got {Movie_IMDB_Rating} IMDB Rating, {Movie_rotten_tomato} Rotten Tomatoes Rating, and {Movie_metascore} metacritic rating.'
    #print(Movie_intro) # check correct
    return [Movie_intro,Movie_poster_url]
    
    
#from here, start the app function
app=Flask(__name__)

@app.route('/')
def index():
    #print(render_template('opening.html'))
    return render_template('opening.html')
    

@app.route('/handle_form', methods=['GET','POST'])
def intro():
    input_rank=request.form["rank"]
    intro=make_user_interactive_search(input_rank)[0]
    img=make_user_interactive_search(input_rank)[1]
    print("this is img!!!",img)
    return render_template('results.html',Intro=intro,img1=img)
    
@app.route('/language')
def language():
    lang_plot_div=make_language_bar_plot()
    return render_template("display.html",plot_div=lang_plot_div)

@app.route('/genre')
def genre():
    genre_plot_div=make_genre_bar_plot()
    return render_template("display.html",plot_div=genre_plot_div)

@app.route('/country')
def country():
    country_plot_div=make_country_bar_plot()
    return render_template("display.html",plot_div=country_plot_div)
    
@app.route('/rating')
def rating():
    rating_plot_div=make_rated_bar_plot()
    return render_template('display.html',plot_div=rating_plot_div)
    

if __name__ == "__main__":
    IMDB_tuple_list=get_imdb_top250()
    omdb_list_of_tuple=make_request_with_cache_omdb_api(id_ls)
    create_imdb_database(IMDB_tuple_list)
    create_omdb_database(omdb_list_of_tuple)
    
    #If want to create database, use above 4 functions
    
    app.run(debug=True)
