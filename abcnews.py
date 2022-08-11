import time
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from dbconnect import db_con, insert_news_search_post
import uuid
from selenium import webdriver
import re

class LoopBreak(Exception):
    pass

ignore = re.compile(
    '[\n\r\t\xa0\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U0001F90D-\U0001F9FF\u202f]')
def ignore_text(text):
    return ignore.sub(' ', text).strip()

def abcnews():
    model_kwargs = {
        'source_name': 'abcnews',
        'biz_kind': 'news',
        'country': 'Australia',
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
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)  # 크롬 드라이버를 사용하는 드라이버 생성
    driver.implicitly_wait(5)  ## 웹 자원을 3초 기다리기

    #검색 키워드
    wordlist3 = [['korean', '공통'], ['korean music', '공통'], ['k pop', '공통'], ['korean film', '공통'],
                 ['korean movie', '공통'], ['k movie', '공통'], ['korean tv', '공통'], ['korean drama', '공통'],
                 ['korean variety', '공통'], ['k drama', '공통'], ['k variety', '공통'], ['k food', '공통'],
                 ['korean food', '공통'], ['k beauty', '공통'], ['korean beauty', '공통'], ['korean cosmetic', '공통'],
                 ['squid game', '공통'], ['dalgona', '공통']]
    print(wordlist3)

    for keyword in wordlist3:#키워드별 검색
        pds_urls = []#[url, 작성일]을 적재할 리스트
        try:
            i = 1
            while True:
                searchurl = 'https://search-beta.abc.net.au/#/?configure%5BgetRankingInfo%5D=true&configure%5BclickAnalytics%5D=true&configure%5BuserToken%5D=anonymous-47d5e0a9-5767-4efa-8707-eb7c86891fe4&configure%5BhitsPerPage%5D=10&query=' + keyword[0] + '&page='+str(i)+'&sortBy=ABC_production_all_latest&refinementList%5Bsite.title%5D%5B0%5D=ABC%20News'  # 검색어를 추가한 url
                print(keyword[0])
                print('page'+str(i))
                i += 1
                driver.get(searchurl) #주소로 접속
                driver.implicitly_wait(5)
                time.sleep(2)

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                posts = soup.select('.desktop-row .card-layout__content--1j1us')
                #기사들 하나하나 돌면서 작성시간과 url 얻기
                for post in posts:
                    post_url = post.select_one('.link__link--1JC6x.screen-reader-only__sr-link-hint--a7iDz.link__show-visited--17mvm.link__show-focus--3Ny07.link__underline-none--3f8vH').get('href')
                    print(post_url)
                    post_post_dates = post.select_one('.typography__letter-spaced-sm--322vT')
                    post_dates = post_post_dates.text
                    try:
                        post_dates = datetime.strptime(post_dates, '%d/%b/%Y')
                    except:
                        post_dates = post_post_dates.get('datetime')
                        post_dates = post_dates.split('T')
                        post_dates = post_dates[0]
                        post_dates = datetime.strptime(post_dates, '%Y-%m-%d')
                    post_dates = post_dates.date()
                    pd_url = [post_url, post_dates]

                    if post_dates > second_date:
                        print('later than')
                        continue

                    if pd_url not in pds_urls:#중복 url이 없고
                        if post_dates < first_date:
                            print('earlier than 2021')
                            raise LoopBreak()
                        else:#기간 충족하면 리스트에 적재
                            pds_urls.append(pd_url)
                print(pds_urls)
        except LoopBreak:
            pass

        #모은 url들 돌면서 접속
        for url in pds_urls:
            with requests.Session() as session:
                seed_url = url[0]
                print(seed_url)
                resp = session.get(url=seed_url, headers=http_header)
                data = resp.text
                soupsoup = BeautifulSoup(data, "html.parser")

                #제목
                try:
                    title = soupsoup.select_one('._3ANn5 ._3I3Xh._2uBSR._10YQT._1lh6E').text
                except:
                    try:
                        title = soupsoup.select_one('._3sI2v ._3I3Xh._2uBSR._10YQT._1lh6E').text
                    except:
                        try:
                            title = soupsoup.select_one('.Narrative-headerTitle').text
                        except:
                            print('i have no clue')
                            continue
                print(title)
                if 'VIDEO:' in title: #동영상 뉴스는 건너뜀
                    print('no video')
                    continue

                #본문
                try:
                    content = soupsoup.select_one('.ZN39J').text
                    content = content.strip()
                except:
                    content = []
                #print(content)

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
                #print(model_kwargs)

                insert_news_search_post(conn=conn, model_kwargs=model_kwargs)
        conn.close()

abcnews()
