from bs4 import BeautifulSoup
from datetime import datetime
# from dbconnect import db_con, get_keyword, insert_product_post, insert_product_review
import uuid
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import re
from selenium import webdriver


ignore = re.compile('[\n\r\t\xa0\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U0001F90D-\U0001F9FF\u202f]')
def ignore_text(text):
	return ignore.sub(' ', text).strip()

def amazon_search(keyword_kr, keyword_eng, category2):
    model_kwargs = {
        'source_name': 'amazon',
        'biz_kind': 'post',
        #'country': 'USA'
        #'method': 'search',
    }
    # conn = db_con()

    #아마존 검색결과 -> 상품url 수집 -> url접속 후 상품 정보 수집 -> 리뷰 더보기url 접속 후 리뷰 수집

    ## setup Driver|Chrome : 크롬드라이버를 사용하는 driver 생성
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    user_agent = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"

    #헤더 1
    # chrome_options.add_argument('user-agent=' + user_agent)
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")

    #헤더2
    #chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36")

    #헤더3
    #chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
    driver = webdriver.Chrome('chromedriver', options=chrome_options)  # 크롬 드라이버를 사용하는 드라이버 생성
    driver.implicitly_wait(5)  ## 웹 자원을 3초 기다리기

    # try:
    #     shutil.rmtree(r"c:\chrometemp")  # 쿠키 / 캐쉬파일 삭제
    # except FileNotFoundError:
    #     pass
    # subprocess.Popen(
    #     r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"')  # 디버거 크롬 구동
    # option = Options()
    # option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
    # try:
    #     driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=option)
    # except:
    #     chromedriver_autoinstaller.install(True)
    #     driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=option)
    # driver.implicitly_wait(10)

    #키워드별 검색
    print(keyword_eng)
    #urllist = []  # url저장
    pageurl = 'https://www.amazon.com/s?k=' + keyword_eng
    print(pageurl)
    driver.get(pageurl)  # 검색어를 이용한 검색 결과
    driver.implicitly_wait(3)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')  ## BeautifulSoup사용하기

    #페이지 수
    page_num = soup.select('.a-disabled')
    if not page_num:
        page_num = soup.select('.s-pagination-disabled')
    print(page_num)
    try:
        page_num = page_num[-1]
        page_num = page_num.text
        page_num = page_num.strip()
    except:
        page_num = '1'
    if page_num.isdigit() == False:#끝 페이지가 나와있지 않다면?(5페이지 이하일 경우)
        page_num = soup.select('.a-normal')
        try:
            page_num = page_num[-1]
        except:
            None
        if not page_num:
            page_num = soup.select('.s-pagination-button')
            page_num = page_num[-2]
            print(page_num)
        print(page_num)
        page_num = page_num.text
        page_num = page_num.strip()
        if page_num.isdigit() == False:#그럼에도 불구하고 끝 페이지가 나와있지 않다면?(1페이지 이하)
            page_num = 1
        else:
            page_num = int(page_num)
    else:
        page_num = int(page_num)
    print(page_num)

    for t in range(1, page_num+1, 1):#페이지 별로
        print('page'+str(t))
        pageurl = 'https://www.amazon.com/s?k=' + keyword_eng + '&page=' + str(t)
        print(pageurl)
        driver.get(pageurl)  # 검색어를 이용한 검색 결과
        driver.implicitly_wait(3)
        time.sleep(1)

        # 페이지에 있는 제품들 url 수집
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')  ## BeautifulSoup사용하기

        try:
            err = soup.select_one('.a-box-inner').text
            if 'Enter the characters you see below' in err:
                print('oh no')
                break
        except:
            None

        products = soup.select('.s-main-slot .s-asin')  # .s-main-slot .sg-col-4-of-12')#. s-asin sg-col-4-of-16 sg-col sg-col-4-of-20
        urllist=[]
        for product in products:
            # 스폰서 제품 제외
            sponsored = product.select_one('.s-sponsored-label-text')
            if sponsored:
                print('skip sponsored')
                continue
            else:
                preurl = product.select_one('.a-size-mini .a-link-normal')  # .s-asin .a-size-mini .a-link-normal
                href = preurl.get('href')
                url = 'https://www.amazon.com' + href
                print(url)
                urllist.append(url)
        print(urllist)

        #url 돌면서 접속
        for url in urllist:
            try:
                driver.get(url)
            except:
                print('not working well')
                continue
            driver.implicitly_wait(3)
            time.sleep(1)

            #변수 초기화화
            kword = ''
            product_name2 = ''
            manufacture = ''
            categ = ''
            #url = ''
            review_num2 = ''
            rating = ''

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')  ## BeautifulSoup사용하기

            #상품명
            product = soup.findAll('span', {'class': 'a-size-large product-title-word-break'})
            if not product:
                print('not appropriate page')
                continue
            product_name = [t.text for t in product]
            product_name2 = " ".join(product_name)
            print('product name')
            product_name2 = product_name2.replace('\\n', '').strip()
            print(product_name2)

            #제조사
            manu = soup.select('.a-normal.a-spacing-micro .a-spacing-small')
            if manu:
                for man in manu:
                    if 'Brand' in man.text:
                        manufacture = man.text.strip()
                        manufacture = manufacture.replace('Brand', '').strip()
                    else:
                        continue
            else:
                manu = soup.findAll('a', {'id': 'bylineInfo'})
                manufact = [t.text for t in manu]
                manufacture = " ".join(manufact)
                manufacture = manufacture.replace('\\n', '').replace('Visit the ', '').replace('Store', '').strip()
                manufacture = manufacture.replace('Brand: ', '').strip()
            print('manufacturer')
            print(manufacture)

            #카테고리
            cat = soup.findAll('a', {'class': 'a-link-normal a-color-tertiary'})
            categ = [t.text for t in cat]
            categ = ">".join(categ)
            categ = categ.replace('\n', '').strip()
            categ = re.sub(' +', ' ', categ)
            print('category')
            #print(type(categ))
            print(categ)

            #url
            #print('url')
            #print(url)
            # #평점 수
            # rating_num = soup.findAll('span', {'id': 'acrCustomerReviewText'})
            # rating_num = [t.text for t in rating_num]
            # if rating_num:
            #     rating_num = rating_num[0]
            #     rating_num = rating_num.replace(' ratings', '').replace(',','').strip()
            #     rating_num = int(rating_num)
            #     print('rating num')
            #     print(type(rating_num))
            #     print(rating_num)

            #평점
            rating = soup.findAll('span', {'class': 'a-size-base a-nowrap'})
            rating = [t.text for t in rating]
            if rating:
                rating = rating[0]
                rating = rating.replace(' out of 5', '').strip()
                rating = float(rating)
                #print(type(rating))
                print(rating)
            if rating == []:
                rating = None

            #리뷰 더보기 링크 구하기
            prereview_url = soup.find('a', {'class': 'a-link-emphasis a-text-bold'})
            #print(prereview_url)
            #for link in prereview_url:
            if not prereview_url:#리뷰가 없다면
                print('no review')
                kword = keyword_eng.replace('+', ' ').strip()
                time.sleep(2)
                data_id = str(uuid.uuid4()).replace('-', '')
                model_kwargs['data_id'] = data_id
                model_kwargs['keyword'] = kword
                # model_kwargs['biz_kind'] = data_id
                # model_kwargs['domain'] = data_id
                model_kwargs['title'] = ignore_text(product_name2)
                model_kwargs['manufacturer'] = ignore_text(manufacture)
                model_kwargs['category'] = ignore_text(category2)
                model_kwargs['prod_category'] = ignore_text(categ)
                model_kwargs['url'] = url
                model_kwargs['review_count'] = 0
                model_kwargs['rating'] = rating
                model_kwargs['content'] = None
                print(model_kwargs)
                #df = df.append(model_kwargs, ignore_index=True)
                insert_post = insert_product_post(conn=conn, model_kwargs=model_kwargs)
                if insert_post == 'exclude':
                    print('exclude content')
                    print('post done' + '-' * 100)
                    time.sleep(5)
                    continue
                elif insert_post == 'dup':
                    print('duplicate content')
                    print('post done' + '-' * 100)
                    time.sleep(20)
                    continue
                print('post done' + '-' * 100)
                time.sleep(3)
                continue


            reviewhref = prereview_url.get('href')  # 링크 구하기
            review_url = 'https://www.amazon.com' + reviewhref
            #print(review_url)

            #리뷰 첫 페이지에 들어가서 전체 리뷰 수 구하기
            driver.get(review_url)
            driver.implicitly_wait(5)
            reviewnumhtml = driver.page_source
            reviewnumsoup = BeautifulSoup(reviewnumhtml, 'html.parser')  ## BeautifulSoup사용하기
            review_num = reviewnumsoup.select_one('.a-spacing-medium .a-spacing-base').text
            review_num = review_num.split(', ')
            #print(review_num)
            review_num2 = review_num[1]
            review_num2 = review_num2.replace('with reviews', '').replace(' ', '').replace(',', '').strip()
            review_num2 = int(review_num2)
            #print(review_num2)

            kword = keyword_eng.replace('+', ' ').strip()
            #time.sleep(2)
            data_id = str(uuid.uuid4()).replace('-','')
            model_kwargs['data_id'] = data_id
            model_kwargs['keyword'] = kword
            #model_kwargs['biz_kind'] = data_id
            #model_kwargs['domain'] = data_id
            model_kwargs['title'] = ignore_text(product_name2)
            model_kwargs['manufacturer'] = ignore_text(manufacture)
            model_kwargs['category'] = ignore_text(category2)
            model_kwargs['prod_category'] = ignore_text(categ)
            model_kwargs['url'] = url
            model_kwargs['review_count'] = review_num2
            model_kwargs['rating'] = rating
            model_kwargs['content'] = None
            print(model_kwargs)
            #df = df.append(model_kwargs, ignore_index=True)
            insert_post = insert_product_post(conn=conn, model_kwargs=model_kwargs)
            if insert_post == 'exclude':
                print('exclude content')
                print('post done' + '-' * 100)
                time.sleep(5)
                continue
            elif insert_post == 'dup':
                print('duplicate content')
                print('post done' + '-' * 100)
                time.sleep(20)
                continue
            print('post done'+ '-'*100)

            review_page = int(review_num2 / 10) + 2 #리뷰 페이지 구하기
            reviewtest = 0 #리뷰 숫자 구하기
            #리뷰 하나씩 수집
            r = 1
            for p in range(1, review_page, 1):
                review_url2 = review_url + '&pageNumber=' + str(p)
                driver.get(review_url2)
                driver.implicitly_wait(5)

                reviewhtml = driver.page_source
                reviewsoup = BeautifulSoup(reviewhtml, 'html.parser')  ## BeautifulSoup사용하기

                reviews = reviewsoup.select('.review-views .review')
                for review in reviews:
                    writer = ''
                    texts = ''
                    helpful = ''
                    #postdate = ''
                    stars = ''
                    place = ''
                    #작성자
                    writer = review.select_one('.a-profile-name').text

                    try: #helpful 수 구하기
                        helpful = review.select_one('.cr-vote-text').text
                        helpful = helpful.replace('people found this helpful', '')
                        helpful = int(helpful)
                    except:
                        helpful = 0

                    #리뷰 본문
                    texts = review.select_one('.review-text-content').text
                    texts = texts.replace('Your browser does not support HTML5 video.', '').strip()

                    postdate_place = review.select_one('.review-date').text #날짜, 장소가 들어있는 텍스트

                    #리뷰 작성일자 구하기
                    if 'Reviewed in' in postdate_place:
                        postdate_place = postdate_place.split('on')
                        #print(postdate_place)
                        postdate = postdate_place[1]
                        postdate = postdate.replace(',', '').strip()
                        #place = postdate.replace()
                    postdate = datetime.strptime(postdate, '%B %d %Y')
                    postdate = postdate.date()

                    #별점 구하기
                    stars = review.select_one('.review-rating').text
                    stars = stars.replace('out of 5 stars', '').strip()
                    stars = float(stars)

                    #작성국가 구하기
                    preplace = postdate_place[0] #reviewsoup.select_one('.review-views .a-spacing-medium').text#다시 할 것
                    preplace = preplace[12:]
                    preplace = preplace.replace('Reviewed ', '').replace('the ', '').strip()
                    place = preplace.replace('From ', '').strip()

                    rev_url = review_url2 + '#' + str(r)
                    r+=1
                    comment_id = str(uuid.uuid4()).replace('-', '')
                    model_kwargs['data_id'] = data_id
                    model_kwargs['comment_id'] = comment_id
                    model_kwargs['writer'] = ignore_text(writer)
                    model_kwargs['content'] = ignore_text(texts)
                    model_kwargs['like_count'] = helpful
                    model_kwargs['post_date'] = postdate
                    model_kwargs['star_point'] = stars
                    model_kwargs['country'] = place
                    model_kwargs['url'] = rev_url

                    first_date = '2021/11/01'
                    first_date = datetime.strptime(first_date, '%Y/%m/%d')
                    first_date = first_date.date()

                    if postdate < first_date:
                        print('before 2021')
                        continue

                    #df2 = df2.append(model_kwargs, ignore_index=True)

                    # print(type(data_id))
                    # print(type(comment_id))
                    # print(type(writer))
                    # print(type(texts))
                    # print(type(helpful))
                    # print(type(postdate))
                    # print(type(stars))
                    # print(type(place))
                    print(model_kwargs)
                    insert_product_review(conn=conn, model_kwargs=model_kwargs)

                    print(ignore_text(writer))
                    print(helpful)
                    print(ignore_text(texts))
                    print(postdate)
                    print(stars)
                    print(place)
                    reviewtest += 1
                    print(reviewtest)
                    print('-'*100)
                print('page'+str(p)+'done')
                if p > 501:
                    print('no more than 5000 reviews')
                    time.sleep(15)
                    break
                time.sleep(5)
    conn.close()
    print('done')
    driver.close()

amazon_search(None, "JungSaemMool", 'COSMETIC')
# amazon_search(None, "Goodal", 'COSMETIC')