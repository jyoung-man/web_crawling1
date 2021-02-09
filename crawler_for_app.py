# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 23:04:22 2021

@author: Jy
"""
#!/usr/bin/env python
# coding: utf-8

import requests
import sqlite3
import re
import time
from bs4 import BeautifulSoup  #refecence: https://www.crummy.com/software/BeautifulSoup/bs4/doc/


    
def get_url_contents(url):
    s = None
    try:
        s = requests.Session()
        resp = s.get(url)
        return resp.status_code, resp.text
    finally:
        if s is not None:
            s.close()
            
def get_dept_code():
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    cur.execute("DROP TABLE dept;")
    cur.execute("CREATE TABLE dept(d_name text, d_code text);")
    url = 'https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01011'
    sc, fc = get_url_contents(url)
    parse = BeautifulSoup(fc, 'html.parser')
    depts = parse.find_all("select", {"name": "openSust"}) 
    dept = []
    code = []

    for t in depts:
        name = t.text
        code.append(str(t))
        dept.append(name)

    code_num = re.findall("\d+", code[0]) #문자열에서 숫자만 추출하는 함수
    dept_name = dept[0].split('\n')
    code_num = code_num[1:]
    dept_name = dept_name[3:-1]
    i = 0
    
    for n in dept_name:
        cur = con.cursor()
        cur.execute('INSERT INTO dept VALUES(:d_name, :d_code);', {"d_name":n, "d_code":code_num[i]})
        i+=1
    
    delete = ["105291", "105321", "126784", "127320", "105541", "105561", "105591", "126905", "126777", "121012", "103391", "122056", "122053", "122054", "122410", "122412", "122058", "122062", "122096", "120806", "120809", "122098", "122099", "126791", "122097", "103013", "102931", "127425", "103851", "103901", "121218", "126790", "126782", "103912", "103911", "126793", "122048", "122102", "122101", "122100", "126792", "122104", "104601", "122103", "104581", "121242", "121243", "121244", "126779", "105441", "105451", "126778", "103741", "126788", "103681", "127109", "126789", "103731", "120933", "127114", "127113", "121134", "121136", "126785", "103271", "126902", "122216", "003221", "126901", "127117", "127117", "122227", "126904", "121263", "122405", "122080", "122409", "126799", "122407", "122408", "105251", "103751", "105611", "127116", "122071"]
    for d in delete:
        cur = con.cursor()
        cur.execute('DELETE FROM dept WHERE d_code = "{}";'.format(d))
    con.commit()
    return code_num

def make_major_db(code):
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    cur.execute("DROP TABLE major;")
    cur.execute("CREATE TABLE major(type text, l_number text, l_name text, credit integer, d_code text, time text, prof text, untact text, note text, section text);")
    url = "https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01011"
    for c in code:
        dept = "&openSust="+c
        sc, fc = get_url_contents(url+dept)
        parse = BeautifulSoup(fc, 'html.parser')
        datas = parse.find_all("tr", {"class": "table_bg_white"})
        if len(datas) < 10:
            continue
        data = []
        print(c)
        time.sleep(2)
        for t in datas[1:]:
            data = t.text.split('\n')
            k_lecture = data[5].split('(')
            data[5] = k_lecture[0]
            _prof = data[11].split(',')
            data[11] = _prof[0]
            cur = con.cursor()
            cur.execute("INSERT INTO major VALUES(:type, :l_number, :l_name, :credit, :d_code, :time, :prof, :untact, :note, :section);", {"type":data[3], "l_number":data[4], "l_name":data[5], "credit":data[7], "d_code":c , "time":data[10], "prof":data[11], "untact":data[17], "note":data[22], "section":data[20]})
            '''
            print(data[3]) #이수구분
            print(data[4]) #과목번호
            print(data[5]) #강의명
            print(data[7]) #학점
            print(data[9]) #수강학과 #이거 말고 code 안의 과목번호를 넣자
            print(data[10]) #시간, 장소
            print(data[11]) #담당교수
            '''
            print(data[17]) #녹화:실시간:대면
            print(data[22]) #note

        #print(name)
        #담당 교수님이 두 분 이상인 강의 검색하는 법: where length(교수)>7(공백, 콤마 포함하여)
        
    con.commit()
    print(cur.fetchall())
    
def make_curtural_db():
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    cur.execute("DROP TABLE cultural;")
    cur.execute("CREATE TABLE cultural(type text, l_number text, l_name text, credit integer, d_code text, time text, prof text, untact text, note text, section text);")
    url = "https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01011&pobtDiv="
    code = ["B0404P", "B04054"]
    for c in code:
        sc, fc = get_url_contents(url+c)
        parse = BeautifulSoup(fc, 'html.parser')
        datas = parse.find_all("tr", {"class": "table_bg_white"})
        if len(datas) < 10:
            continue
        data = []
        time.sleep(2)
        for t in datas[1:]:
            data = t.text.split('\n')
            k_lecture = data[5].split('(')
            data[5] = k_lecture[0]
            _prof = data[11].split(',')
            data[11] = _prof[0]
            cur = con.cursor()
            cur.execute("INSERT INTO cultural VALUES(:type, :l_number, :l_name, :credit, :d_code, :time, :prof, :untact, :note, :section);", {"type":data[3], "l_number":data[4], "l_name":data[5], "credit":data[7], "d_code":c , "time":data[10], "prof":data[11], "untact":data[17], "note":data[22], "section":data[20]})
            '''
            print(data[3]) #이수구분
            print(data[4]) #과목번호
            print(data[5]) #강의명
            print(data[7]) #학점
            print(data[9]) #수강학과 #이거 말고 code 안의 과목번호를 넣자
            print(data[10]) #시간, 장소
            print(data[11]) #담당교수
            '''
            print(data[17]) #녹화:실시간:대면
            print(data[22]) #note
            print(data[20]) #section, 영역

        #print(name)
        #담당 교수님이 두 분 이상인 강의 검색하는 법: where length(교수)>7(공백, 콤마 포함하여)
    con.commit()
    
def dept_for_me():
    
    url = 'https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01011'
    sc, fc = get_url_contents(url)
    parse = BeautifulSoup(fc, 'html.parser')
    depts = parse.find_all("select", {"name": "openSust"}) 
    dept = []
    code = []

    for t in depts:
        name = t
        print(name)
        code.append(str(t))
        dept.append(name)
    
    return

def delete_more_dept():
    #delete = ["105291", "105321", "126784", "127320", "105541", "105561", "105591", "126905", "126777", "121012", "103391", "122056", "122053", "122054", "122410", "122412", "122058", "122062", "122096", "120806", "120809", "122098", "122099", "126791", "122097", "103013", "102931", "127425", "103851", "103901", "121218", "126790", "126782", "103912", "103911", "126793", "122048", "122102", "122101", "122100", "126792", "122104", "104601", "122103", "104581", "121242", "121243", "121244", "126779", "105441", "105451", "126778", "103741", "126788", "103681", "127109", "126789", "103731", "120933", "127114", "127113", "121134", "121136", "126785", "103271", "126902", "122216", "003221", "126901", "127117", "127117", "122227", "126904", "121263", "122405", "122080", "122409", "126799", "122407", "122408", "105251", "103751", "105611", "127116", "122071"]
    #delete = ["003221", "126901", "127117", "122227", "126904", "121263", "122405", "122080", "122409", "126799", "122407", "122408", "105251", "103751", "105611", "127116", "122071"]
    delete = ["127307"]
    con = sqlite3.connect('./iku.sqlite')
    for d in delete:
        cur = con.cursor()
        cur.execute('DELETE FROM dept WHERE d_code = "{}";'.format(d))
        cur.execute('DELETE FROM major WHERE d_code = "{}";'.format(d))
    con.commit()
    
        
def insert_lecture(dept):
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    url = "https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01011&openSust="
    sc, fc = get_url_contents(url+dept)
    parse = BeautifulSoup(fc, 'html.parser')
    datas = parse.find_all("tr", {"class": "table_bg_white"})
    data = []
    print(dept)
    time.sleep(2)
    for t in datas[1:]:
        data = t.text.split('\n')
        k_lecture = data[5].split('(')
        data[5] = k_lecture[0]
        _prof = data[11].split(',')
        data[11] = _prof[0]
        cur = con.cursor()
        cur.execute("INSERT INTO major VALUES(:type, :l_number, :l_name, :credit, :d_code, :time, :prof, :untact, :note);", {"type":data[3], "l_number":data[4], "l_name":data[5], "credit":data[7], "d_code":dept , "time":data[10], "prof":data[11], "untact":data[17], "note":data[22], "section":data[20]})
        '''
        print(data[3]) #이수구분
        print(data[4]) #과목번호
        print(data[5]) #강의명
        print(data[7]) #학점
        print(data[9]) #수강학과 #이거 말고 code 안의 과목번호를 넣자
        print(data[10]) #시간, 장소
        print(data[11]) #담당교수
        '''
    con.commit()
    
def update_lecture_data():
    con = sqlite3.connect('./iku.sqlite')
    f = open('items_to_change.txt', 'r')
    line = f.readline()
    while True:
        items = line.split(" ")
        dept = items[0]
        del items[0]
        for i in items:
            print(i)
            sql = 'update major set d_code = "{}" where l_number = "{}";'.format(dept, i)
            cur = con.cursor()
            cur.execute(sql)
            print(sql)
        line = f.readline()
        if not line: break
    college = ["105271", "126897", "102761", "104951", "127119", "122045", "105121", "105061"]
    cur.execute('update major set d_code = "105091" where d_code = "105061";')
    cur.execute('update dept set d_name = "건축대학 건축학부" where d_code = "121135";')
    for c in college:
        cur.execute('DELETE FROM dept WHERE d_code = {};'.format(c))
    con.commit()
    f.close()

    
def refresh_db():
    code = get_dept_code()
    make_major_db(code)
    make_curtural_db() 
    update_lecture_data()

if __name__ == '__main__':
    #dept_for_me()
    #dept = "105271"
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    cur.execute('update dept set d_name = "건축대학 건축학부" where d_code = "121135";')
    con.commit()
    cur.execute('SELECT * FROM dept;')
    #cur.execute('select * from major where d_code = "105061";');
    #cur.execute('SELECT * FROM cultural;')
    #print(cur.fetchall())

    for i in range(100):
        print(cur.fetchone())

