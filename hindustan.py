import time
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from dbconnect import db_con, insert_news_search_post
import uuid
from selenium import webdriver
import re
from datetime import datetime, timedelta
import json
from selenium.webdriver.common.keys import Keys

class LoopBreak(Exception):
    pass

ignore = re.compile(
    '[\n\r\t\xa0\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U0001F90D-\U0001F9FF\u202f]')
def ignore_text(text):
    return ignore.sub(' ', text).strip()

def hindustan():
    model_kwargs = {
        'source_name': 'hindustan times',
        'biz_kind': 'news',
        'country': 'India',
        'methd': 'search',
        'category': 'article'
    }

    # 기준날짜 2021년
    first_date = '2021/01/01'
    first_date = datetime.strptime(first_date, '%Y/%m/%d')
    first_date = first_date.date()

    # 기준날짜 2021년
    second_date = '2021/11/30'
    second_date = datetime.strptime(second_date, '%Y/%m/%d')
    second_date = second_date.date()

    conn = db_con()
    http_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}

    ## setup Driver|Chrome : 크롬드라이버를 사용하는 driver 생성
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
    # # chrome_options.add_argument("--headless")
    # driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)  # 크롬 드라이버를 사용하는 드라이버 생성
    # driver.implicitly_wait(5)  ## 웹 자원을 3초 기다리기

    #검색 키워드
    wordlist3 = [['korean music', '공통'], ['k pop', '공통'], ['korean film', '공통'],
                 ['korean movie', '공통'], ['korean tv', '공통'], ['korean drama', '공통'], ['korean variety', '공통'],
                 ['korean food', '공통'], ['korean beauty', '공통'], ['korean cosmetic', '공통'],
                 ['squid game', '공통'], ['dalgona', '공통']]
    print(wordlist3)

    for keyword in wordlist3:  #키워드별 검색
        pds_urls = []
        i = 1
        try:
            while True:
                with requests.Session() as session:
                    seed_url = 'https://www.hindustantimes.com/search?q='+keyword[0]+'&page='+str(i)
                    i += 1
                    print(seed_url)
                    resp = session.get(url=seed_url, headers=http_header)
                    data = resp.text
                    soupsoup = BeautifulSoup(data, "html.parser")
                    #기사들
                    posts = soupsoup.select('.ht-ad-holder .cartHolder.listView')

                for post in posts:
                    #url
                    post_url = 'https://www.hindustantimes.com' + post.select_one('.cartHolder.listView .hdg3 a').get('href')
                    print(post_url)
                    #작성일자
                    post_post_dates = post.select_one('.dateTime').text
                    print(post_post_dates)
                    post_dates = post_post_dates.split('on ')[1]
                    post_dates = post_dates.replace('IST', '').strip()
                    print(post_dates)
                    post_dates = datetime.strptime(post_dates, '%b %d, %Y %I:%M %p')
                    post_dates = post_dates.date()
                    print(post_dates)

                    pd_url = [post_url, post_dates]
                    if pd_url not in pds_urls:
                        if '/videos/' in post_url:
                            print('no video')
                            continue
                        elif '/photos/' in post_url:
                            print('no photo')
                            continue

                        if post_dates > second_date:
                            print('later than')
                            continue

                        if post_dates < first_date: #기준일 보다 이르면 그만
                            print('earlier than')
                            raise LoopBreak()
                        else:
                            pds_urls.append(pd_url)
                time.sleep(1)
                print(pds_urls)
                if i > 50:
                    break
                if len(posts) < 30:
                    break

        except LoopBreak:
            pass

        for url in pds_urls:
            print('-'*200)
            print('-'*200)
            print('-'*200)

            with requests.Session() as session:
                seed_url = url[0]
                print(seed_url)
                resp = session.get(url=seed_url, headers=http_header)
                data = resp.text
                soupsoup = BeautifulSoup(data, "html.parser")
                #제목
                title = soupsoup.select_one('.fullStory.tfStory .hdg1').text
                print(title)
                #기사가 아닌 부분 제거
                try:
                    text_remove = soupsoup.select_one('.font-italic')
                    text_remove.clear()
                    print('strange thing eliminated')
                except:
                    None
                #본문
                try:
                    content = []
                    contents = soupsoup.select('.tfStory .storyDetails .detail p')
                    for t in contents:
                        if 'Also Read' in t.text:
                            continue
                        else:
                            content.append(t.text)
                    # content = [t.text for t in contents]
                    content = " ".join(content)
                    content = content.strip()
                except:
                    content = []

                postdate = url[1]
                print(postdate)

                # 뉴스 기사
                model_kwargs['data_id'] = str(uuid.uuid4()).replace('-', '')
                model_kwargs['keyword'] = keyword[0]
                model_kwargs['keyword_kr'] = keyword[1]
                model_kwargs['url'] = url[0]
                model_kwargs['post_date'] = postdate
                model_kwargs['title'] = ignore_text(title)
                model_kwargs['content'] = ignore_text(content)
                model_kwargs['comment_count'] = None
                model_kwargs['dislike_count'] = None
                model_kwargs['view_count'] = None
                model_kwargs['vote'] = None
                model_kwargs['tag'] = None
                print(model_kwargs)

                insert_news_search_post(conn=conn, model_kwargs=model_kwargs)
                time.sleep(2)
    conn.close()

hindustan()
