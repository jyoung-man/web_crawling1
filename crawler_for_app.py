# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 23:04:22 2021

@author: Jy
"""
#!/usr/bin/env python
# coding: utf-8

import requests
import sqlite3
from requests_file import FileAdapter
import re
import time
from bs4 import BeautifulSoup  #refecence: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

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
            
def get_dept_code():
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    cur.execute("DROP TABLE dept;")
    cur.execute("CREATE TABLE dept(d_name text, d_code text);")
    url = 'https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01012'
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
    park = []
    print(c)
    time.sleep(1) #트래픽 한 번에 너무 많이 몰리지 않게
    for t in datas[1:]:
        data = t.text.split('\n')
        k_lecture = data[5].split('(')
        data[5] = k_lecture[0]
        when, where = calculate_time(data[10].strip())
        _prof = data[11].split(',')
        data[11] = _prof[0].strip()
        park = get_ratio_data(data[4])
        cur = con.cursor()
        cur.execute("INSERT INTO lecture VALUES(:type, :l_number, :l_name, :d_code, :prof, :section);", {"type":data[3], "l_number":data[4], "l_name":data[5], "d_code":c , "prof":data[11], "section":data[20]})
        cur.execute("REPLACE INTO lec_info VALUES(:l_number, :credit, :time, :classroom, :untact, :note, :first, :second, :third, :fourth);", {"l_number":data[4], "credit":data[7], "time":when, "classroom":where, "untact":data[17], "note":data[22], "first":park[0], "second":park[1], "third":park[2], "fourth":park[3]})
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
    cur.execute("CREATE TABLE lec_info(l_number text, credit integer, time text, classroom text, untact text, note text, first double, second double, third double, fourth double);")
    for c in code:
        url = "https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01012&openSust="
        insert_into_db(url, c)
        
    type_code = ["B0404P", "B04054", "B04047"]
    for t in type_code:
        url = "https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01012&pobtDiv="
        insert_into_db(url, t)
    con.commit()
    
def show_dept_for_me():  #융합치유전공  추가해줘
    url = 'https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01012'
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
    delete = ["105291", "105321", "126784", "127320", "105541", "105561", "105591", "126905", "126777", "121012", "103391", "122056", "122053", "122054", "122410", "122412", "122058", "122062", "122096", "120806", "120809", "122098", "122099", "126791", "122097", "103013", "102931", "127425", "103851", "103901", "121218", "126790", "126782", "103912", "103911", "126793", "122048", "122102", "122101", "122100", "126792", "122104", "104601", "122103", "104581", "121242", "121243", "121244", "126779", "105441", "105451", "126778", "103741", "126788", "103681", "127109", "126789", "103731", "120933", "127114", "127113", "121134", "121136", "126785", "103271", "126902", "122216", "003221", "126901", "127117", "127117", "122227", "126904", "121263", "122405", "122080", "122409", "126799", "122407", "122408", "105251", "103751", "105611", "127116", "122071"]
    con = sqlite3.connect('./iku.sqlite')
    for d in delete:
        cur = con.cursor()
        cur.execute('DELETE FROM dept WHERE d_code = "{}";'.format(d))
    con.commit()
    
def update_lecture_data():
    con = sqlite3.connect('./iku.sqlite')
    f = open('items_to_change.txt', 'r')
    line = f.readline()
    while True:
        items = line.split(" ")
        dept = items[0]
        del items[0]
        for i in items[:-1]:
            print(i)
            sql = 'INSERT INTO lecture (type, l_number, l_name, d_code, prof, section) SELECT type, l_number, l_name, "{}", prof, section FROM lecture WHERE l_number = "{}" LIMIT 1;'.format(dept, i)

           # sql = 'update lecture set d_code = "{}" where l_number = "{}";'.format(dept, i)
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
        #print(data[2]) #교수님 성함
        #print(data[5]) #연구실
        #print(data[7]) #이메일       
    con.commit()

def physics_prof_data(url):
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    sc, fc = get_url_contents(url)
    parse = BeautifulSoup(fc, 'html.parser')
    datas = parse.find_all("tr")
    data = []
    for d in datas[1:]:
        data = d.text.split("\n")
        cur.execute('INSERT INTO professor VALUES(:prof, :lab, :contact);', {"prof":data[2], "lab":data[5], "contact":data[7]})
        #print(data[2]) #교수님 성함
        #print(data[5]) #연구실
        #print(data[7]) #이메일       
    con.commit()
    
def sanghuh_prof_data(url):
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    sc, fc = get_url_contents(url)
    parse = BeautifulSoup(fc, 'html.parser')
    datas = parse.find_all("dd")
    data = []
    professor = []
    i = 0
    for d in range(len(datas)):
        data = datas[d].text.split("\n")
        value = data[0].split(" : ")
        if len(value) > 1 and (d%8 == 0 or d%8 == 3 or d%8 == 5):
            professor.append(value[1])
            
            #print(value[1])
        
    #print(professor)
    count = len(professor)
    for i in range(int(count/3)):
        j = 3*i
        name = professor[j].split(" ( ")
        cur.execute('INSERT INTO professor VALUES(:prof, :lab, :contact);', {"prof":name[0], "lab":professor[j+1], "contact":professor[j+2]})
        #print(name[0]) #교수님 성함
        #print(professor[j+1]) #연구실
        #print(professor[j+2]) #이메일
    con.commit()
    
def realestate_prof_data(url):
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    sc, fc = get_url_contents(url)
    parse = BeautifulSoup(fc, 'html.parser')
    datas = parse.find_all("div", {"class": "con"})
    data = []
    for d in datas[1:]:
        data = d.text.replace("\t", "").replace("\r","").split("\n")
        lab = data[14].split(" : ")
        mail = data[13].split(" : ")
        #print(data)
        cur.execute('INSERT INTO professor VALUES(:prof, :lab, :contact);', {"prof":data[4], "lab":lab[1], "contact":mail[1]})
        #print(data[4]) #교수님 성함
        #print(lab[1]) #연구실
        #print(mail[1]) #이메일       
    con.commit()
    
def get_more_prof_db():
    url = 'file:///content/web_crawling1/dept/'
    dept = ['anis', 'anis2', 'biology', 'biology2', 'biology3', 'cropscience', 'ehs', 'fla', 'fla2', 'foodbio', 'foodbio2', 'kufsm']
    for d in dept:
        target = url + d + '.html'
        sanghuh_prof_data(target)
    physics_prof_data(url + 'physics.html')
    realestate_prof_data(url + 'realestate.html')
    
def get_ratio_data(code):
    park = []
    
    for i in range(1, 5):
        url = "https://kupis.konkuk.ac.kr/sugang/acd/cour/aply/CourBasketInwonInq.jsp?ltYy=2021&ltShtm=B01012&sbjtId={}&promShyr={}&fg=B".format(code, str(i))
        sc, fc = get_url_contents(url)
        parse = BeautifulSoup(fc, 'html.parser')
        students = parse.find_all("td",{"align": "center"})
        if students:
          temp = str(students[0])
          temp = temp.split(" / ")
          value = temp[1].split("<")
          if len(value[0]) > 0:
              flo = float(value[0])
              park.append(flo)
          else:
              park.append(1)
        else:
          park.append(1)
    return park

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
    
def teaching():
    t = "B04047"
    name = "교직"
    url = "https://kupis.konkuk.ac.kr/sugang/acd/cour/time/SeoulTimetableInfo.jsp?ltYy=2021&ltShtm=B01012&pobtDiv="
    insert_into_db(url, t)
    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    cur.execute('INSERT INTO dept VALUES(:d_name, :d_code);', {"d_name":name, "d_code":t})
    con.commit()
    
def refresh_db():
    code = get_dept_code()
    make_lecture_db(code)
    teaching()
    update_lecture_data()
    get_prof_database()
    get_more_prof_db()
    
if __name__ == '__main__':
    show_dept_for_me()
    refresh_db()

    con = sqlite3.connect('./iku.sqlite')
    cur = con.cursor()
    #cur.execute('update dept set d_name = replace(d_name, "KU융합과학기술원", "KIT");')
    cur.execute('update professor set prof = "켈리" where prof = "Kelly Ashihara";')
    con.commit()

    '''
    #cur.execute('select * from lecture natural join lec_info where l_number = "3206";')
    #cur.execute('select * from lecture where prof in (select prof from lecture where prof = "김석");')
    #cur.execute('select prof from professor where prof in (select prof from professor group by prof having count(prof)>1);')
    #cur.execute('select * from professor where prof = "Kelly";')
    con.commit
    cur.execute('select * from lecture where prof = "켈리";')
    print(cur.fetchall())
    '''

    #cur.execute('select * from lecture where d_code =  "127123";')
    cur.execute('select * from lec_info where l_number =  "3208";')

    for i in range(200):
        print(cur.fetchone())
