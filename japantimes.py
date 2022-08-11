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

def japantimes():
    model_kwargs = {
        'source_name': 'japantimes',
        'biz_kind': 'news',
        'country': 'Japan',
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
    wordlist3 = [['korean music', '공통'], ['k+pop', '공통'], ['korean film', '공통'],
                 ['korean movie', '공통'], ['korean tv', '공통'], ['korean drama', '공통'], ['korean variety', '공통'],
                 ['korean food', '공통'], ['korean beauty', '공통'], ['korean cosmetic', '공통'],
                 ['squid game', '공통'], ['dalgona', '공통']]
    print(wordlist3)

    for keyword in wordlist3:#키워드별 검색
        pds_urls = []
        try:
            i = 0
            searchurl = 'https://www.nst.com.my/search?keywords=' + keyword[0] # 검색어를 추가한 url
            print(keyword[0])
            driver.get(searchurl)
            driver.implicitly_wait(5)
            time.sleep(2)
            while True:
                # sort = driver.find_element_by_class_name('gsc-selected-option-container')
                # driver.execute_script("arguments[0].click();", sort)
                # time.sleep(1)
                # sort_date = driver.find_element_by_css_selector('div > div > div > div.gsc-above-wrapper-area > table > tbody > tr > td.gsc-orderby-container > div > div.gsc-option-menu-container.gsc-inline-block > div.gsc-option-menu > div:nth-child(2) > div')
                # driver.execute_script("arguments[0].click();", sort_date)
                # driver.implicitly_wait(5)
                # time.sleep(1)

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                posts = soup.select('.gsc-result .gsc-thumbnail-inside .gs-title .gs-title')
                for post in posts:
                    #url
                    post_url = post.get('href')
                    print(post_url)

                    #작성일자
                    post_post_dates = post_url.split('/')
                    try:
                        post_dates = post_post_dates[4]+'/'+post_post_dates[5]+'/'+post_post_dates[6]
                        post_dates = datetime.strptime(post_dates, '%Y/%m/%d')
                    except:
                        try:
                            post_dates = post_post_dates[3]+'/'+post_post_dates[4]+'/'+post_post_dates[5]
                            post_dates = datetime.strptime(post_dates, '%Y/%m/%d')
                        except:
                            print('not a news')
                            continue
                    post_dates = post_dates.date()

                    pd_url = [post_url, post_dates]

                    if post_dates > second_date:
                        print('later than')
                        continue

                    if pd_url not in pds_urls:
                        if post_dates < first_date: #기준일보다 이르면 패스
                            print('earlier than')
                            continue
                            # raise LoopBreak()
                        else:
                            pds_urls.append(pd_url)
                print(pds_urls)

                if i > 9: #10페이지이면 마지막이니까 수집 그만
                    break
                #페이지 번호 클릭
                try:
                    pages = driver.find_elements_by_class_name('gsc-cursor .gsc-cursor-page')
                    driver.execute_script("arguments[0].click();", pages[i])
                    driver.implicitly_wait(5)
                    time.sleep(1)
                    print(i)
                    i += 1
                except:
                    break

        except LoopBreak:
            pass

        for url in pds_urls:
            with requests.Session() as session:
                seed_url = url[0]
                print(seed_url)
                resp = session.get(url=seed_url, headers=http_header)
                data = resp.text
                soupsoup = BeautifulSoup(data, "html.parser")

                #제목
                title = soupsoup.select_one('.padding_block.single-title h1').text
                print(title)
                #비디오는 스킵
                if 'VIDEO:' in title:
                    print('no video')
                    continue
                #본문
                try:
                    contents = soupsoup.select('.padding_block .entry p')
                    content = [t.text for t in contents]
                    content = " ".join(content)
                except:
                    content = []
                print(content)

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
    conn.close()

japantimes()
