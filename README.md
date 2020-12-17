# Zekun-Zhao-Final-Project
The main project is “Final Project.” I also upload the “Secrets”, which contains my API key for this program. 
There are several important functions in the file, and I also add doc string to every one of them.

make_url_request_using_cache: Check the cache for a saved result for this url. If the result is found, return it. Otherwise send a new request, save it, then return it.

get_imdb_top250: generate a list of tuple, the tuple formed by url, rank, name, year, id of Top 250 IMBD movies.

make_request_api: Make a request to the Web API using the baseurl and params and return a dictionary

create_imdb_database: generate imdb database using information from IMDB(list of tuple)

create_omdb_database: generate imdb database using information from OMDB(list of tuple)

make_language_bar_plot, make_genre_bar_plot, make_country_bar_plot, make_rated_bar_plot: link to database and based on different criteria making bar plots

To run this program, users need to import those packages:
sqlite3,
requests,
BeautifulSoup,
Secrets,
Plotly,
Flask,
Os
Moreover, users also need to use the templates file to run the program, and save the templates file in the same directory with "Final Project" and "Secrets".

After run the program and open the link, users can click on four links to view graphs about the movies’ data, or input a number to search movie’s information.

