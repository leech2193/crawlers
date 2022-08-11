from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from dbconnect import insert_sns_post, db_con, get_keyword, insert_news_search_post
import uuid
import time
import re

ignore = re.compile(
    '[\n\r\t\xa0\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U0001F90D-\U0001F9FF\u202f]')
def ignore_text(text):
    return ignore.sub(' ', text).strip()

first_date = '2021/01/01'
first_date = datetime.strptime(first_date, '%Y/%m/%d')
first_date = first_date.date()

# 기준날짜 2021년
second_date = '2021/11/30'
second_date = datetime.strptime(second_date, '%Y/%m/%d')
second_date = second_date.date()

http_header = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}
def jakartapost():
    ## setup Driver|Chrome : 크롬드라이버를 사용하는 driver 생성
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)  # 크롬 드라이버를 사용하는 드라이버 생성
    driver.implicitly_wait(5)  ## 웹 자원을 3초 기다리기

    model_kwargs = {
        'source_name': 'jakartapost',
        'biz_kind': 'news',
        'country': 'Indonesia',
        'methd': 'search',
        'category': 'article'
    }
    conn = db_con()

    #검색 키워드
    wordlist3 = [['korean+music', '공통'], ['k pop', '공통'], ['korean+film', '공통'],
                 ['korean+movie', '공통'], ['korean+tv', '공통'], ['korean+drama', '공통'],
                 ['korean+variety', '공통'],  ['korean+food', '공통'], ['korean+beauty', '공통'], ['korean+cosmetic', '공통'],
                 ['squid+game', '공통'], ['dalgona', '공통']]

    for keyword in wordlist3:#키워드별 검색
        for page in range(1, 11, 1):
            searchurl = 'https://www.thejakartapost.com/search?q='+keyword[0]+'#gsc.tab=0&gsc.q='+keyword[0]+'&gsc.page='+str(page)  # 검색어를 추가한 url
            driver.get(searchurl)  # 검색어를 이용한 검색 결과
            driver.implicitly_wait(5)
            time.sleep(5)
            print(page)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            urls = soup.select('.gsc-webResult.gsc-result .gs-webResult.gs-result .gsc-thumbnail-inside .gs-title .gs-title')
            urllist = []
            for url in urls:
                #url
                purl = url.get('href')
                #이상한거 거름
                if '/tag/' in purl:
                    print('no tag')
                    continue
                elif '/hashtag/' in purl:
                    print('no hashtag')
                    continue
                print(purl)
                test2 = purl.split("/")
                #작성일자
                try:
                    post_date = test2[4]+'/'+test2[5]+'/'+test2[6]
                except IndexError:
                    print('not a news')
                    continue
                try:
                    post_date = datetime.strptime(post_date, '%Y/%m/%d')
                except:
                    print('not a news too')
                    continue
                post_date = post_date.date()

                post = []

                print(post_date)

                if post_date > second_date:
                    print('later than')
                    continue

                if post_date < first_date:
                    print('skip before 2021')
                    break

                if purl not in urllist:
                    if '/tag/' in url:
                        continue
                    else:
                        post.append(purl)
                        post.append(post_date)
                    urllist.append(post)

            print(urllist)

            for url in urllist:
                driver.get(url[0])
                driver.implicitly_wait(5)
                time.sleep(2)

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                postdate = url[1]
                #기사아닌것 거름
                try:
                    text_remove = soup.find('div', {'class': "setMDetail"})
                    text_remove.clear()
                    print('check this out')
                except:
                    None
                try:
                    text_remove = soup.find('div', {'class': 'singlePagePremiumGate'})
                    text_remove.clear()
                    print('check this out2')
                except:
                    None
                try:
                    text_remove = soup.find('div', {'class': 'topicRelated'})
                    text_remove.clear()
                    print('check this out3')
                except:
                    None
                try:
                    text_remove = soup.find('div', {'class': 'col-xs-12 no-padding tagSingle'})
                    text_remove.clear()
                    print('check this out4')
                except:
                    None
                try:
                    text_remove = soup.find('div', {'class': 'col-xs-12 singleread'})
                    text_remove.clear()
                    print('check this out5')
                except:
                    None
                #제목
                title = soup.select_one('.title-large').text
                #본문
                content = soup.select_one('.col-md-10.col-xs-12.detailNews')
                #print(content)
                try:
                    content = content.text
                except:
                    content = soup.select_one('.col-xs-12.tjp-detail-news')
                    content = content.text
                content = content.strip()

                if postdate < first_date:  # 기준일 이전 게시물의 경우 건너뜀
                    print('skip before')
                    continue

                print(url[0])
                print(title)
                print(postdate)
                print(content)
                print('-'*100)

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
jakartapost()
