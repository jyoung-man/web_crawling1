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

def insert_into_db(url, c):
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    sc, fc = get_url_contents(url+c)
    parse = BeautifulSoup(fc, 'html.parser')
    datas = parse.find_all("tr", {"class": "table_bg_white"})
    if len(datas) < 10: 
        return #NULL POINT EXCEPTION 방지. 정보가 안 나오는 강의는 조회 안하도록
    data = []
    print(c)
    time.sleep(2) #트래픽 한 번에 너무 많이 몰리지 않게
    for t in datas[1:]:
        data = t.text.split('\n')
        k_lecture = data[5].split('(')
        data[5] = k_lecture[0]
        when, where = calculate_time(data[10].strip())
        _prof = data[11].split(',')
        data[11] = _prof[0].strip()
        cur = con.cursor()
        cur.execute("INSERT INTO lecture VALUES(:type, :l_number, :l_name, :d_code, :prof, :section);", {"type":data[3], "l_number":data[4], "l_name":data[5], "d_code":c , "prof":data[11], "section":data[20]})
        cur.execute("REPLACE INTO lec_info VALUES(:l_number, :credit, :time, :classroom, :untact, :note);", {"l_number":data[4], "credit":data[7], "time":when, "classroom":where, "untact":data[17], "note":data[22]})
        '''
        print(data[3]) #이수구분
        print(data[4]) #과목번호
        print(data[5]) #강의명
        print(data[7]) #학점
        print(data[9]) #수강학과 #이거 말고 code 안의 과목번호를 넣자
        print(data[10]) #시간, 장소
        print(data[11]) #담당교수
        print(data[17]) #녹화:실시간:대면
        print(data[22]) #note
        '''
    con.commit()

def make_lecture_db(code):
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    cur.execute("DROP TABLE lecture;")
    cur.execute("CREATE TABLE lecture(type text, l_number text, l_name text, d_code text, prof text, section text);")
    cur.execute("DROP TABLE lec_info;")
    cur.execute("CREATE TABLE lec_info(l_number text, credit integer, time text, classroom text, untact text, note text);")
    for c in code:
        url = "https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01011&openSust="
        insert_into_db(url, c)
        
    type_code = ["B0404P", "B04054"]
    for t in type_code:
        url = "https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01011&pobtDiv="
        insert_into_db(url, t)
    con.commit()
    
def show_dept_for_me():
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
        #cur.execute('DELETE FROM lecture WHERE d_code = "{}";'.format(d))
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
            sql = 'update lecture set d_code = "{}" where l_number = "{}";'.format(dept, i)
            cur = con.cursor()
            cur.execute(sql)
            print(sql)
        line = f.readline()
        if not line: break
    college = ["105271", "126897", "102761", "104951", "127119", "122045", "105121", "105061"]
    cur.execute('update lecture set d_code = "105091" where d_code = "105061";')
    cur.execute('update dept set d_name = "건축대학 건축학부" where d_code = "121135";')
    for c in college:
        cur.execute('DELETE FROM dept WHERE d_code = {};'.format(c))
    con.commit()
    f.close()

def get_prof_database():
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    cur.execute("DROP TABLE professor;")
    cur.execute("CREATE TABLE professor(prof text, lab text, contact text);")
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_01_01_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_01_02_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_01_02_02_tab01.jsp"    
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_01_01_02_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_01_01_03_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_02_01_05_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_01_03_02_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_01_03_04_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_02_01_01_tab01.jsp"
    insert_prof_data(url)
    #url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_02_01_02_tab01.jsp"
    #insert_prof_data(url)
    #물리학과
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_02_01_03_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_03_01_04_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_11_01_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_04_10_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_04_03_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_04_04_02_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_05_01_04_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_04_05_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_15_01_05_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_04_04_03_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_04_08_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_06_01_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_08_01_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_06_01_02_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_08_01_02_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_08_02_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_15_01_02_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_15_01_03_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_09_01_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_09_01_03_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_20_01_03_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_20_01_04_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_20_01_05_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_20_01_06_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_20_01_07_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_20_01_10_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_20_01_08_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_20_01_09_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_12_01_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_13_01_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_13_01_02_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_13_01_03_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_13_01_05_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_13_02_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_13_02_05_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_14_01_01_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_14_01_02_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_14_01_03_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_14_01_04_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_14_01_05_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_14_01_06_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_14_01_07_tab01.jsp"
    insert_prof_data(url)
    url = "https://www.konkuk.ac.kr/jsp/Coll/coll_01_19.jsp"
    insert_prof_data(url)
    #부동산학과, 물리학과, 생과대 안넣었음    
    
def insert_prof_data(url):
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    sc, fc = get_url_contents(url)
    parse = BeautifulSoup(fc, 'html.parser')
    datas = parse.find_all("tr")
    data = []
    for d in datas[1:]:
        data = d.text.split("\n")
        cur.execute('INSERT INTO professor VALUES(:prof, :lab, :contact);', {"prof":data[2], "lab":data[5], "contact":data[7]})
        print(data[2]) #교수님 성함
        print(data[5]) #연구실
        print(data[7]) #이메일       
    con.commit()

def calculate_time(info):
    info = info.replace(" ", "")
    days = info.split(",")
    when = ""
    where = ""
    for i in range(len(days)):
        if i>0:
            when += ','
            where += ','
        time = []        
        temp = re.findall("\d+", days[i])

        mark = days[i].find('(')
        where += days[i][mark:]

        for t in temp:
            k = float(t)/2 + 9
            sc = str(k)
            val = str(sc).find(".5")
            if val == -1:
                sc = sc.replace(".0", ":00")
            else:
                sc = sc.replace(".5", ":30")
            time.append(sc)
        #print(time)
        if len(time) > 1:    
            when += (days[i][0] + time[0] + "-" + time[1])
        elif len(time) > 0:
            when += days[i][0]
        else:
            continue
    #print(when)
    return when, where
    
    
def refresh_db():
    code = get_dept_code()
    make_lecture_db(code)
    update_lecture_data()
    get_prof_database()
    
if __name__ == '__main__':
    #dept_for_me()
    #dept = "105271"
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    cur.execute('select * from lecture where prof = "SANGILIYANDI";')
    print(cur.fetchall())
    '''
    cur.execute('select * from professor;')
    for i in range(600):
        print(cur.fetchone())
    '''
    #cur.execute('update dept set d_name = "건축대학 건축학부" where d_code = "121135";')
    #con.commit()
    #refresh_db()
    #get_prof_database()

