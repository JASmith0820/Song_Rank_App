# -*- coding: utf-8 -*-
"""
DNSC 6203 Group Project - Python code for Web Scraping
Jessica Smith, Yahui Zhou, and Andrew Nichols
Created on Wed Dec  2 13:43:20 2015

The code completes the following tasks:
    Part 1: Scrapes the Billboard and Shazam websites, stores data in 
        a MySQL database, and creates csv files
        
    Part 2: Takes csv files that were generated in earlier weeks and stores
        them in a cumulative MySQL database
        
    Part 3: Performs queries on the cumulative MySQL database and stores
        the results in csv files for analysis in R
        
Note that there are 8 csv files contained in the historic_files folder.
(included with our project submission). Please make sure this folder
and its contents are accessible by your current working directory.
"""

'''
PART 1: Web scraping

The first section of code scrapes the web to retrieve four sources
of music data:
    Billboard Hot 100
    Billboard Trending 140 (most shared on Twitter in last 24 hours)
    Shazam Top 100
    Shazam Hit Predictor
    
The lists are stored in a local mysql database called music. 
The database is dropped and recreated each time the code runs. 
A csv file is generated for each list and stored in the working directory. 
'''

#-------------SET THE DATE PULLED-------------------
#Before doing anything else, set these two variables
#date_pulled goes into the MySQL databases
#date_csv_format goes onto the end of the csv files
#Both should reflect today's date
date_pulled = '12/02/2015'
date_csv_format = '20151202'


#-------------IMPORT REQUIRED LIBRARIES--------------
import pandas as pd
from bs4 import BeautifulSoup
import urllib2
import MySQLdb as SQL
import csv
import numpy as np

#-----------MAKE MYSQL DATABASE-------------------------
#This will have a table for each data source we use
conn = SQL.connect(host='localhost', user='root', passwd='root')
cursor = conn.cursor()

sql = 'DROP DATABASE IF EXISTS music;'
cursor.execute(sql)
sql = ' CREATE DATABASE music; '
cursor.execute(sql)
cursor.close()

#----------DEFINE ALL FUNCTIONS--------------------
def initialize_lists():
    #Ensure that the lists for songs, artists, and
    #rank are all blank
    songs = []
    artists = []
    rank = []
    
    return songs, artists, rank
    
def initialize_soup(url):
    #Takes a url as input
    #Returns the scraped URL as a BeautifulSoup object
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)
    
    return soup
    
def initialize_song_arrays(songs):
    #Takes a list of songs and returns two numpy arrays:
    #song_array: numpy array starting at zero
    #rank: numpy array starting at 1
    #So if you have 20 songs, song_array will run from 0 to 19 and
    #rank will run from 1 to 20
    num_songs = len(songs)
    song_array = np.arange(0, num_songs)
    rank = np.arange(1, num_songs+1)
    
    return song_array, rank
    
def initialize_db_connection():
    # Set up a connection to the new music database
    # IF YOU WANT TO CHANGE THE DB NAME, ONLY NEED TO CHANGE IT HERE
    LPdb = SQL.connect(host='localhost', user='root', passwd='root', db='music')
    
    #set autocommit to 1 so data can be appended easily
    cursor = LPdb.cursor()
    sql = ' SET AUTOCOMMIT = 1;'
    cursor.execute(sql)
    return cursor
    
def create_table(tablename, cursor):
    #Takes a string as an input, then creates a table with that name
    #You must also provide a cursor
    #Does not return anything
    #All tables have the same 4 fields
    sql = '''
     CREATE TABLE %s (
     date_pulled CHAR(20),
     rank CHAR(20),
     song CHAR(255),
     artist CHAR(255));
     ''' % tablename
    cursor.execute(sql)
    
def insert_to_table(dictionary, tablename, cursor):
    #Takes a dictionary, a string tablename, and a cursor as input
    #Pulls the data from the dictionary and inserts it into the 
    #table based on the tablename you provide   
    
    for i in np.arange(0,len(dictionary)):
        sql='''
        INSERT INTO %s (date_pulled, rank, song, artist)
        VALUES ("%s", "%s","%s", "%s");''' % (tablename, date_pulled, dictionary[i]['rank'], \
        dictionary[i]['song'], dictionary[i]['artist'])
        cursor.execute(sql)  
        
def view_sql_table(tablename, cursor):
    #Provide a tablename and cursor as input
    #Returns the data from the table
    sql = 'SELECT * FROM %s' % tablename
    cursor.execute(sql)
    return cursor.fetchall()
    
def save_data_to_csv(tablename, date_csv_format, cursor):
    #Takes as input a string filename, a date, and a cursor
    #Pulls the data from the given sql table and writes it to a csv
    #The name of the csv will be the filename, an underscore, and the date
    #e.g. billboardhot100_20151125
    filename = "%s_%s.csv" % (tablename, date_csv_format)
    
    writer = csv.writer(open(filename, 'w'))
    writer.writerow(['date_pulled', 'rank', 'song', 'artist'])
    sql = 'SELECT * FROM %s' % tablename
    cursor.execute(sql)
    for i in cursor.fetchall():
        writer.writerow(i)

def remove_double_quotes(my_list):
    #Takes a list, and removes double quotes from any of its items
    #Double quotes are replaced with single quotes
    #The cleaned list is returned     
    my_list_clean = []
    
    for i in my_list:
        my_list_clean.append(i.replace('"',"'"))
        
    return my_list_clean 
    
def remove_featured_artists(mylist):
    #Takes a list as input
    #Returns a new list with any featured artists removed
    #This can be run on the list of songs or the list of artists
    my_list_clean = []
    
    for i in mylist:
        i_clean = i
        if 'featuring' in i.lower():
            i_clean = i[0: i.lower().index('featuring')-1]
        if 'feat.' in i.lower():
            i_clean = i[0: i.lower().index('feat.')-1]
        my_list_clean.append(i_clean)
    
    return my_list_clean
    
def remove_extra_spaces(my_list):
    #Takes a list, and removes leading and trailing spaces from all items
    #The cleaned list is returned     
    my_list_clean = []
    
    for i in my_list:
        my_list_clean.append(i.strip())
        
    return my_list_clean 
    
    

#----------GET BILLBOARD HOT 100 LIST---------------
songs, artists, rank = initialize_lists()
soup = initialize_soup('http://www.billboard.com/charts/hot-100')

#Find all div tags with a class called row-title
#Then, find everything marked as h2. These are the song names.
for tr in soup.findAll("div", { "class" : "row-title" }):
    for td in tr.findAll("h2"):
        songs.append(str(td.text.encode('ascii','ignore')).strip())

#Find all div tags with a class called row-title
#Then, find everything marked as h2. These are the artist names.        
for tr in soup.findAll("div", { "class" : "row-title" }):
    for td in tr.findAll("h3"):
        artists.append(str(td.text.encode('ascii','ignore')).strip())

song_array, rank = initialize_song_arrays(songs)

#Make sure there are no double quotes in the songs or artists
songs = remove_double_quotes(songs)
artists = remove_double_quotes(artists)

#Remove featured artists from songs and artists lists
songs = remove_featured_artists(songs)
artists = remove_featured_artists(artists)

#Remove any leading or trailing spaces from songs and artists lists
songs = remove_extra_spaces(songs)
artists = remove_extra_spaces(artists)

#Make a blank dictionary to hold the song information
billboardhot100 = {}

#Place the rank, the artist, and the song into the dictionary
for idx in song_array: 
    billboardhot100[idx] = {"rank": rank[idx], "artist": artists[idx], "song": songs[idx]}

#Create a table to house the data
cursor = initialize_db_connection()
create_table('billboardhot100', cursor)

#Move data from dictionary to table
#The dictionary and the SQL tablename have the same name
insert_to_table(billboardhot100, 'billboardhot100', cursor)

#View the data
view_sql_table('billboardhot100', cursor)

#Write the data to csv:
save_data_to_csv('billboardhot100', date_csv_format, cursor)

#Close the cursor    
cursor.close()

#----------GET TOP SHARED ARTISTS FROM BILLBOARD---------------
songs, artists, rank = initialize_lists()
soup = initialize_soup('http://realtime.billboard.com/?chart=last24hours')

#Get all strings from the site. Append a subset of them to list_temp
list_temp = []
for j in soup.findAll(string=True):
    x = j.strip()
    x = x.replace('(','')
    x = x.replace(')','')
    x = x.replace('play in Spotify','')
    x = x.replace('play in Deezer','')
    x = x.replace('play in Apple','')
    x = x.replace('play in Rdio','')
    x = x.strip()
    if len(x)>=1:
        list_temp.append(x) 

#The site will return Billboard's Emerging Artists, Trending 140 in realtime, 
#and Trending 140 (most shared) in the past 24 hours. We are only interested in the
#most shared in the past 24 hours. First, we will scrub out unnecessary
#list elements by finding the first occurrence of the number 1, which 
#indicates the start of the first list.     
start_num = list_temp.index('1')+1
list_temp = list_temp[start_num:]

#Next, we will find the index value where the words Top 140 in Overall
#appear. This is the start of the list we want. 
start_num = list_temp.index('Top 140 in Overall')

#The following loop figures out where the top 140 in overall list ends
#It looks for a windows.NREUM to indicate the end of the list
#However, if it doesn't find that it simply sets the end of the list
#as the value for stop_num
stop_num = len(list_temp)
for i in list_temp:
    if i.startswith("window.NREUM"):
        stop_num = list_temp.index(i)

#Update list_temp to retain only the data between the starting index
#and stopping index that we identified above. This is the list we want.
list_temp = list_temp[start_num:stop_num]
list_clean = list_temp[5:]

rank = []
signal = []

#Take the elements from the cleaned up list and place them into 
#songs, artists, rank, and signal lists.
for idx, val in enumerate(list_clean):
    if idx % 4 == 0:
        rank.append(val)
    if idx % 4 == 1:
        artists.append(val)
    if idx % 4 == 2:
        songs.append(val)
    if idx % 4 == 3:
        signal.append(val)

song_array = np.arange(0, len(songs))   

#Make sure there are no double quotes in the songs or artists list
songs = remove_double_quotes(songs)
artists = remove_double_quotes(artists)

#Remove featured artists from songs and artists lists
songs = remove_featured_artists(songs)
artists = remove_featured_artists(artists)

#Remove any leading or trailing spaces from songs and artists lists
songs = remove_extra_spaces(songs)
artists = remove_extra_spaces(artists)

#Make a blank dictionary to hold the song information
billboardtoptrending = {}

#Place the rank, the artist, and the song into the dictionary
for idx in song_array: 
    billboardtoptrending[idx] = {"rank": rank[idx], "artist": artists[idx], "song": songs[idx]}

#Create a table to house the data
cursor = initialize_db_connection()
create_table('billboardtoptrending', cursor)

#Move data from dictionary to table
#The dictionary and the SQL tablename have the same name
insert_to_table(billboardtoptrending, 'billboardtoptrending', cursor)

#View the data
view_sql_table('billboardtoptrending', cursor)

#Write the data to csv:
save_data_to_csv('billboardtoptrending', date_csv_format, cursor)

#Close the cursor    
cursor.close()

#------------GET TOP 100 FROM SHAZAM-----------
songs, artists, rank = initialize_lists()
soup = initialize_soup('http://www.shazam.com/charts/top-100/united-states')

for tr in soup.find_all("p", {"class": "ti__title"}):
    songs.append(str(tr.text.encode('ascii','ignore')).strip())
    
for tr in soup.find_all("p", {"class": "ti__artist"}):
    artists.append(str(tr.text.encode('ascii','ignore')).strip())

#Make sure there are no double quotes in the songs or artists list
songs = remove_double_quotes(songs)
artists = remove_double_quotes(artists)

#Remove featured artists from songs and artists lists
songs = remove_featured_artists(songs)
artists = remove_featured_artists(artists)

#Remove any leading or trailing spaces from songs and artists lists
songs = remove_extra_spaces(songs)
artists = remove_extra_spaces(artists)

song_array, rank = initialize_song_arrays(songs)

#Make a blank dictionary to hold the song information
shazamtop100 = {}

#Place the rank, the artist, and the song into the dictionary
for idx in song_array: 
    shazamtop100[idx] = {"rank": rank[idx], "artist": artists[idx], "song": songs[idx]}

#Create a table to house the data
cursor = initialize_db_connection()
create_table('shazamtop100', cursor)

#Move data from dictionary to table
#The dictionary and the SQL tablename have the same name
insert_to_table(shazamtop100, 'shazamtop100', cursor)

#View the data
view_sql_table('shazamtop100', cursor)

#Write the data to csv:
save_data_to_csv('shazamtop100', date_csv_format, cursor)

#Close the cursor    
cursor.close()

#------------GET PREDICTED HITS FROM SHAZAM-----------
songs, artists, rank = initialize_lists()
soup = initialize_soup('http://www.shazam.com/charts/future-hits/united-states')

for tr in soup.find_all("p", {"class": "ti__title"}):
    #print str(tr.text.encode('ascii','ignore')).strip()
    songs.append(str(tr.text.encode('ascii','ignore')).strip())
    
for tr in soup.find_all("p", {"class": "ti__artist"}):
    artists.append(str(tr.text.encode('ascii','ignore')).strip())

#Make sure there are no double quotes in the songs or artists list
songs = remove_double_quotes(songs)
artists = remove_double_quotes(artists)

#Remove featured artists from songs and artists lists
songs = remove_featured_artists(songs)
artists = remove_featured_artists(artists)

#Remove any leading or trailing spaces from songs and artists lists
songs = remove_extra_spaces(songs)
artists = remove_extra_spaces(artists)

song_array, rank = initialize_song_arrays(songs)

#Make a blank dictionary to hold the song information
shazamhitpredictor = {}

#Place the rank, the artist, and the song into the dictionary
for idx in song_array: 
    shazamhitpredictor[idx] = {"rank": rank[idx], "artist": artists[idx], "song": songs[idx]}

#Create a table to house the data
cursor = initialize_db_connection()
create_table('shazamhitpredictor', cursor)

#Move data from dictionary to table
#The dictionary and the SQL tablename have the same name
insert_to_table(shazamhitpredictor, 'shazamhitpredictor', cursor)

#View the data
view_sql_table('shazamhitpredictor', cursor)

#Write the data to csv:
save_data_to_csv('shazamhitpredictor', date_csv_format, cursor)

#Close the cursor    
cursor.close()

'''
Part 2: Cumulative Database

Two of the key questions we attempt to answer in our project are:
    1) Does the shazam hit predictor accurately predict future hits on the
        Billboard Hot 100?
    2) Does the Twitter data harvested in Billboard's Trending 140 list
        accurately predict future hits on the Billboard Hot 100?
        
A limitation of web scraping is that it only pulls the current data, not
the historic data. Therefore, we have retained csv files for the past two
weeks (created using the code in Part 1) so that we could compare 
Shazam's Hit Predictor and Billboard's Trending 140 lists with 
the Billboard Hot 100 list one week later.

The following code will load the historic files into a database called 
music_cumulative. 
'''

#This program takes all csv files that have been generated
#on all dates and creates a cumulative database to store them all

import MySQLdb as SQL
import csv
import numpy as np

#-----------DEFINE ALL FUNCTIONS--------------------------------
def create_table(tablename, cursor):
    #Takes a string as an input, then creates a table with that name
    #You must also provide a cursor
    #Does not return anything
    #All tables have the same 4 fields
    sql = '''
     CREATE TABLE %s (
     date_pulled CHAR(20),
     rank CHAR(20),
     song CHAR(255),
     artist CHAR(255));
     ''' % tablename
    cursor.execute(sql)
    
def insert_to_table(filename, tablename, cursor):
    #Takes a dictionary, a string tablename, and a cursor as input
    #Pulls the data from the dictionary and inserts it into the 
    #table based on the tablename you provide          
    csv_data = csv.reader(file(filename))
    next(csv_data)
    for row in csv_data:  
        sql='''
            INSERT INTO %s (date_pulled, rank, song, artist)
            VALUES ("%s","%s","%s","%s");''' % (tablename, row[0],row[1],row[2],row[3])
        cursor.execute(sql)
        
def view_sql_table(tablename, cursor):
    #Provide a tablename and cursor as input
    #Returns the data from the table
    sql = 'SELECT * FROM %s' % tablename
    cursor.execute(sql)
    return cursor.fetchall()

#-------CREATE A CUMULATIVE DATABASE----------------

conn = SQL.connect(host='localhost', user='root', passwd='root')
cursor = conn.cursor()

sql = 'DROP DATABASE IF EXISTS music_cumulative;'
cursor.execute(sql)
sql = ' CREATE DATABASE music_cumulative; '
cursor.execute(sql)
cursor.close()

LPdb = SQL.connect(host='localhost', user='root', passwd='root', db='music_cumulative')

#set autocommit to 1 so data can be appended easily
cursor = LPdb.cursor()
sql = ' SET AUTOCOMMIT = 1;'
cursor.execute(sql)

#---------CREATE ALL TABLES---------------------------------------
create_table('billboardhot100', cursor)
create_table('billboardtoptrending', cursor)
create_table('shazamtop100', cursor)
create_table('shazamhitpredictor', cursor)

#-------------IMPORT ALL FILES IN TO THE DATABASE-----------------
billboardhot100files = ('historic_files/billboardhot100_20151114.csv','historic_files/billboardhot100_20151125.csv')
for filename in billboardhot100files:
    insert_to_table(filename, 'billboardhot100', cursor)    

billboardtoptrendingfiles = ('historic_files/billboardtoptrending_20151114.csv','historic_files/billboardtoptrending_20151125.csv')
for filename in billboardtoptrendingfiles:
    insert_to_table(filename, 'billboardtoptrending', cursor)  

shazamtop100files = ('historic_files/shazamtop100_20151114.csv','historic_files/shazamtop100_20151125.csv')
for filename in shazamtop100files:
    insert_to_table(filename, 'shazamtop100', cursor)

shazamhitpredictorfiles = ('historic_files/shazamhitpredictor_20151114.csv','historic_files/shazamhitpredictor_20151125.csv')
for filename in shazamhitpredictorfiles:
    insert_to_table(filename, 'shazamhitpredictor', cursor) 

#-------------CHECK THE DATA IN ALL OF THE TABLES----------------------
billboardhot100 = view_sql_table('billboardhot100', cursor)
billboardtoptrending = view_sql_table('billboardtoptrending', cursor)
shazamtop100 = view_sql_table('shazamtop100', cursor)
shazamhitpredictor = view_sql_table('shazamhitpredictor', cursor)

cursor.close()

'''
Part 3: Query the Cumulative Database

In this section of the code, we query the cumulative database in order 
to create the csv files required for our R plots.

This section of code creates 3 csv files:

    billboardhot100_vs_shazamtop100.csv
    shazamhitpredictor_vs_billboardhot100.csv
    billboardtoptrending_vs_billboardhot100.csv
    
These will be stored in your working directory.
    
'''
import MySQLdb as SQL

#Connect to the music_cumulative database
LPdb = SQL.connect(host='localhost', user='root', passwd='root', db='music_cumulative')
cursor = LPdb.cursor()
sql = ' SET AUTOCOMMIT = 1;'
cursor.execute(sql)

#What is the relationship between billboard hot 100 rank and shazam top 100 rank?
sql = '''
SELECT B.artist, B.song, B.rank as billboard_rank, IFNULL(S.rank, 'NA') as shazam_rank
FROM
  (SELECT *
  FROM billboardhot100
  WHERE date_pulled = '11/25/2015'
  LIMIT 30) B
LEFT OUTER JOIN 
  (SELECT * 
  FROM shazamtop100 
  WHERE date_pulled = '11/25/2015') S on B.song=S.song and LEFT(B.artist, 3)=LEFT(S.artist, 3)
'''
cursor.execute(sql)
music1 = cursor.fetchall()

with open('billboardhot100_vs_shazamtop100.csv', 'w') as handle:
    handle.write('\"artist\",\"song\",\"billboard_rank\",\"shazam_rank\"\n')
    for i in music1:
        handle.write('\"%s\",\"%s\",\"%s\",\"%s\"\n' % (i[0],i[1],i[2],i[3]))

#How accurate is the shazam hit predictor in guessing future hits?
#1 = hit, 2 = not hit
sql = '''
SELECT A.artist, A.song, A.rank as shazam_hit_predictor_rank
      , IFNULL(B.rank, 'NA') as billboard_hot_100_rank
      ,IF(B.rank IS NULL, '2', '1') as hit
FROM
  (SELECT * FROM shazamhitpredictor
  WHERE date_pulled='11/14/2015') A
LEFT OUTER JOIN 
  (SELECT * FROM billboardhot100
  WHERE date_pulled='11/25/2015') B
ON A.song=B.song and LEFT(A.artist, 3)=LEFT(B.artist, 3)
'''
cursor.execute(sql)
music2 = cursor.fetchall()

with open('shazamhitpredictor_vs_billboardhot100.csv', 'w') as handle:
    handle.write('\"artist\",\"song\",\"shazam_hit_predictor_rank",\"billboard_hot_100_rank",\"hit\"\n')
    for i in music2:
        handle.write('\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n' % (i[0],i[1],i[2],i[3],i[4]))

#Do hits trending on twitter predict future hits?
#1 = hit, 2 = not hit
sql = '''
SELECT A.artist, A.song, A.rank as billboard_top_trending_rank
      , IFNULL(B.rank, 'NA') as billboard_hot_100_rank
      , IF(B.rank IS NULL, '2', '1') as hit
FROM
  (SELECT * FROM billboardtoptrending
  WHERE date_pulled='11/14/2015'
  LIMIT 20) A
LEFT OUTER JOIN 
  (SELECT * FROM billboardhot100
  WHERE date_pulled='11/25/2015') B
ON A.song=B.song and LEFT(A.artist, 3)=LEFT(B.artist, 3)
'''
cursor.execute(sql)
music3 = cursor.fetchall()

with open('billboardtoptrending_vs_billboardhot100.csv', 'w') as handle:
    handle.write('\"artist\",\"song\",\"billboard_top_trending_rank\",\"billboard_hot_100_rank\",\"hit\"\n')
    for i in music3:
        handle.write('\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n' % (i[0],i[1],i[2],i[3],i[4]))
        
'''
Part 4: Get artists' hometowns

This section of the code uses an API to access a database (Echonest) 
containing information about the hometown cities of popular artists.
Popular artists from the billboard hot 100 list are passed to the API,
and the artists' hometowns are returned. This data is stored in locations.csv
to be read into R for vizualization. 
'''

from pyechonest import config
from pyechonest import artist
import urllib
import json
import pandas as pd
import csv

# Input the key to get the permission to use Pyechonest API
config.ECHO_NEST_API_KEY="QEVL9CB4AYV6P8PJ8"

# Base url to get the hometown info from Echonest
url1 = "http://developer.echonest.com/api/v4/artist/profile?api_key=QEVL9CB4AYV6P8PJ8&id="
url2 = "&format=json&bucket=artist_location"

# Get the top 30 Artists' name from information scrapped from BillBoard
df = pd.read_csv("historic_files/billboardhot100_20151125.csv")
artists = list(df["artist"])
artists = artists[0:30]

# Use Pyechonest API to get the artists ID then get the hometown info from Echonest
hometowns = []
for a in artists:
    try:      
        person = artist.Artist(a)
        ID = str(person.id)
    
        url = url1 + ID + url2
    
        response = urllib.urlopen(url)
        data = json.loads(response.read())
      
        hometown = data["response"]["artist"]["artist_location"]["location"]
        hometowns.append(str(hometown))
    except:
        hometowns.append("Unknown")

# Remove artists that cannot get hometown info in Echonest        
ht = {}
for i in range(0,30):
    ht[artists[i]] = hometowns[i]
    
ht = {i:ht[i] for i in ht if ht[i]!="Unknown"}

# The clean lists to generate the map of top 30 artists' hometown
artists_re = [i for i in ht]
hometown_re = [ht[i] for i in ht]
ah = zip(artists_re,hometown_re)

#save the information to a text file to import to R
with open('location.csv','w+') as handle:
    a = csv.writer(handle,delimiter=",")
    a.writerows(ah)
