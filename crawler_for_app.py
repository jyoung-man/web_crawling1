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
    #cur.execute("DROP TABLE dept;")
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
    con.commit()
    return code_num

def make_sugang_db(code):
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    #cur.execute("DROP TABLE lecture;")
    cur.execute("CREATE TABLE lecture(type text, l_number text, l_name text, credit integer, d_code text, time text, prof text);")
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
            cur = con.cursor()
            cur.execute("INSERT INTO lecture VALUES(:type, :l_number, :l_name, :credit, :d_code, :time, :prof);", {"type":data[3], "l_number":data[4], "l_name":data[5], "credit":data[7], "d_code":c , "time":data[10], "prof":data[11]})
            '''
            print(data[3]) #이수구분
            print(data[4]) #과목번호
            print(data[5]) #강의명
            print(data[7]) #학점
            print(data[9]) #수강학과 #이거 말고 code 안의 과목번호를 넣자
            print(data[10]) #시간, 장소
            print(data[11]) #담당교수
            '''
        #print(name)
        #담당 교수님이 두 분 이상인 강의 검색하는 법: where length(교수)>7(공백, 콤마 포함하여)
    con.commit()
    print(cur.fetchall())
    
if __name__ == '__main__':

    code = get_dept_code()
    make_sugang_db(code)
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    cur.execute('SELECT * FROM lecture where d_code = 127428')
    print(cur.fetchone())
    print(cur.fetchone())
    print(cur.fetchone())
    print(cur.fetchone())
    print(cur.fetchone())
    print(cur.fetchone())
    print(cur.fetchone())
    print(cur.fetchone())
    print(cur.fetchone())
