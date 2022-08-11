import time
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from dbconnect import db_con, insert_news_search_post
import uuid
from selenium import webdriver
import re
import json

class LoopBreak(Exception):
    pass

ignore = re.compile(
    '[\n\r\t\xa0\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U0001F90D-\U0001F9FF\u202f]')
def ignore_text(text):
    return ignore.sub(' ', text).strip()

def globaltimes():
    model_kwargs = {
        'source_name': 'globaltimes',
        'biz_kind': 'news',
        'country': 'China',
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
    # # chrome_options.add_argument("--headless")
    # driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)  # 크롬 드라이버를 사용하는 드라이버 생성
    # driver.implicitly_wait(5)  ## 웹 자원을 3초 기다리기

    #검색 키워드 ['korean', '공통'],
    wordlist3 = [['korean music', '공통'], ['k pop', '공통'], ['korean film', '공통'],
                 ['korean movie', '공통'], ['korean tv', '공통'], ['korean drama', '공통'],
                 ['korean variety', '공통'],  ['korean food', '공통'], ['korean beauty', '공통'], ['korean cosmetic', '공통'],
                 ['squid game', '공통'], ['dalgona', '공통']]
    print(wordlist3)

    for keyword in wordlist3:#키워드별 검색
        try:
            with requests.Session() as session:
                pds_urls = []
                page = 1
                while True:
                    seed_url = 'https://search.globaltimes.cn/QuickSearchCtrl?page_no='+str(page)+'&search_txt='+keyword[0]
                    print(keyword[0])
                    print(page)
                    resp = session.get(url=seed_url, headers=http_header)
                    soupsoup = BeautifulSoup(resp.text, 'html.parser')
                    #print(soupsoup)
                    # html = driver.page_source
                    # soupsoup = BeautifulSoup(html, "html.parser")
                    posts = soupsoup.select('.span9')
                    post_num = 0
                    for post in posts:
                        #url
                        url = post.find('a', {'target': '_blank'})['href']
                        print(url)
                        #작성일자
                        post_date = post.find('small').text.strip()
                        post_date = post_date.split('Source')[0].strip()
                        print(post_date)
                        post_date = datetime.strptime(post_date, '%Y/%m/%d')
                        post_date = post_date.date()
                        print(post_date)
                        pd_url = [url, post_date]

                        if post_date > second_date:
                            print('later than')
                            continue

                        if url not in pds_urls:
                            if post_date < first_date:#기준일보다 이르면 수집 그만
                                print('earlier than')
                                raise LoopBreak()
                            else:
                                pds_urls.append(pd_url)
                        post_num+=1
                    if post_num < 10:#기사가 10개 미만이면 마지막페이지이므로 수집 그만
                        print('less then 10 posts')
                        raise LoopBreak()
                    # element1 = driver.find_element_by_css_selector('body > div.row-fluid.body-fluid > div.container-fluid.row-content > div:nth-child(12) > a:nth-child(11)')
                    # driver.execute_script("arguments[0].click();", element1)
                    # driver.implicitly_wait(5)
                    page += 1
                    time.sleep(1)
        except LoopBreak:
            pass
        print(pds_urls)
        for url in pds_urls:
            with requests.Session() as session:
                seed_url = url[0]
                print(seed_url)
                resp = session.get(url=seed_url, headers=http_header)
                data = resp.text
                soupsoup = BeautifulSoup(data, "html.parser")
                #제목
                title = soupsoup.select_one('.article_top .article_title').text.strip()
                #본문
                content = soupsoup.select_one('.article_content .article_right').text.strip()

                postdate = url[1]

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

    conn.close()

globaltimes()
