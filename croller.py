#!/usr/bin/env python
# coding: utf-8

import requests
import sqlite3
from requests_file import FileAdapter
from bs4 import BeautifulSoup

    
def get_url_contents(url):
    s = None
    try:
        s = requests.Session()
        if url.lower().startswith('file://'):
            s.mount('file://', FileAdapter())
            resp = s.get(url)
        else:
            resp = s.get(url)
        return resp.status_code, resp.text
    finally:
        if s is not None:
            s.close()
            
def splitdata(year, func):
    url = 'https://www.weather.go.kr/weather/climate/past_table.jsp?stn=108&yy='
    date = str(year) + "&obs="+func
    sc, fc = get_url_contents(url+date)
    parse = BeautifulSoup(fc, 'html.parser')
    temps = parse.find_all("tr") 
    temp = []
        
    for t in temps:
        data = t.text
        temp.append(data)
    
    return temp[-1]
            
def get_music_data():
    y = 1990
    m = 3
    RANK = 30
    con = sqlite3.connect('./music.db')
    cur = con.cursor()
    cur.execute("DROP TABLE musicdb")
    cur.execute("CREATE TABLE musicdb(rank integer, title text, artist text, album text, year integer, month integer);")
    url = 'file:///C:/DB/melon/'
    
    while y<2020:
        date = str(y)+ "/" + str(y) + "_" + str(m) + ".html"
        print(url+date)
        sc, fc = get_url_contents(url+date)
        #print('url="%s"\nsc=%s\nfc=<%s>' % (url, sc, fc))
        parse = BeautifulSoup(fc, 'html.parser')
     
        titles = parse.find_all("div", {"class": "ellipsis rank01"}) 
        singers = parse.find_all("div", {"class": "ellipsis rank02"}) 
        albums = parse.find_all("div",{"class": "ellipsis rank03"})

        title = []
        singer = []
        album = []
     
        for t in titles:
            title.append(t.find('strong').text)
     
        for s in singers:
            singer.append(s.find('span', {"class": "checkEllipsis"}).text)
     
        for a in albums:
            album.append(a.find('a').text)
        
        for i in range(RANK):
            #print('%3d위: %s [ %s ] - %s'%(i+1, title[i], singer[i]))
            cur = con.cursor()
            cur.execute('INSERT INTO musicdb VALUES(:rank, :title, :artist, :album, :year, :month);', {"rank":i, "title":title[i], "artist":singer[i], "album":album[i], "year":y, "month":m})
        if m<12:
            m = m+1
        else:
            m = 1
            y = y+1
    y=2020
    
    while m<9:
        date = str(y)+ "/" + str(y) + "_" + str(m) + ".html"
        print(url+date)
        sc, fc = get_url_contents(url+date)
        #print('url="%s"\nsc=%s\nfc=<%s>' % (url, sc, fc))
        parse = BeautifulSoup(fc, 'html.parser')
     
        titles = parse.find_all("div", {"class": "ellipsis rank01"}) 
        singers = parse.find_all("div", {"class": "ellipsis rank02"}) 
        albums = parse.find_all("div",{"class": "ellipsis rank03"})

        title = []
        singer = []
        album = []

        for t in titles:
            title.append(t.find('strong').text)
     
        for s in singers:
            singer.append(s.find('span', {"class": "checkEllipsis"}).text)
     
        for a in albums:
            album.append(a.find('a').text)
        
        for i in range(RANK):
            #print('%3d위: %s [ %s ] - %s'%(i+1, title[i], singer[i]))
            cur = con.cursor()
            cur.execute('INSERT INTO musicdb VALUES(:rank, :title, :artist, :album, :year, :month);', {"rank":i, "title":title[i], "artist":singer[i], "album":album[i], "year":y, "month":m})
        
        m=m+1
    
    con.commit()
    #cur = con.cursor()
    #cur.execute('SELECT * FROM musicdb where year=2017')
    #print(cur.fetchall())


def get_weather_data():
    y = 1990
    m = 12
    con = sqlite3.connect('./music.db')
    cur = con.cursor()
    cur.execute("DROP TABLE weatherdb;")

    cur.execute("CREATE TABLE weatherdb(year integer, month integer, temp text, precipitation text);")
    
    while y<2021:
        tp = splitdata(y, "07").split("평균\n")
        t_data = tp[1].split("\n")
        print(t_data)

        pp = splitdata(y, "21").split("합계\n")
        p_data = pp[1].split("\n")
        print(p_data)
        
        if y == 2020:
            m = 8
        
        for i in range(m):
            cur = con.cursor()
            cur.execute('INSERT INTO weatherdb VALUES(:year, :month, :temp, :precipitation);', {"year":y, "month":i+1, "temp":t_data[i], "precipitation":p_data[i]})
        
        con.commit()
        y=y+1
        
    #cur = con.cursor()
    #cur.execute('SELECT * FROM weatherdb where year=2017 and month=8')
    #print(cur.fetchall())
    cur = con.cursor()    
    cur.execute('SELECT * FROM weatherdb where year=2020')
    print(cur.fetchall())


if __name__ == '__main__':
    get_music_data()
    #get_weather_data()
    con = sqlite3.connect('./music.db')
    cur = con.cursor()
    #cur.execute('SELECT AVG(precipitation) FROM weatherdb GROUP BY month')
    cur.execute('SELECT year, month, precipitation FROM weatherdb WHERE year=1990')
    #cur.execute('SELECT * FROM musicdb WHERE title = "시든 꽃에 물을 주듯"')
    print(cur.fetchall())
