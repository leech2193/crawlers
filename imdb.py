import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
from dbconnect import db_con, get_keyword, insert_content_review
import uuid
from selenium import webdriver
from datetime import datetime, timedelta
import re

class LoopBreak(Exception):
    pass

ignore = re.compile(
    '[\n\r\t\xa0\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U0001F90D-\U0001F9FF\u202f]')
def ignore_text(text):
    return ignore.sub(' ', text).strip()

def imdb():
    model_kwargs = {
        'source_name': 'imdb',
        'biz_kind': 'review',
        #'methd': 'search'
    }
    conn = db_con()


    ## setup Driver|Chrome : 크롬드라이버를 사용하는 driver 생성
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)  # 크롬 드라이버를 사용하는 드라이버 생성
    driver.implicitly_wait(5)  ## 웹 자원을 3초 기다리기

    #한류일 경우 1)을 사용, 글로벌일 경우 1) 주석 처리 후 2) 사용

    #urllist = [["D.P.", "https://www.imdb.com/title/tt13024974/reviews?sort=submissionDate&dir=desc&ratingFilter=0"]]

    # urllist = [["Parasite", "https://www.imdb.com/title/tt6751668/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Introduction", "https://www.imdb.com/title/tt14035108/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["midnight", "https://www.imdb.com/title/tt14757872/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["double patty 2021", "https://www.imdb.com/title/tt14493552/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["MY BIG MAMA'S CRAZY RIDE", "https://www.imdb.com/title/tt13972688/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["mission possible", "https://www.imdb.com/title/tt14140954/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Burning", "https://www.imdb.com/title/tt7282468/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Exit", "https://www.imdb.com/title/tt10648440/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["New Year Blues", "https://www.imdb.com/title/tt13893464/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Endless Rain", "https://www.imdb.com/title/tt14540764/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["intruder ", "https://www.imdb.com/title/tt12491064/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Miss & Mrs. Cops", "https://www.imdb.com/title/tt10161238/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["recalled", "https://www.imdb.com/title/tt14527836/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["slate", "https://www.imdb.com/title/tt13576808/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Sweet & Sour ", "https://www.imdb.com/title/tt14599938/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["What Happened to Mr. Cha", "https://www.imdb.com/title/tt13667212/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["pipeline  ", "https://www.imdb.com/title/tt14716932/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Minari", "https://www.imdb.com/title/tt10633456/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Space Sweepers", "https://www.imdb.com/title/tt12838766/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Seobok", "https://www.imdb.com/title/tt13316722/reviews/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Aloners", "https://www.imdb.com/title/tt14598598/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Escape from Mogadishu", "https://www.imdb.com/title/tt14810692/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Sinkhole", "https://www.imdb.com/title/tt12664618/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Hostage: Missing Celebrity", "https://www.imdb.com/title/tt14941222/reviews?sort=submissionDate&dir=desc&ratingFilter=0"]]
    # urllist = [["She Would Never Know","https://www.imdb.com/title/tt13446244/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["One The Woman","https://www.imdb.com/title/tt15007114/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Here's My Plan","https://www.imdb.com/title/tt14461244/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["RUN ON","https://www.imdb.com/title/tt13271834/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Times OCN","https://www.imdb.com/title/tt13800344/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["W: Two Worlds Apart","https://www.imdb.com/title/tt5797194/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Police University","https://www.imdb.com/title/tt14518136/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Love Scene Number","https://www.imdb.com/title/tt13927228/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Sweet Home","https://www.imdb.com/title/tt11612120/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["At a Distance Spring Is Green","https://www.imdb.com/title/tt14518430/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Legend of the Blue Sea","https://www.imdb.com/title/tt5766194/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["High Class","https://www.imdb.com/title/tt14596714/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["True Beauty","https://www.imdb.com/title/tt13274038/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Nevertheless","https://www.imdb.com/title/tt14518284/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["law school","https://www.imdb.com/title/tt13885336/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Lovers of the Red Sky","https://www.imdb.com/title/tt13776460/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["sky castle","https://www.imdb.com/title/tt9151274/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Hello Me!","https://www.imdb.com/title/tt13670090/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["youth of may","https://www.imdb.com/title/tt14166666/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["You Are My Spring","https://www.imdb.com/title/tt14169816/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["LOST","https://www.imdb.com/title/tt14609588/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Mine","https://www.imdb.com/title/tt14023192/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Mouse","https://www.imdb.com/title/tt13634792/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Mr.Queen","https://www.imdb.com/title/tt13400006/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["PENTHOUSE","https://www.imdb.com/title/tt13067118/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Voice","https://www.imdb.com/title/tt6212854/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Doom at Your Service","https://www.imdb.com/title/tt13669128/reviews/?ref_=nv_sr_srsg_0"],
    #         ["Hometown","https://www.imdb.com/title/tt14687370/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Dark Hole","https://www.imdb.com/title/tt13885376/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Beyond Evil","https://www.imdb.com/title/tt13634872/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["HOSPITAL PLAYLIST","https://www.imdb.com/title/tt11769304/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["The Veil","https://www.imdb.com/title/tt14482296/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["L.U.C.A.: The Beginning","https://www.imdb.com/title/tt13752928/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Racket Boys","https://www.imdb.com/title/tt14482414/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["The Witch's Diner","https://www.imdb.com/title/tt14596486/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Love(ft. Marriage and Divorce)","https://www.imdb.com/title/tt13814840/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Move to Heaven","https://www.imdb.com/title/tt11052470/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Taxi Driver","https://www.imdb.com/title/tt13759970/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Mad for Each Other","https://www.imdb.com/title/tt14596414/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Phoenix 2020","https://www.imdb.com/title/tt14433228/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Undercover","https://www.imdb.com/title/tt12940504/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["The Devil Judge","https://www.imdb.com/title/tt14169770/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Love Alarm","https://www.imdb.com/title/tt9145880/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["River Where the Moon Rises","https://www.imdb.com/title/tt13634686/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Hometown ChaChaCha","https://www.imdb.com/title/tt14518756/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Yumi's Cells","https://www.imdb.com/title/tt14596630/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Oh My Venus","https://www.imdb.com/title/tt5189944/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Descendants of the Sun","https://www.imdb.com/title/tt4925000/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["MASTER'S SUN","https://www.imdb.com/title/tt3184674/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Vincenzo","https://www.imdb.com/title/tt13433812/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["HUSH","https://www.imdb.com/title/tt13273670/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Monthly Magazine Home","https://www.imdb.com/title/tt13885272/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Revolutionary Sisters","https://www.imdb.com/title/tt14223138/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Imitation","https://www.imdb.com/title/tt14371376/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Itaewon Class","https://www.imdb.com/title/tt11239552/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Amor Fati","https://www.imdb.com/title/tt14386466/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Delayed Justice","https://www.imdb.com/title/tt13269814/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["On the Verge of Insanity","https://www.imdb.com/title/tt14408332/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["My Roommate is a Gumiho","https://www.imdb.com/title/tt13777028/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Hwarang","https://www.imdb.com/title/tt5646594/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Kingdom: Ashin of the North","https://www.imdb.com/title/tt13412252/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Scarlet Heart Ryeo","https://www.imdb.com/title/tt5320412/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Navillera","https://www.imdb.com/title/tt13885302/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Weightlifting Fairy Kim Bok-joo","https://www.imdb.com/title/tt6157148/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Extracurricular","https://www.imdb.com/title/tt10262630/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["SISYPHUS THE MYTH","https://www.imdb.com/title/tt13715448/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Oh My Lady Lord","https://www.imdb.com/title/tt13715346/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Bossam: Steal the Fate","https://www.imdb.com/title/tt13928294/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Sell Your Haunted House","https://www.imdb.com/title/tt14223310/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["While You Were Sleeping","https://www.imdb.com/title/tt6256484/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["Dal Ri and Gamjatang","https://www.imdb.com/title/tt14730768/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #         ["dodosolsollalasol","https://www.imdb.com/title/tt12850262/reviews?sort=submissionDate&dir=desc&ratingFilter=0"]]
    # urllist = [["18 Again", "https://www.imdb.com/title/tt12846096/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["More Than Friends", "https://www.imdb.com/title/tt12879170/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Kkondae Intern", "https://www.imdb.com/title/tt12511316/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Tomorrow, with You", "https://www.imdb.com/title/tt5994346/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["The Sweet Blood", "https://www.imdb.com/title/tt14339838/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["The Road: The Tragedy of One", "https://www.imdb.com/title/tt14687098/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["The Package", "https://www.imdb.com/title/tt6257658/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Live On", "https://www.imdb.com/title/tt13273946/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Familiar Wife", "https://www.imdb.com/title/tt8487786/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Extraordinary You", "https://www.imdb.com/title/tt10826102/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Next Door With J", "https://www.imdb.com/title/tt14912862/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Flower Boys next door", "https://www.imdb.com/title/tt2748124/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Cheese In the Trap", "https://www.imdb.com/title/tt4741110/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Kill it", "https://www.imdb.com/title/tt9772814/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Legend of the Blue Sea", "https://www.imdb.com/title/tt5766194/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Peach of Time", "https://www.imdb.com/title/tt15270030/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["The Bride of Habaek", "https://www.imdb.com/title/tt6385752/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Hotel Del Luna", "https://www.imdb.com/title/tt10220588/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["MOOD OF THE DAY", "https://www.imdb.com/title/tt5586914/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["THE CLASSIFIED FILE", "https://www.imdb.com/title/tt4791594/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["THE ODD FAMILY ZOMBIES ON SALE", "https://www.imdb.com/title/tt9765144/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["THE SWINDLERS", "https://www.imdb.com/title/tt7243686/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Less Than Evil", "https://www.imdb.com/title/tt9143820/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Bad Guys: City of Evil", "https://www.imdb.com/title/tt12404980/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["THE FORTRESS", "https://www.imdb.com/title/tt7160176/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Angel's Last Mission : Love", "https://www.imdb.com/title/tt10160592/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["WARRIORS OF THE DAWN", "https://www.imdb.com/title/tt6010020/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["ROAD KILL", "https://www.imdb.com/title/tt10396028/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Long Live The King", "https://www.imdb.com/title/tt10446722/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["FENGSHUI", "https://www.imdb.com/title/tt7046524/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["MUSUDAN", "https://www.imdb.com/title/tt5447140/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["THE AGE OF SHADOWS", "https://www.imdb.com/title/tt4914580/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Bad Papa", "https://www.imdb.com/title/tt8907470/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["TRAIN TO BUSAN", "https://www.imdb.com/title/tt5700672/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Do You Like Brahms?", "https://www.imdb.com/title/tt12867750/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Saimdang: Memoir of Colors", "https://www.imdb.com/title/tt5220316/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["MEMOIR OF A MURDERER", "https://www.imdb.com/title/tt5729348/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Hide and Seek", "https://www.imdb.com/title/tt3155654/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["SKY CASTLE1", "https://www.imdb.com/title/tt9151274/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Love In Sadness", "https://www.imdb.com/title/tt9829586/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Signal", "https://www.imdb.com/title/tt5332206/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["A Pledge to God", "https://www.imdb.com/title/tt9257510/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Gentleman's Dignity", "https://www.imdb.com/title/tt2362760/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Flower of Evil", "https://www.imdb.com/title/tt11691684/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["THE AGE OF BLOOD", "https://www.imdb.com/title/tt8081830/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["At Eighteen", "https://www.imdb.com/title/tt10474124/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Graceful Friends", "https://www.imdb.com/title/tt12531492/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Reply 1994", "https://www.imdb.com/title/tt3357586/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Because This is My First Life", "https://www.imdb.com/title/tt7278588/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Goodbye to goodbye", "https://www.imdb.com/title/tt8409646/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["THE STAR NEXT DOOR", "https://www.imdb.com/title/tt8661098/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Please Don't Meet / Date Him", "https://www.imdb.com/title/tt13394428/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["SECRET OF THE LIVING DEAD", "https://www.imdb.com/title/tt7108976/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["THE HUNTRESSES", "https://www.imdb.com/title/tt3530418/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["KAIROS", "https://www.imdb.com/title/tt12874950/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["THE PRISON", "https://www.imdb.com/title/tt6589464/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["HOWLING", "https://www.imdb.com/title/tt2186819/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["SECRET ZOO", "https://www.imdb.com/title/tt11566164/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Must You Go？", "https://www.imdb.com/title/tt14137516/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Save Me 2", "https://www.imdb.com/title/tt7020532/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["To My Star (Movie)", "https://www.imdb.com/title/tt13788764/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["You Make Me Dance", "https://www.imdb.com/title/tt13911962/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Class of Lies", "https://www.imdb.com/title/tt10467640/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["The Cursed", "https://www.imdb.com/title/tt13086164/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Team Bulldog: Off-duty Investigation", "https://www.imdb.com/title/tt12379076/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Catch the Ghost", "https://www.imdb.com/title/tt10712926/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Breakup Probation, A Week", "https://www.imdb.com/title/tt14043128/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Confession", "https://www.imdb.com/title/tt2468774/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["Kill Me Heal Me", "https://www.imdb.com/title/tt4339192/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #             ["A Korean Odyssey", "https://www.imdb.com/title/tt7099334/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #            ["Hellbound", "https://www.imdb.com/title/tt12235718/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #            ["My Name", "https://www.imdb.com/title/tt12940504/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #            ["Dr.Brain", "https://www.imdb.com/title/tt15758760/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #            ["Happiness", "https://www.imdb.com/title/tt14979052/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #            ["The King's Affection", "https://www.imdb.com/title/tt14609428/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #            ["Now, We Are Breaking Up", "https://www.imdb.com/title/tt14408016/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #            ["Jirisan", "https://www.imdb.com/title/tt13400300/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #            ["Secret Royal Inspector Joy", "https://www.imdb.com/title/tt15181018/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #            ["The Red Sleeve", "https://www.imdb.com/title/tt14687200/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #            ["Reflection of You", "https://www.imdb.com/title/tt14684086/reviews?sort=submissionDate&dir=desc&ratingFilter=0"],
    #            ["Inspector Koo", "https://www.imdb.com/title/tt14731794/reviews?sort=submissionDate&dir=desc&ratingFilter=0"]]


    #global content
    # urllist = [['Fatale', 'https://www.imdb.com/title/tt8829830/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Our Friend', 'https://www.imdb.com/title/tt9608818/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Marksman', 'https://www.imdb.com/title/tt6902332/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Monster Hunter', 'https://www.imdb.com/title/tt6475714/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Little Things', 'https://www.imdb.com/title/tt10016180/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Wonder Woman 1984', 'https://www.imdb.com/title/tt7126948/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The War with Grandpa', 'https://www.imdb.com/title/tt4532038/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Croods: A New Age', 'https://www.imdb.com/title/tt2850386/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Promising Young Woman','https://www.imdb.com/title/tt9620292/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Land', 'https://www.imdb.com/title/tt10265034/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Nomadland', 'https://www.imdb.com/title/tt9770150/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Tom and Jerry', 'https://www.imdb.com/title/tt1361336/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Judas and the Black Messiah','https://www.imdb.com/title/tt9784798/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Nobody', 'https://www.imdb.com/title/tt7888964/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Boogie', 'https://www.imdb.com/title/tt10896398/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Courier', 'https://www.imdb.com/title/tt8368512/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Chaos Walking', 'https://www.imdb.com/title/tt2076822/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Raya and the Last Dragon','https://www.imdb.com/title/tt5109280/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Unholy', 'https://www.imdb.com/title/tt9419056/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['In the Earth', 'https://www.imdb.com/title/tt13429362/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Mortal Kombat', 'https://www.imdb.com/title/tt0293429/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Together Together', 'https://www.imdb.com/title/tt11285280/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Demon Slayer: Mugen Train','https://www.imdb.com/title/tt11032374/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Girl Who Believes in Miracles','https://www.imdb.com/title/tt9098454/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Spiral', 'https://www.imdb.com/title/tt10342730/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Cruella', 'https://www.imdb.com/title/tt3228774/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Dream Horse', 'https://www.imdb.com/title/tt9883996/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['World War Z', 'https://www.imdb.com/title/tt0816711/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Finding You', 'https://www.imdb.com/title/tt8760280/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Wrath of Man', 'https://www.imdb.com/title/tt11083552/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['A Quiet Place Part II','https://www.imdb.com/title/tt8332922/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Queen Bees', 'https://www.imdb.com/title/tt8338076/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Spirit Untamed', 'https://www.imdb.com/title/tt11084896/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['F9: The Fast Saga', 'https://www.imdb.com/title/tt5433138/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Werewolves Within', 'https://www.imdb.com/title/tt9288692/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ["Hitman's Wife's Bodyguard", 'https://www.imdb.com/title/tt8385148/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Peter Rabbit 2: The Runaway','https://www.imdb.com/title/tt8376234/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Old', 'https://www.imdb.com/title/tt10954652/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Stillwater', 'https://www.imdb.com/title/tt10696896/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Snake Eyes', 'https://www.imdb.com/title/tt8404256/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Black Widow', 'https://www.imdb.com/title/tt3480822/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Jungle Cruise', 'https://www.imdb.com/title/tt0870154/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Green Knight', 'https://www.imdb.com/title/tt9243804/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Forever Purge', 'https://www.imdb.com/title/tt10327252/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Boss Baby: Family Business','https://www.imdb.com/title/tt6932874/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Escape Room: Tournament of Champions','https://www.imdb.com/title/tt9844522/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Respect', 'https://www.imdb.com/title/tt2452150/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Candyman', 'https://www.imdb.com/title/tt9347730/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Free Guy', 'https://www.imdb.com/title/tt6264654/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Protege', 'https://www.imdb.com/title/tt6079772/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ["Don't Breathe 2", 'https://www.imdb.com/title/tt6246322/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Night House', 'https://www.imdb.com/title/tt9731534/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['PAW Patrol: The Movie', 'https://www.imdb.com/title/tt11832046/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Copshop', 'https://www.imdb.com/title/tt5748448/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Dear Evan Hansen', 'https://www.imdb.com/title/tt9357050/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Card Counter', 'https://www.imdb.com/title/tt11196036/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Eyes of Tammy Faye','https://www.imdb.com/title/tt9115530/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Shang-Chi and the Legend of the Ten Rings','https://www.imdb.com/title/tt9376612/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    # urllist = [['Dune', 'https://www.imdb.com/title/tt1160419/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Antlers', 'https://www.imdb.com/title/tt7740510/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['No Time to Die', 'https://www.imdb.com/title/tt2382320/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Halloween Kills', 'https://www.imdb.com/title/tt10665338/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ["Ron's Gone Wrong", 'https://www.imdb.com/title/tt7504818/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Last Night in Soho', 'https://www.imdb.com/title/tt9639470/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Addams Family 2','https://www.imdb.com/title/tt11125620/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The French Dispatch', 'https://www.imdb.com/title/tt8847712/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Venom: Let There Be Carnage','https://www.imdb.com/title/tt7097896/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ["My Hero Academia: World Heroes' Mission", 'https://www.imdb.com/title/tt13544716/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Encanto', 'https://www.imdb.com/title/tt2953050/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Eternals', 'https://www.imdb.com/title/tt9032400/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['King Richard', 'https://www.imdb.com/title/tt9620288/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['House of Gucci', 'https://www.imdb.com/title/tt11214590/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Ghostbusters: Afterlife','https://www.imdb.com/title/tt4513678/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Clifford the Big Red Dog','https://www.imdb.com/title/tt2397461/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Resident Evil: Welcome to Raccoon City','https://www.imdb.com/title/tt6920084/reviews?sort=submissionDate&dir=desc&ratingFilter=0']]
    # category = 'global'
    # global_category = 'BoxOffice'

    # urllist = [['365 Days', 'https://www.imdb.com/title/tt10886166/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Sightless', 'https://www.imdb.com/title/tt10303430/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Double Dad', 'https://www.imdb.com/title/tt4733736/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Death to 2020', 'https://www.imdb.com/title/tt13567480/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Dracula Untold', 'https://www.imdb.com/title/tt0829150/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The White Tiger', 'https://www.imdb.com/title/tt6571548/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['We Can Be Heroes', 'https://www.imdb.com/title/tt10600398/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Outside the Wire', 'https://www.imdb.com/title/tt10451914/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Midnight Sky', 'https://www.imdb.com/title/tt10539608/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Pieces of a Woman', 'https://www.imdb.com/title/tt11161474/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Dig', 'https://www.imdb.com/title/tt3661210/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Red Dot', 'https://www.imdb.com/title/tt11307814/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Below Zero', 'https://www.imdb.com/title/tt9845564/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Squared Love', 'https://www.imdb.com/title/tt13846542/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['I Care a Lot', 'https://www.imdb.com/title/tt9893250/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ["Finding 'Ohana", 'https://www.imdb.com/title/tt10332588/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['News of the World', 'https://www.imdb.com/title/tt6878306/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['To All the Boys: Always and Forever','https://www.imdb.com/title/tt10676012/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Animals on the Loose: A You vs. Wild Interactive Movie','https://www.imdb.com/title/tt13853720/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Moxie', 'https://www.imdb.com/title/tt6432466/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Yes Day', 'https://www.imdb.com/title/tt8521876/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Sentinelle', 'https://www.imdb.com/title/tt11734264/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Paper Lives', 'https://www.imdb.com/title/tt13045890/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Crazy About Her', 'https://www.imdb.com/title/tt11698630/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Deadly Illusions', 'https://www.imdb.com/title/tt7897330/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Girl on the Train','https://www.imdb.com/title/tt3631112/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Operation Varsity Blues: The College Admissions Scandal','https://www.imdb.com/title/tt14111734/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Run', 'https://www.imdb.com/title/tt8633478/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Shrek', 'https://www.imdb.com/title/tt0126029/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Minions', 'https://www.imdb.com/title/tt2293640/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Blackhat', 'https://www.imdb.com/title/tt2717822/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Sky High', 'https://www.imdb.com/title/tt0405325/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Stowaway', 'https://www.imdb.com/title/tt9203694/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Seaspiracy', 'https://www.imdb.com/title/tt14152756/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Thunder Force', 'https://www.imdb.com/title/tt10121392/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Love and Monsters', 'https://www.imdb.com/title/tt2222042/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Secret Magic Control Agency','https://www.imdb.com/title/tt13932162/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Home', 'https://www.imdb.com/title/tt2224026/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Oxygen', 'https://www.imdb.com/title/tt6341832/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['I Am All Girls', 'https://www.imdb.com/title/tt9013182/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Army of the Dead', 'https://www.imdb.com/title/tt0993840/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Things Heard & Seen','https://www.imdb.com/title/tt10962368/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Fifty Shades of Grey','https://www.imdb.com/title/tt2322441/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Penguins of Madagascar','https://www.imdb.com/title/tt1911658/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Woman in the Window','https://www.imdb.com/title/tt6111574/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Mitchells vs. The Machines','https://www.imdb.com/title/tt7979580/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Awake', 'https://www.imdb.com/title/tt10418662/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Xtreme', 'https://www.imdb.com/title/tt11658120/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Trouble', 'https://www.imdb.com/title/tt6772524/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Fatherhood', 'https://www.imdb.com/title/tt4733624/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Wish Dragon', 'https://www.imdb.com/title/tt5562070/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Skater Girl', 'https://www.imdb.com/title/tt6964940/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Good on Paper', 'https://www.imdb.com/title/tt8231668/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Silver Skates', 'https://www.imdb.com/title/tt10525672/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Rurouni Kenshin: The Final','https://www.imdb.com/title/tt11809034/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Blood Red Sky', 'https://www.imdb.com/title/tt6402468/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Water Man', 'https://www.imdb.com/title/tt4779326/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Fear Street: 1994', 'https://www.imdb.com/title/tt6566576/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Fear Street: 1978', 'https://www.imdb.com/title/tt9701940/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Fear Street: 1666', 'https://www.imdb.com/title/tt9701942/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Magnificent Seven','https://www.imdb.com/title/tt2404435/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Major Grom: Plague Doctor','https://www.imdb.com/title/tt7601480/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Trollhunters: Rise of the Titans', 'https://www.imdb.com/title/tt12851396/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Vivo', 'https://www.imdb.com/title/tt6338498/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Beckett', 'https://www.imdb.com/title/tt10230994/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Aftermath', 'https://www.imdb.com/title/tt10691162/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Sweet Girl', 'https://www.imdb.com/title/tt10731768/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Resort to Love', 'https://www.imdb.com/title/tt12929990/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Last Mercenary', 'https://www.imdb.com/title/tt12808182/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Kissing Booth 3', 'https://www.imdb.com/title/tt12783454/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Loud House Movie', 'https://www.imdb.com/title/tt6714432/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['The Secret Life of Pets', 'https://www.imdb.com/title/tt2709768/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Kate', 'https://www.imdb.com/title/tt7737528/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Prey', 'https://www.imdb.com/title/tt15198608/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #            ['Intrusion', 'https://www.imdb.com/title/tt5563324/reviews?sort=submissionDate&dir=desc&ratingFilter=0']]
    # category = 'global'
    # global_category = 'netflix_movie'
    # urllist = [['Schumacher', 'https://www.imdb.com/title/tt10322274/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Nightbooks', 'https://www.imdb.com/title/tt10521144/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Man on Fire', 'https://www.imdb.com/title/tt0328107/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ["He's All That", 'https://www.imdb.com/title/tt4590256/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['The Stronghold', 'https://www.imdb.com/title/tt10404944/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['SAS: Red Notice', 'https://www.imdb.com/title/tt4479380/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Afterlife of the Party', 'https://www.imdb.com/title/tt11742798/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Venom', 'https://www.imdb.com/title/tt1270797/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['The Trip', 'https://www.imdb.com/title/tt13109952/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['The Guilty', 'https://www.imdb.com/title/tt9421570/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Friendzone', 'https://www.imdb.com/title/tt14700948/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Night Teeth', 'https://www.imdb.com/title/tt10763820/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Ride Along 2', 'https://www.imdb.com/title/tt2869728/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['The Forgotten Battle', 'https://www.imdb.com/title/tt10521092/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['No One Gets Out Alive', 'https://www.imdb.com/title/tt13056008/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['My Little Pony: A New Generation', 'https://www.imdb.com/title/tt10101702/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ["There's Someone Inside Your House", 'https://www.imdb.com/title/tt8150814/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Yara', 'https://www.imdb.com/title/tt15655276/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Bruised', 'https://www.imdb.com/title/tt8310474/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Love Hard', 'https://www.imdb.com/title/tt10752004/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Red Notice', 'https://www.imdb.com/title/tt7991608/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['The Croods', 'https://www.imdb.com/title/tt15341442/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Army of Thieves', 'https://www.imdb.com/title/tt13024674/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['The Harder They Fall','https://www.imdb.com/title/tt10696784/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['Central Intelligence','https://www.imdb.com/title/tt1489889/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
    #             ['The Princess Switch 3: Romancing The Star','https://www.imdb.com/title/tt14731142/reviews?sort=submissionDate&dir=desc&ratingFilter=0']]
    # category = 'global'
    # global_category = 'netflix_movie'
    urllist = [['Lupin', 'https://www.imdb.com/title/tt2531336/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Vikings', 'https://www.imdb.com/title/tt2306299/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Cobra Kai', 'https://www.imdb.com/title/tt7221388/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Bridgerton', 'https://www.imdb.com/title/tt8740790/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Disenchantment', 'https://www.imdb.com/title/tt5363918/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ["The Queen's Gambit", 'https://www.imdb.com/title/tt10048342/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Fate: The Winx Saga', 'https://www.imdb.com/title/tt8179402/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Yo soy Betty la fea', 'https://www.imdb.com/title/tt0233127/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['The Uncanny Counter','https://www.imdb.com/title/tt13273826/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Chilling Adventures of Sabrina','https://www.imdb.com/title/tt7569592/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Riverdale', 'https://www.imdb.com/title/tt5420376/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Snowpiercer', 'https://www.imdb.com/title/tt6156584/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Firefly Lane', 'https://www.imdb.com/title/tt9012876/reviews?sort=helpfulnessScore&dir=desc&ratingFilter=0'],
                ['New Amsterdam', 'https://www.imdb.com/title/tt7817340/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Behind Her Eyes', 'https://www.imdb.com/title/tt9698442/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Tribes of Europa', 'https://www.imdb.com/title/tt9184982/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Crime Scene: The Vanishing at the Cecil Hotel','https://www.imdb.com/title/tt13837672/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['The One', 'https://www.imdb.com/title/tt13879466/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Sky Rojo', 'https://www.imdb.com/title/tt8690776/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['The Bold Type', 'https://www.imdb.com/title/tt6116060/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Ginny & Georgia', 'https://www.imdb.com/title/tt10813940/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Who Killed Sara?', 'https://www.imdb.com/title/tt11937816/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Formula 1: Drive to Survive','https://www.imdb.com/title/tt8289930/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['The Circle', 'https://www.imdb.com/title/tt9581768/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['The Serpent', 'https://www.imdb.com/title/tt7985576/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['The Blacklist', 'https://www.imdb.com/title/tt5592230/reviews?sort=helpfulnessScore&dir=desc&ratingFilter=0'],
                ['The Irregulars', 'https://www.imdb.com/title/tt10893694/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Shadow and Bone', 'https://www.imdb.com/title/tt2403776/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Tale of the Nine Tailed','https://www.imdb.com/title/tt12879418/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Demon Slayer: Kimetsu no Yaiba','https://www.imdb.com/title/tt9335498/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Sexify', 'https://www.imdb.com/title/tt14315542/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Friends', 'https://www.imdb.com/title/tt0108778/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Ragnarok', 'https://www.imdb.com/title/tt9251798/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Falsa Identidad', 'https://www.imdb.com/title/tt8598690/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ["Jupiter's Legacy", 'https://www.imdb.com/title/tt5774002/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Love, Death & Robots', 'https://www.imdb.com/title/tt9561862/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Jurassic World: Camp Cretaceous','https://www.imdb.com/title/tt10436228/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Elite', 'https://www.imdb.com/title/tt7134908/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Lucifer', 'https://www.imdb.com/title/tt4052886/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['StartUp', 'https://www.imdb.com/title/tt5028002/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Sweet Tooth', 'https://www.imdb.com/title/tt12809988/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Record of Ragnarok', 'https://www.imdb.com/title/tt13676344/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Sex/Life', 'https://www.imdb.com/title/tt10839422/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Atypical', 'https://www.imdb.com/title/tt6315640/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Virgin River', 'https://www.imdb.com/title/tt9077530/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Rick and Morty', 'https://www.imdb.com/title/tt2861424/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['The Good Doctor', 'https://www.imdb.com/title/tt6470478/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Never Have I Ever', 'https://www.imdb.com/title/tt10062292/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Too Hot to Handle', 'https://www.imdb.com/title/tt12004280/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['The Cook of Castamar','https://www.imdb.com/title/tt12626014/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Hit & Run', 'https://www.imdb.com/title/tt9073940/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Clickbait', 'https://www.imdb.com/title/tt10888878/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Control Z', 'https://www.imdb.com/title/tt11937662/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Outer Banks', 'https://www.imdb.com/title/tt10293938/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['AlRawabi School for Girls','https://www.imdb.com/title/tt10183912/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['The Snitch Cartel: Origins','https://www.imdb.com/title/tt14417802/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Good Girls', 'https://www.imdb.com/title/tt6474378/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Money Heist', 'https://www.imdb.com/title/tt6468322/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Sex Education', 'https://www.imdb.com/title/tt7767422/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Money Heist: From Tokyo to Berlin','https://www.imdb.com/title/tt15384346/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Turning Point: 9/11 and the War on Terror','https://www.imdb.com/title/tt15260794/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Maid', 'https://www.imdb.com/title/tt11337908/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Dynasty', 'https://www.imdb.com/title/tt6128300/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Paw Patrol', 'https://www.imdb.com/title/tt11832046/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Locke & Key', 'https://www.imdb.com/title/tt3007572/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Midnight Mass', 'https://www.imdb.com/title/tt10574558/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Kastanjemanden', 'https://www.imdb.com/title/tt10834220/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['The Five Juanas', 'https://www.imdb.com/title/tt15377930/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Alice in Borderland','https://www.imdb.com/title/tt10795658/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Arcane', 'https://www.imdb.com/title/tt11126994/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Cowboy Bebop', 'https://www.imdb.com/title/tt1267295/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['Narcos: Mexico', 'https://www.imdb.com/title/tt8714904/reviews?sort=submissionDate&dir=desc&ratingFilter=0'],
                ['The Queen of Flow', 'https://www.imdb.com/title/tt8560918/reviews?sort=submissionDate&dir=desc&ratingFilter=0']]
    #2)
    category = 'global'
    global_category = 'netflix_tvshow'

    for url in urllist:
        driver.get(url[1])
        driver.implicitly_wait(3)
        time.sleep(2)
        review_num = 0

        last_height = driver.execute_script("return document.body.scrollHeight")
        # load more 클릭
        cnum = 0
        while True:
            try:
                load_more = driver.find_element_by_css_selector('#load-more-trigger')
                driver.execute_script("arguments[0].click();", load_more)

                conn = db_con()

                print('click')
                driver.implicitly_wait(10)
                time.sleep(3)
                cnum += 1

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                reviews = soup.select('.lister-item.mode-detail.imdb-user-review')
                review = reviews[-1]

                review_date = review.select_one('.review-date').text
                review_date = datetime.strptime(review_date, '%d %B %Y')
                review_date = review_date.date()
                print(review_date)

                first_date = '2021/06/01'
                first_date = datetime.strptime(first_date, '%Y/%m/%d')
                first_date = first_date.date()
                if review_date < first_date:  # 기준일 이전 게시물이 나오면 더이상 로드하지 않음
                    print('skip before')
                    break

                #필요할 때만
                # if cnum > 25:
                #     print('break')
                #     break
            except:
                print('no click')
                break
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:  # 새 길이와 이전 스크롤 길이가 같다면, 검색 끝 이므로 break
                break
            last_height = new_height

        load_longers = driver.find_elements_by_css_selector('div:nth-child(1) > div.ipl-expander > div > div')
        for load_longer in load_longers:
            driver.execute_script("arguments[0].click();", load_longer)
            print('click2')

        time.sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        reviews = soup.select('.lister-item.mode-detail.imdb-user-review')

        #리뷰마다 돌면서
        for review in reviews:
            try:
                star_points = review.select_one('.rating-other-user-rating').text.strip()
                print(star_points)
                star_points = star_points.split('/')[0]
                star_points = int(star_points)
            except:
                star_points = None

            review_date = review.select_one('.review-date').text
            review_date = datetime.strptime(review_date, '%d %B %Y')
            review_date = review_date.date()

            helpful = review.select_one('.actions.text-muted').text.strip()
            helpful = helpful.split('out')
            helpful = helpful[0]
            helpful = helpful.replace(',', '')
            helpful = int(helpful)

            #작성자
            review_writer = review.select_one('.display-name-link').text.strip()

            #본문
            review_content = review.select_one('.text.show-more__control').text.strip()

            #제목
            review_header = review.select_one('.title').text.strip()

            review_num += 1

            #1)
            # try:
            #     category = soup.select_one('.aux-content-widget-2.links.subnav .nobr').text
            #     if 'TV' in category:
            #         category = 'drama'
            #     if not category:
            #         category = 'movie'
            # except:
            #     category = 'movie'

            movie_drama = url[0]
            print(movie_drama)
            print(review_writer)
            print(review_header)
            print(review_content)
            print(helpful)
            print(review_date)
            print(star_points)
            print(review_num)
            print('-'*100)

            model_kwargs['comment_id'] = str(uuid.uuid4()).replace('-', '')
            model_kwargs['source_name'] = 'imdb'
            model_kwargs['category'] = ignore_text(category)
            model_kwargs['title'] = ignore_text(movie_drama)
            model_kwargs['writer'] = ignore_text(review_writer)
            model_kwargs['review_title'] = ignore_text(review_header)
            model_kwargs['content'] = ignore_text(review_content)
            model_kwargs['like_count'] = helpful
            model_kwargs['post_date'] = review_date
            model_kwargs['star_point_five'] = None
            model_kwargs['star_point_ten'] = star_points
            model_kwargs['global_category'] = global_category
            model_kwargs['url'] = url[1] + '#' + str(review_num)+'_'+str(datetime.today().strftime("%Y%m%d"))
            print(model_kwargs)

            first_date = '2021/06/01'
            first_date = datetime.strptime(first_date, '%Y/%m/%d')
            first_date = first_date.date()
            if review_date < first_date:  # 기준일 이전 게시물의 경우 건너뜀
                print('skip before')
                break

            second_date = '2021/11/30'
            second_date = datetime.strptime(second_date, '%Y/%m/%d')
            second_date = second_date.date()
            if review_date > second_date:  # 기준일 이후 게시물의 경우 건너뜀
                print('skip after')
                continue

            insert_content_review(conn=conn, model_kwargs=model_kwargs)
            #time.sleep(1)

    conn.close()
    print('done')
    driver.close()

imdb()