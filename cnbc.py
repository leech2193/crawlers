from bs4 import BeautifulSoup
from datetime import datetime
from dbconnect import db_con, get_keyword, insert_product_post, insert_product_review
import uuid
import time
import re
from selenium import webdriver
import subprocess
import shutil
from dbconnect import db_con, get_keyword, insert_news_search_post

ignore = re.compile(
    '[\n\r\t\xa0\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U0001F90D-\U0001F9FF\u202f]')
def ignore_text(text):
    return ignore.sub(' ', text).strip()

model_kwargs = {
    'source_name': 'cnbcnews',
    'biz_kind': 'news',
    'country': 'USA',
    'methd': 'search',
    'category': 'article'
}

#검색 키워드
wordlist3 = [['korean', '공통'], ['korean music', '공통'], ['k pop', '공통'], ['korean film', '공통'], ['korean movie', '공통'], ['k movie', '공통'], ['korean tv', '공통'], ['korean drama', '공통'], ['korean variety', '공통'], ['k drama', '공통'], ['k variety', '공통'], ['k food', '공통'], ['korean food', '공통'], ['k beauty', '공통'], ['korean beauty', '공통'], ['korean cosmetic', '공통'], ['squid game', '공통'], ['dalgona', '공통']]
print(wordlist3)

def cnbc():
    conn = db_con()

    ## setup Driver|Chrome : 크롬드라이버를 사용하는 driver 생성
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)  # 크롬 드라이버를 사용하는 드라이버 생성
    driver.implicitly_wait(5)  ## 웹 자원을 3초 기다리기
    for word in wordlist3:
        print(word[0])
        #urllist = []  # url저장
        pageurl = 'https://www.cnbc.com/search/?query='+word[0]+'&qsearchterm=' + word[0]
        print(pageurl)
        driver.get(pageurl)  # 검색어를 이용한 검색 결과
        driver.implicitly_wait(5)
        time.sleep(5)

        #newest click
        newest = driver.find_element_by_css_selector('#sortdate')
        driver.execute_script("arguments[0].click();", newest)
        time.sleep(3)

        #기준날짜
        first_date = '2021/01/01'
        first_date = datetime.strptime(first_date, '%Y/%m/%d')
        first_date = first_date.date()

        # 기준날짜
        second_date = '2019/09/28'
        second_date = datetime.strptime(second_date, '%Y/%m/%d')
        second_date = second_date.date()

        # Get scroll height. 스크롤 길이 구하기
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            print('scroll')
            # Scroll down to bottom. 끝까지 스크롤하기
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(1)
            # Calculate new scroll height and compare with last scroll height. 스크롤 길이 새로 구하고 이전 스크롤 길이와 비교
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:  # 새 길이와 이전 스크롤 길이가 같다면, 검색 끝 이므로 break
                break
            last_height = new_height
            time.sleep(2)
            html = driver.page_source
            datesoup = BeautifulSoup(html, 'html.parser')  ## BeautifulSoup사용하기
            postdates = datesoup.select('.SearchResult-publishedDate')
            last_postdate = postdates[-1].text
            print(last_postdate)
            last_postdate = datetime.strptime(last_postdate, '%m/%d/%Y %I:%M:%S %p')
            last_postdate = last_postdate.date()
            if last_postdate < first_date:  # 2019년 이전 게시물의 경우 건너뜀
                print('skip before 2019')
                break


        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')  ## BeautifulSoup사용하기
        posts = soup.select('.SearchResult-searchResult.SearchResult-standardVariant')
        pds_urls = []
        for post in posts: #기사마다 돌면서
            #작성일자
            post_dates = post.select_one('.SearchResult-publishedDate').text
            post_dates = datetime.strptime(post_dates, '%m/%d/%Y %I:%M:%S %p')
            post_dates = post_dates.date()
            print(post_dates)

            #기사 url
            post_url = post.select_one('.SearchResult-searchResultTitle .resultlink').get('href')
            print(post_url)
            pd_url = []
            if 'video' in post_url:
                print('skip video')
                continue
            elif '/select/' in post_url:
                print('skip select')
                continue
            if post_dates < first_date:
                print('earlier than 2019')
                continue
            # if post_dates > second_date:
            #     print('이건 빼고')
            #     continue

            pd_url = [post_url, post_dates]
            if pd_url not in pds_urls:
                pds_urls.append(pd_url)

        print(pds_urls)

        for pdurl in pds_urls:
            url = pdurl[0]
            post_date = pdurl[1]
            print(url)
            print(post_date)
            driver.get(url)
            driver.implicitly_wait(5)
            time.sleep(1)
            cururl = driver.current_url
            if 'video' in cururl: #비디오 뺀다. url이 바뀌므로 다시 체크
                print('no video')
                continue

            html = driver.page_source
            sorrysoup = BeautifulSoup(html, 'html.parser')  ## BeautifulSoup사용하기
            try:
                sorry = sorrysoup.select_one('.TrendingNow-container').text
                if "sorry" in sorry:
                    continue
            except:
                None

            html = driver.page_source
            postsoup = BeautifulSoup(html, 'html.parser')  ## BeautifulSoup사용하기

            #제목
            try:
                post_title = postsoup.select_one('.ArticleHeader-headerContentContainer .ArticleHeader-headline').text
            except:
                try:
                    post_title = postsoup.select_one('.ArticleHeader-styles-makeit-wrapper--uJ7TO.ArticleHeader-styles-makeit-wrapperNoImage--kSnai .ArticleHeader-styles-makeit-headline--1DSjp').text
                except:
                    post_title = postsoup.select_one('.ArticleHeader-styles-acorns-headerContentContainer--3PwUb .ArticleHeader-styles-acorns-headline--1y2zZ').text
            print(post_title)

            #본문
            #postsoup = postsoup.select("div:not('.RelatedContent-container')")
            #post_contents = postsoup.find_all(class=".group")

            try:
                text_remove = postsoup.find(class_="RelatedContent-container")
                text_remove.clear()
                print('check this out')
            except:
                None
            post_contents = postsoup.select('.group p')
            # content_list = []
            # for body in post_contents:
            #     post_content = [t.text for t in body]
            #     content_list.append(post_content)
            content = [t.text for t in post_contents]
            content = " ".join(content)
            content = content.strip()
            print(content)
            print('-' * 100)
            # 뉴스 기사
            model_kwargs['data_id'] = str(uuid.uuid4()).replace('-', '')
            model_kwargs['keyword'] =word[0]
            model_kwargs['keyword_kr'] = word[1]
            model_kwargs['url'] = url
            model_kwargs['post_date'] = post_date
            model_kwargs['title'] = ignore_text(post_title)
            model_kwargs['content'] = ignore_text(content)
            model_kwargs['comment_count'] = None
            model_kwargs['dislike_count'] = None
            model_kwargs['view_count'] = None
            model_kwargs['vote'] = None
            model_kwargs['tag'] = None
            print(model_kwargs)

            insert_news_search_post(conn=conn, model_kwargs=model_kwargs)
            time.sleep(1)
    conn.close()

cnbc()