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

def rotten_tomatoes():
    model_kwargs = {
        'source_name': 'rotten tomatoes',
        'biz_kind': 'review',
        #'methd': 'search'
    }
    conn = db_con()


    ## setup Driver|Chrome : 크롬드라이버를 사용하는 driver 생성
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)  # 크롬 드라이버를 사용하는 드라이버 생성
    driver.implicitly_wait(5)  ## 웹 자원을 3초 기다리기

    # 한국 작품이면 1) 사용하시고 글로벌은 1) 주석 처리 후 2) 사용하면 됩니다

    # urllist= ['https://www.rottentomatoes.com/tv/squid_game/s01/reviews?type=user', 'https://www.rottentomatoes.com/m/the_8th_night/reviews?type=user',
    #           'https://www.rottentomatoes.com/m/night_in_paradise/reviews?type=user',
    #           'https://www.rottentomatoes.com/m/parasite_2019/reviews?type=user',  'https://www.rottentomatoes.com/m/miss_and_mrs_cops/reviews?type=user',
    #           'https://www.rottentomatoes.com/m/minari/reviews?type=user',  'https://www.rottentomatoes.com/m/space_sweepers/reviews?type=user',
    #           'https://www.rottentomatoes.com/m/escape_from_mogadishu/reviews?type=user']

    # urllist = ['https://www.rottentomatoes.com/m/zombie_for_sale/reviews?type=user',
    #            'https://www.rottentomatoes.com/m/the_swindlers/reviews?type=user',
    #            'https://www.rottentomatoes.com/m/the_fortress_2017/reviews?type=user',
    #            'https://www.rottentomatoes.com/m/the_age_of_shadows/reviews?type=user',
    #            'https://www.rottentomatoes.com/m/train_to_busan/reviews?type=user',
    #            'https://www.rottentomatoes.com/m/memoir_of_a_murderer/reviews?type=user',
    #            'https://www.rottentomatoes.com/m/113921da-b28b-32d1-8deb-1f0228bf0025/reviews?type=user',
    #            'https://www.rottentomatoes.com/m/detective_k_secret_of_the_living_dead/reviews?type=user',
    #            'https://www.rottentomatoes.com/m/the_prison/reviews?type=user',
    #            'https://www.rottentomatoes.com/m/howling_2012/reviews?type=user',
    #            'https://www.rottentomatoes.com/m/secret_zoo/reviews?type=user']
    # urllist = ['https://www.rottentomatoes.com/tv/run_on/s01/reviews?type=user', 'https://www.rottentomatoes.com/tv/sweet_home/s01/reviews?type=user',
    #            'https://www.rottentomatoes.com/tv/nevertheless/s01/reviews?type=user', 'https://www.rottentomatoes.com/tv/law_school/s01/reviews?type=user',
    #            'https://www.rottentomatoes.com/tv/you_are_my_spring/s01/reviews?type=user', 'https://www.rottentomatoes.com/tv/mine/s01/reviews?type=user',
    #            'https://www.rottentomatoes.com/tv/hospital_playlist/s02/reviews?type=user', 'https://www.rottentomatoes.com/tv/racket_boys/s01/reviews?type=user',
    #            'https://www.rottentomatoes.com/tv/love_ft_marriage_and_divorce/s01/reviews?type=user', 'https://www.rottentomatoes.com/tv/love_ft_marriage_and_divorce/s02/reviews?type=user',
    #            'https://www.rottentomatoes.com/tv/move_to_heaven/s01/reviews?type=user',
    #            'https://www.rottentomatoes.com/tv/mad_for_each_other/s01/reviews?type=user', 'https://www.rottentomatoes.com/tv/the_devil_judge/s01/reviews?type=user',
    #            'https://www.rottentomatoes.com/tv/love_alarm/s02/reviews?type=user', 'https://www.rottentomatoes.com/tv/hometown_cha_cha_cha/s01/reviews?type=user',
    #            'https://www.rottentomatoes.com/tv/vincenzo/s01/reviews?type=user', 'https://www.rottentomatoes.com/tv/itaewon_class/s01/reviews?type=user',
    #            'https://www.rottentomatoes.com/tv/navillera/s01/reviews?type=user', 'https://www.rottentomatoes.com/tv/extracurricular/s01/reviews?type=user',
    #            'https://www.rottentomatoes.com/tv/hellbound/s01/reviews?type=user', 'https://www.rottentomatoes.com/tv/my_name/s01/reviews?type=user',
    #            'https://www.rottentomatoes.com/tv/dr_brain/s01/reviews?type=user']

    # urllist = ['https://www.rottentomatoes.com/m/fatale/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/our_friend/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_marksman_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/monster_hunter/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_little_things_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/wonder_woman_1984/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_war_with_grandpa/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_croods_a_new_age/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/promising_young_woman/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/land_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/nomadland/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/tom_and_jerry/reviews',
    #         'https://www.rottentomatoes.com/m/judas_and_the_black_messiah/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/nobody_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/boogie_2020/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_courier/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/chaos_walking/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/raya_and_the_last_dragon/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_unholy_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/in_the_earth/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/mortal_kombat_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/together_together/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/demon_slayer_kimetsu_no_yaiba_the_movie_mugen_train/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_girl_who_believes_in_miracles/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/cruella/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/dream_horse/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/world-war-z/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/finding_you/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/wrath_of_man/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/a_quiet_place_part_ii/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/queen_bees/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/spirit_untamed/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/f9/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/werewolves_within/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_hitmans_wifes_bodyguard/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/peter_rabbit_2_the_runaway/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/old/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/stillwater_2020/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/snake_eyes_gi_joe_origins/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/black_widow_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/jungle_cruise/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_green_knight/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_forever_purge/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_boss_baby_family_business/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/escape_room_tournament_of_champions/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/respect_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/candyman_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/free_guy/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_protege/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/dont_breathe_2/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_night_house/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/paw_patrol_the_movie/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/copshop/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/dear_evan_hansen/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_card_counter/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_eyes_of_tammy_faye_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/shang_chi_and_the_legend_of_the_ten_rings/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/dune_2021/reviews?type=user',
    # urllist = ['https://www.rottentomatoes.com/m/antlers/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/no_time_to_die_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/halloween_kills/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/rons_gone_wrong/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/last_night_in_soho/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_addams_family_2/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_french_dispatch/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/venom_let_there_be_carnage/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/my_hero_academia_world_heroes_mission/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/encanto_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/eternals/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/king_richard/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/house_of_gucci/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/ghostbusters_afterlife/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/clifford_the_big_red_dog/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/resident_evil_welcome_to_raccoon_city/reviews?type=user']
    # #2)
    # category = 'global'
    # global_category = 'BoxOffice'
    # urllist = ['https://www.rottentomatoes.com/m/365_days_2020/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/sightless/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/double_dad/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/death_to_2020/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/dracula_untold/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_white_tiger_2020/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/we_can_be_heroes_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/outside_the_wire/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_midnight_sky/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/pieces_of_a_woman/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_dig_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/red_dot/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/below_zero_2011/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/squared_love/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/i_care_a_lot/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/finding_ohana/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/news_of_the_world/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/to_all_the_boys_always_and_forever/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/moxie/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/yes_day/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/sentinelle/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/paper_lives/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/crazy_about_her/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/deadly_illusions/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_girl_on_the_train_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/operation_varsity_blues_the_college_admissions_scandal/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/run_2020/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/shrek/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/minions/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/blackhat/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/1142872-sky_high/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/stowaway_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/seaspiracy/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/thunder_force/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/love_and_monsters/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/secret_magic_control_agency/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/home_2015/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/oxygen_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/i_am_all_girls/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/army_of_the_dead_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/things_heard_and_seen/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/fifty_shades_of_grey/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/penguins_of_madagascar_operation/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_woman_in_the_window_2020/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_mitchells_vs_the_machines/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/awake_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/xtreme/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/trouble_2018/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/fatherhood_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/wish_dragon/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/skater_girl/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/good_on_paper/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/rurouni_kenshin_final_chapter_part_i_the_final/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/blood_red_sky/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_water_man/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/fear_street_part_one_1994/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/fear_street_part_two_1978/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/fear_street_part_three_1666/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_magnificent_seven_2016/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/major_grom_plague_doctor/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/trollhunters_rise_of_the_titans/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/vivo/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/beckett/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/aftermath_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/sweet_girl/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/resort_to_love/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_last_mercenary/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_kissing_booth_3/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_loud_house_movie/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/the_secret_life_of_pets_2/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/kate_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/prey_2021/reviews?type=user',
    #         'https://www.rottentomatoes.com/m/intrusion_2021/reviews?type=user']
    # category = 'global'
    # global_category = 'netflix_movie'

    # urllist = ['https://www.rottentomatoes.com/m/schumacher/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/nightbooks/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/man_on_fire/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/hes_all_that/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/the_stronghold_2020/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/afterlife_of_the_party/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/venom_2018/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/the_trip_2021/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/the_guilty_2021/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/friendzone/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/night_teeth/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/ride_along_2/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/the_forgotten_battle/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/no_one_gets_out_alive/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/my_little_pony_a_new_generation/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/theres_someone_inside_your_house/reviews',
    #  'https://www.rottentomatoes.com/m/yara_2021/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/bruised/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/love_hard/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/red_notice/reviews',
    #  'https://www.rottentomatoes.com/m/the_croods_a_new_age/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/army_of_thieves/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/the_harder_they_fall/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/central_intelligence/reviews?type=user',
    #  'https://www.rottentomatoes.com/m/the_princess_switch_3_romancing_the_star/reviews?type=user']
    # category = 'global'
    # global_category = 'netflix_movie'

    urllist = ['https://www.rottentomatoes.com/tv/lupin/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/lupin/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/vikings_2013/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/vikings_2013/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/vikings_2013/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/vikings_2013/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/vikings_2013/s05/reviews?type=user',
            'https://www.rottentomatoes.com/tv/vikings_2013/s06/reviews?type=user',
            'https://www.rottentomatoes.com/tv/cobra_kai/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/cobra_kai/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/cobra_kai/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/bridgerton/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/disenchantment/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/disenchantment/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_queens_gambit/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/fate_the_winx_saga/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_uncanny_counter/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/chilling_adventures_of_sabrina/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/chilling_adventures_of_sabrina/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/chilling_adventures_of_sabrina/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/chilling_adventures_of_sabrina/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/riverdale/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/riverdale/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/riverdale/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/riverdale/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/riverdale/s05/reviews?type=user',
            'https://www.rottentomatoes.com/tv/riverdale/s06/reviews?type=user',
            'https://www.rottentomatoes.com/tv/snowpiercer/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/snowpiercer/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/firefly_lane/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/new_amsterdam_2018/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/new_amsterdam_2018/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/new_amsterdam_2018/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/new_amsterdam_2018/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/behind_her_eyes/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/tribes_of_europa/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/crime_scene_the_vanishing_at_the_cecil_hotel/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_one/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/sky_rojo/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_bold_type/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_bold_type/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_bold_type/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_bold_type/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_bold_type/s05/reviews?type=user',
            'https://www.rottentomatoes.com/tv/ginny_georgia/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/who_killed_sara/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/who_killed_sara/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/formula_1_drive_to_survive/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/formula_1_drive_to_survive/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/formula_1_drive_to_survive/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_circle_2020/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_circle_2020/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_circle_2020/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_serpent/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_blacklist/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_blacklist/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_blacklist/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_blacklist/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_blacklist/s05/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_blacklist/s06/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_blacklist/s07/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_blacklist/s08/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_blacklist/s09/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_irregulars/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/shadow_and_bone/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/sexify/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/friends/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/friends/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/friends/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/friends/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/friends/s05/reviews?type=user',
            'https://www.rottentomatoes.com/tv/friends/s06/reviews?type=user',
            'https://www.rottentomatoes.com/tv/friends/s07/reviews?type=user',
            'https://www.rottentomatoes.com/tv/friends/s08/reviews?type=user',
            'https://www.rottentomatoes.com/tv/friends/s09/reviews?type=user',
            'https://www.rottentomatoes.com/tv/friends/s10/reviews?type=user',
            'https://www.rottentomatoes.com/tv/ragnarok/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/ragnarok/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/jupiters_legacy/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/love_death_robots/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/love_death_robots/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/jurassic_world_camp_cretaceous/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/jurassic_world_camp_cretaceous/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/jurassic_world_camp_cretaceous/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/jurassic_world_camp_cretaceous/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/elite/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/elite/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/elite/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/elite/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/lucifer/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/lucifer/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/lucifer/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/lucifer/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/lucifer/s05/reviews?type=user',
            'https://www.rottentomatoes.com/tv/lucifer/s06/reviews?type=user',
            'https://www.rottentomatoes.com/tv/startup/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/startup/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/startup/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/sweet_tooth/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/record_of_ragnarok/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/sex_life/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/atypical/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/atypical/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/atypical/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/atypical/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/virgin_river/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/virgin_river/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/virgin_river/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/rick_and_morty/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/rick_and_morty/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/rick_and_morty/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/rick_and_morty/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/rick_and_morty/s05/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_good_doctor/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_good_doctor/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_good_doctor/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_good_doctor/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_good_doctor/s05/reviews?type=user',
            'https://www.rottentomatoes.com/tv/never_have_i_ever/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/never_have_i_ever/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/too-hot-to-handle/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/too-hot-to-handle/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_cook_of_castamar/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/hit_and_run/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/clickbait/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/control_z/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/control_z/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/outer_banks/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/outer_banks/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/alrawabi_school_for_girls/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_snitch_cartel_origins/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/good_girls/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/good_girls/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/good_girls/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/good_girls/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/money_heist/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/money_heist/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/money_heist/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/money_heist/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/money_heist/s05/reviews?type=user',
            'https://www.rottentomatoes.com/tv/sex_education/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/sex_education/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/sex_education/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/turning_point_9_11_and_the_war_on_terror/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/you/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/you/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/you/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/maid/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/dynasty/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/dynasty/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/dynasty/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/dynasty/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/dynasty/s05/reviews?type=user',
            'https://www.rottentomatoes.com/tv/paw_patrol/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/paw_patrol/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/paw_patrol/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/paw_patrol/s04/reviews?type=user',
            'https://www.rottentomatoes.com/tv/paw_patrol/s05/reviews?type=user',
            'https://www.rottentomatoes.com/tv/paw_patrol/s06/reviews?type=user',
            'https://www.rottentomatoes.com/tv/paw_patrol/s07/reviews?type=user',
            'https://www.rottentomatoes.com/tv/paw_patrol/s08/reviews?type=user',
            'https://www.rottentomatoes.com/tv/locke_key/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/locke_key/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/midnight_mass/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_five_juanas/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/alice_in_borderland/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/arcane_league_of_legends/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/cowboy_bebop_2021/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/narcos_mexico/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/narcos_mexico/s02/reviews?type=user',
            'https://www.rottentomatoes.com/tv/narcos_mexico/s03/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_queen_of_flow/s01/reviews?type=user',
            'https://www.rottentomatoes.com/tv/the_queen_of_flow/s02/reviews?type=user']
    #2)
    category = 'global'
    global_category = 'netflix_tvshow'



    #url 돌면서 정보수집
    for url in urllist:
        #url = 'https://www.rottentomatoes.com/m/parasite_2019/reviews?type=user'
        driver.get(url)
        driver.implicitly_wait(3)
        time.sleep(1)#페이지 로딩을 기다리기 위해서
        review_num = 0
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        #맨 첫번째 리뷰 수집(비교용)
        try:
            writer_compare = soup.select_one(
                '.audience-reviews .audience-reviews__item .audience-reviews__name-wrap').text.strip()
            content_compare = soup.select_one(
                '.audience-reviews .audience-reviews__item .audience-reviews__review').text.strip()
        except:
            print('no review')
            continue

        #리뷰 페이지 순환
        try:
            while True:
                #time.sleep(1)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                reviews = soup.select('.audience-reviews .audience-reviews__item')

                #리뷰 돌면서
                for review in reviews:
                    review_writer = review.select_one('.audience-reviews__name-wrap').text.strip()
                    review_content = review.select_one('.audience-reviews__review').text.strip()

                    review_num += 1
                    print(review_num)
                    #첫번째 리뷰가 아니고 리뷰내용이랑 작성자가 겹치면 한바퀴 돌았으니 스탑
                    if review_num != 1:
                        if review_content == content_compare:
                            if review_writer == writer_compare:
                                print('loop!!')
                                print('-'*100)
                                print('-'*100)
                                raise LoopBreak()

                    #날짜
                    review_date = review.select_one('.audience-reviews__duration').text.strip()
                    if 'm ago' in review_date:
                        today = datetime.today()
                        minutes = review_date.replace('m ago', '')
                        minutes = int(minutes)
                        review_date = today - timedelta(minutes=minutes)
                        review_date = review_date.date()
                    elif 'h ago' in review_date:
                        today = datetime.today()
                        hour = review_date.replace('h ago', '')
                        hour = int(hour)
                        review_date = today - timedelta(hours=hour)
                        review_date = review_date.date()
                    elif 'd ago' in review_date:
                        today = datetime.today()
                        day = review_date.replace('d ago', '')
                        day = int(day)
                        review_date = today - timedelta(days=day)
                        review_date = review_date.date()
                    else:
                        review_date = datetime.strptime(review_date, '%b %d, %Y')
                        review_date = review_date.date()

                    review_star = str(review.select_one('.star-display'))
                    star_count = review_star.count('filled')

                    #제목
                    movie_drama = soup.select_one('.panel-body.content_body .center .unstyled.articleLink').text.strip()

                    #1)
                    # 필요하면 사용. 드라마 영화 구분
                    # if '/m/' in url:
                    #     category = 'movie'
                    # elif '/tv/' in url:
                    #     category = 'drama'

                    print(category)
                    print(movie_drama)
                    print(review_writer)
                    print(review_content)
                    print(review_date)
                    print(star_count)
                    print('-'*100)

                    model_kwargs['comment_id'] = str(uuid.uuid4()).replace('-', '')
                    model_kwargs['source_name'] = 'rotten tomatoes'
                    model_kwargs['category'] = ignore_text(category)
                    model_kwargs['title'] = ignore_text(movie_drama)
                    model_kwargs['writer'] = ignore_text(review_writer)
                    model_kwargs['review_title'] = None
                    model_kwargs['content'] = ignore_text(review_content)
                    model_kwargs['like_count'] = None
                    model_kwargs['post_date'] = review_date
                    model_kwargs['star_point_five'] = star_count
                    model_kwargs['star_point_ten'] = None
                    model_kwargs['global_category'] = global_category
                    model_kwargs['url'] = url+'#'+str(review_num)+'_'+str(datetime.today().strftime("%Y%m%d"))

                    print(model_kwargs)

                    first_date = '2021/06/01'
                    first_date = datetime.strptime(first_date, '%Y/%m/%d')
                    first_date = first_date.date()
                    if review_date < first_date:  # 기준일 이전 게시물의 경우 건너뜀
                        print('skip before')
                        raise LoopBreak()

                    second_date = '2021/11/30'
                    second_date = datetime.strptime(second_date, '%Y/%m/%d')
                    second_date = second_date.date()
                    if review_date > second_date:  # 기준일 이후 게시물의 경우 건너뜀
                        print('skip after')
                        continue

                    insert_content_review(conn=conn, model_kwargs=model_kwargs)

                #time.sleep(3)

                #다음페이지 로드
                try:
                    nextpage = driver.find_element_by_css_selector('button.js-prev-next-paging-next.btn.prev-next-paging__button.prev-next-paging__button-right')
                    print(nextpage)
                    driver.execute_script("arguments[0].click();", nextpage)
                    driver.implicitly_wait(5)
                    time.sleep(2) #페이지 로딩 기다림
                except:
                    print('move to next movie/drama')
                    break
        except LoopBreak:
            pass
    conn.close()
    print('done')
    print('-'*100)
    print('-'*100)
    print('-'*100)

rotten_tomatoes()