import datetime
import logging
import os.path
import sys

import bs4
import requests
from requests import request
import database

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Formatter for logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File handler
file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"}
dim_ria_api_homes = (
    'https://dom.ria.com/node/searchEngine/v2/?addMoreRealty=false&excludeSold=1&category=1&realty_type=2&operati, on=3&state_id=10&city_id=0&in_radius=0&with_newbuilds=0&price_cur=1&wo_dupl=1&complex_inspected=0&sort=created_at&period=0&notFirstFloor=0&notLastFloor=0&with_map=0&photos_count_from=0&firstIteraction=false&fromAmp=0&city_ids=10&limit=20&market=3&type=list&client=searchV2&operation_type=3&page=0&ch=209_f_2%2C209_t_2%2C235_f_0%2C235_t_16000%2C246_244')
dim_ria_api_home = "https://dom.ria.com/realty/data/"

# import json
#
# resp = request(method='get', url="""
# https://dom.ria.com/node/searchEngine/v2/?addMoreRealty=false&excludeSold=1&category=1&realty_type=2&operati, on=3&state_id=10&city_id=0&in_radius=0&with_newbuilds=0&price_cur=1&wo_dupl=1&complex_inspected=0&sort=created_at&period=0&notFirstFloor=0&notLastFloor=0&with_map=0&photos_count_from=0&firstIteraction=false&fromAmp=0&city_ids=10&limit=20&market=3&type=list&client=searchV2&operation_type=3&page=0&ch=209_f_2%2C209_t_2%2C235_f_0%2C235_t_16000%2C246_244""")
# dim_ria_api_home = "https://dom.ria.com/realty/data/"
# home_ids = json.loads(resp.content)["items"]
#
# home = request("get", "https://dom.ria.com/realty/data/" + str(home_ids[0]))
# data = json.loads(home.content)


def get_new_homes():
    res = request('get', dim_ria_api_homes, headers=headers)
    soup = bs4.BeautifulSoup(res.content, features="html.parser")

    list_of_homes = soup.find(class_='search-result-list f100-wrap').find_all(class_='realty-item')

    new_homes = []
    for idx, home in enumerate(list_of_homes):
        section = soup.select_one('section.realty-item')
        title_tag = section.select_one('.tit a.size22')
        title = title_tag.get_text(strip=True)
        link = "https://dom.ria.com" + title_tag['href'] if title_tag else None
        price = section.select_one('b.size22').get_text(strip=True)

        images = []
        img_tags = section.select('picture img')
        for img in img_tags:
            if 'src' in img.attrs:
                src = img['src']
                # Optionally enhance resolution
                high_res = src.replace('xl.webp', 'xxl.webp') if 'xl.webp' in src else src
                images.append(high_res)

        if not database.check_and_add_home(link, title, price):
            home_dict = {
                'site': 'dim_ria',
                'title': title,
                'link': link,
                'price': price,
                'description': '',
                'images': images[:9]
            }

            new_homes.append(home_dict)

    logging.info(f"{datetime.datetime.now()} - Dim Ria - Found {len(new_homes)} new homes")
    return new_homes


if __name__ == "__main__":
    logging.basicConfig(handlers=[file_handler, console_handler], level=logging.INFO)
    new_homes = get_new_homes()
    for home in new_homes:
        print(home)
