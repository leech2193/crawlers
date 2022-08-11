from datetime import datetime
from bs4 import BeautifulSoup
from pprint import pprint
import requests
import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from  dbconnect import insert_sns_post, db_con, get_keyword, insert_news_search_post
import uuid


def nbcnews():

    model_kwargs = {
            'source_name': 'nbcnews',
            'biz_kind': 'news',
            'country': 'USA',
            'methd': 'search',
            'category': 'article'
        }
    conn = db_con()

    #검색 키워드
    #아래와 같이 db에서 가지고 오거나, 리스트를 만들어 이용
    #wordlist = get_keyword(conn=conn, source_name='foxnews')

    wordlist2 = ['squid game', 'dalgona', 'BTS', 'korean music', 'k pop', 'korean film',
                 'korean movie', 'korean tv', 'korean drama', 'korean variety',
                 'korean food', 'korean beauty', 'korean cosmetic']
    keyword_kr = '공통'

    first_date = '2021/11/01'
    first_date = datetime.strptime(first_date, '%Y/%m/%d')
    first_date = first_date.date()

    second_date = '2021/11/30'
    second_date = datetime.strptime(second_date, '%Y/%m/%d')
    second_date = second_date.date()

    wordlist3 = []

    for kword in wordlist2:
        print(kword)
        kword = kword.replace(' ', '+').strip()
        wordlist3.append((kword))
    print(wordlist3)

    ## setup Driver|Chrome : 크롬드라이버를 사용하는 driver 생성
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)#크롬 드라이버를 사용하는 드라이버 생성
    driver.implicitly_wait(3) ## 웹 자원을 3초 기다리기

    for q in wordlist3:#키워드별 검색
        searchurl = 'https://www.nbcnews.com/search/?q='+q #검색어를 추가한 url
        driver.get(searchurl) #검색어를 이용한 검색 결과
        time.sleep(2)

        for n in range(1, 11, 1):#검색결과 각 페이지 별 기사 표시(총 10페이지)
            try:
                element1 = driver.find_element_by_css_selector("#" + '___gcse_0 > div > div > div > div.gsc-wrapper > div.gsc-resultsbox-visible > div > div > div.gsc-cursor-box.gs-bidi-start-align > div > div:nth-child(' + str(n) + ')')
                driver.execute_script("arguments[0].click();", element1)
            except: #페이지가 1페이지에서 끝나는 경우, 페이지 클릭이 불가능한 경우, 건너뛰기
                break
            driver.implicitly_wait(5)
            htmlset = driver.page_source  ## 페이지의 elements모두 가져오기
            soupsoup = BeautifulSoup(htmlset, 'html.parser')  ## BeautifulSoup사용하기
            address = soupsoup.select('div.gs-webResult.gs-result > div.gsc-thumbnail-inside > div > a')  # 주소

            for i in range(1,11,1): #페이지의 각 기사들 클릭 후 데이터 수집(페이지당 기사 10개)
                # 변수 초기화
                url = ''
                key = ''
                writedate = ''
                headtitle = ''
                articlebody2 = ''

                key = q#검색키워드
                key = key.replace('+', ' ').strip()
                print(key)

                #각 기사 클릭
                element2 = driver.find_element_by_css_selector("#" + '___gcse_0 > div > div > div > div.gsc-wrapper > div.gsc-resultsbox-visible > div > div > div.gsc-expansionArea > div:nth-child(' + str(i) + ') > div.gs-webResult.gs-result > div.gsc-thumbnail-inside > div > a')
                driver.execute_script("arguments[0].click();", element2)
                driver.implicitly_wait(5)

                #url
                url = address[i - 1].attrs['data-ctorig']
                print(url)

                if 'www.nbcnews.com/slideshow' in url:  # 슬라이드쇼 뉴스라면
                    html = requests.get(url)
                    soup = BeautifulSoup(html.text, 'html.parser')
                    html.close()

                    #제목
                    head=soup.findAll('h1',{'class':'slideshow-lede__main-title js-article-headline'})
                    headtitle = [ t.text for t in head]
                    headtitle = " ".join(headtitle)
                    print(headtitle)

                    #본문#styles_container__aQhg_ slide slide--active slide__slideshow--active
                        #styles_container__aQhg_ slide slide__slideshow--active
                    body=soup.findAll('div',{'class':'slide__caption'})
                    articlebody = [t.text for t in body]
                    #pprint(articlebody)
                    articlebody2 = " ".join(articlebody)
                    print(articlebody2)
                    if not articlebody2:
                        body = soup.findAll('div', {'class': 'styles_container__aQhg_ slide slide__slideshow--active'})
                        articlebody = [t.text for t in body]
                        # pprint(articlebody)
                        articlebody2 = " ".join(articlebody)

                    #작성일자
                    date=soup.findAll('time',{'class':'relative z-1'})
                    #date = date[0]['datetime']
                    writedate = [t.text for t in date]
                    writedate = " ".join(writedate)

                    writedate = writedate.replace('Updated ', '').strip()
                    writedate = writedate.replace('.', '').replace(',', '').replace('Sept', 'Sep').replace('March','Mar').replace('April', 'Apr').replace('June', 'Jun').replace('July', 'Jul').replace('UTC','').strip()
                    writedate = writedate[0:20]

                    writedate = writedate.replace(' 1 ',' 01 ').replace(' 2 ',' 02 ').replace(' 3 ',' 03 ').replace(' 4 ',' 04 ').replace(' 5 ',' 05 ').replace(' 6 ',' 06 ').replace(' 7 ',' 07 ').replace(' 8 ',' 08 ').replace(' 9 ',' 09 ').strip()
                    writedate = writedate.replace('\xa0', '').replace('/', '').strip()
                    writedate = writedate.replace('Updated', '').strip()
                    writedate = datetime.strptime(writedate, '%b %d %Y')
                    writedate = writedate.date()
                    print(writedate)

                    if writedate < first_date:  # 2021년 이전 게시물의 경우 건너뜀
                        print('Skip before 2021')
                        # 열려있는 탭 끄기
                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue

                    print(second_date)
                    if writedate > second_date:  # 2021년 이전 게시물의 경우 건너뜀
                        print('Skip after 10')
                        # 열려있는 탭 끄기
                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue

                    # 뉴스 기사
                    model_kwargs['data_id'] = str(uuid.uuid4()).replace('-', '')
                    model_kwargs['keyword'] = key
                    model_kwargs['keyword_kr'] = keyword_kr
                    model_kwargs['url'] = url
                    model_kwargs['post_date'] = writedate
                    model_kwargs['title'] = headtitle
                    model_kwargs['content'] = articlebody2
                    model_kwargs['comment_count'] = None
                    model_kwargs['dislike_count'] = None
                    model_kwargs['view_count'] = None
                    model_kwargs['vote'] = None
                    model_kwargs['tag'] = None
                    model_kwargs['happy'] = None
                    model_kwargs['unmoved'] = None
                    model_kwargs['amused'] = None
                    model_kwargs['excited'] = None
                    model_kwargs['angry'] = None
                    model_kwargs['sad'] = None
                    model_kwargs['like_count'] = None

                    insert_news_search_post(conn=conn, model_kwargs=model_kwargs)

                    #열려있는 탭 끄기
                    time.sleep(2)
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(2)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                elif 'www.nbcnews.com/' in url:  # 일반 뉴스라면
                    html = requests.get(url)
                    soup = BeautifulSoup(html.text, 'html.parser')
                    html.close()
                    #제목
                    head=soup.findAll('h1',{'class':'article-hero-headline__htag'})#lh-none-print black-print  # f8 f9-m fw3 mb3 mt0 f10-xl founders-cond lh-none'})
                    if not head:
                        head = soup.findAll('h2', {'class': 'article-hero__headline'})
                    headtitle = [ t.text for t in head]
                    headtitle = " ".join(headtitle)
                    print(headtitle)

                    #본문
                    body=soup.findAll('div',{'class':'article-body__content'})
                    articlebody = [ t.text for t in body]
                    #pprint(articlebody)
                    articlebody2 = " ".join(articlebody)
                    print(articlebody2)

                    #작성일자
                    date=soup.findAll('time',{'class':'relative z-1'})
                    if not date:
                        print('video news skip')
                        # 열려있는 탭 끄기
                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue
                    writedate = [t.text for t in date]
                    writedate = " ".join(writedate)
                    writedate = writedate.replace('Updated', '').replace('\xa0', '').strip()
                    writedate = writedate.replace('.', '').replace(',', '').replace('Sept', 'Sep').replace('March','Mar').replace('April', 'Apr').replace('June', 'Jun').replace('July', 'Jul').replace('UTC','').strip()
                    writedate = writedate[0:11]
                    print(writedate)
                    writedate = writedate.replace(' 1 ',' 01 ').replace(' 2 ',' 02 ').replace(' 3 ',' 03 ').replace(' 4 ',' 04 ').replace(' 5 ',' 05 ').replace(' 6 ',' 06 ').replace(' 7 ',' 07 ').replace(' 8 ',' 08 ').replace(' 9 ',' 09 ').strip()
                    writedate = datetime.strptime(writedate, '%b %d %Y')
                    writedate = writedate.date()
                    print(writedate)

                    print(first_date)
                    if writedate < first_date:  # 2021년 이전 게시물의 경우 건너뜀
                        print('Skip before 2021')
                        # 열려있는 탭 끄기
                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue

                    print(second_date)
                    if writedate > second_date:  # 2021년 이전 게시물의 경우 건너뜀
                        print('Skip after 10')
                        # 열려있는 탭 끄기
                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue

                    # 뉴스 기사
                    model_kwargs['data_id'] = str(uuid.uuid4()).replace('-', '')
                    model_kwargs['keyword'] = key
                    model_kwargs['keyword_kr'] = keyword_kr
                    model_kwargs['url'] = url
                    model_kwargs['post_date'] = writedate
                    model_kwargs['title'] = headtitle
                    model_kwargs['content'] = articlebody2
                    model_kwargs['comment_count'] = None
                    model_kwargs['dislike_count'] = None
                    model_kwargs['view_count'] = None
                    model_kwargs['vote'] = None
                    model_kwargs['tag'] = None
                    model_kwargs['happy'] = None
                    model_kwargs['unmoved'] = None
                    model_kwargs['amused'] = None
                    model_kwargs['excited'] = None
                    model_kwargs['angry'] = None
                    model_kwargs['sad'] = None
                    model_kwargs['like_count'] = None

                    insert_news_search_post(conn=conn, model_kwargs=model_kwargs)

                    time.sleep(1)
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(1)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])


                elif 'www.today.com/' in url:  # today 뉴스라면
                    html = requests.get(url)
                    soup = BeautifulSoup(html.text, 'html.parser')
                    html.close()
                    #제목
                    head=soup.findAll('h1',{'class':'article-hero-headline__htag'})# f8 f9-m fw3 mb3 mt0 publico-hed lh-title'})
                    headtitle = [ t.text for t in head]
                    headtitle = " ".join(headtitle)
                    print(headtitle)

                    #본문
                    body=soup.findAll('div',{'class':'article-body__content'})
                    articlebody = [ t.text for t in body]
                    #pprint(articlebody)
                    articlebody2 = " ".join(articlebody)
                    print(articlebody2)

                    if not articlebody2:
                        body = soup.findAll('div', {'class': 'recipe-body__chefNotes'})
                        articlebody = [t.text for t in body]
                        # pprint(articlebody)
                        articlebody2 = " ".join(articlebody)
                        print(articlebody2)

                    #작성일자
                    date = soup.findAll('time', {'class': 'relative z-1'})
                    print('date')
                    print(date)
                    if not date:
                        print('video news skip')
                        # 열려있는 탭 끄기
                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue
                    print(date)
                    writedate = [t.text for t in date]
                    writedate = " ".join(writedate)
                    writedate = writedate.replace('.', '').replace(',', '').replace('Sept', 'Sep').replace('March','Mar').replace('April', 'Apr').replace('June', 'Jun').replace('July', 'Jul').replace('UTC', '').strip()
                    writedate = writedate[0:11]
                    print(writedate)
                    writedate = writedate.replace(' 1 ', ' 01 ').replace(' 2 ', ' 02 ').replace(' 3 ', ' 03 ').replace(' 4 ', ' 04 ').replace(' 5 ', ' 05 ').replace(' 6 ', ' 06 ').replace(' 7 ', ' 07 ').replace(' 8 ',' 08 ').replace(' 9 ', ' 09 ').strip()
                    writedate = datetime.strptime(writedate, '%b %d %Y')
                    writedate = writedate.date()
                    print(writedate)

                    print(first_date)
                    if writedate < first_date:  # 2021년 이전 게시물의 경우 건너뜀
                        print('Skip before 2021')
                        # 열려있는 탭 끄기
                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue

                    print(second_date)
                    if writedate > second_date:  # 2021년 이전 게시물의 경우 건너뜀
                        print('Skip after 10')
                        # 열려있는 탭 끄기
                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue

                    # 뉴스 기사
                    model_kwargs['data_id'] = str(uuid.uuid4()).replace('-', '')
                    model_kwargs['keyword'] = key
                    model_kwargs['keyword_kr'] = keyword_kr
                    model_kwargs['url'] = url
                    model_kwargs['post_date'] = writedate
                    model_kwargs['title'] = headtitle
                    model_kwargs['content'] = articlebody2
                    model_kwargs['comment_count'] = None
                    model_kwargs['dislike_count'] = None
                    model_kwargs['view_count'] = None
                    model_kwargs['vote'] = None
                    model_kwargs['tag'] = None
                    model_kwargs['happy'] = None
                    model_kwargs['unmoved'] = None
                    model_kwargs['amused'] = None
                    model_kwargs['excited'] = None
                    model_kwargs['angry'] = None
                    model_kwargs['sad'] = None
                    model_kwargs['like_count'] = None

                    insert_news_search_post(conn=conn, model_kwargs=model_kwargs)

                    time.sleep(2)
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(2)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                else:
                    print('not news')
                    continue

    #브라우저 창 끄기
    driver.quit()

nbcnews()