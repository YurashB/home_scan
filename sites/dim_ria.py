import datetime
import json
import logging

import bs4
from requests import request
import database

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"}
dim_ria_api_homes = (
    'https://dom.ria.com/node/searchEngine/v2/?addMoreRealty=false&excludeSold=1&category=1&realty_type=2&operati, on=3&state_id=10&city_id=0&in_radius=0&with_newbuilds=0&price_cur=1&wo_dupl=1&complex_inspected=0&sort=created_at&period=0&notFirstFloor=0&notLastFloor=0&with_map=0&photos_count_from=0&firstIteraction=false&fromAmp=0&city_ids=10&limit=20&market=3&type=list&client=searchV2&operation_type=3&page=0&ch=209_f_2%2C209_t_2%2C235_f_0%2C235_t_16000%2C246_244')
dim_ria_api_home = "https://dom.ria.com/realty/data/"
dim_ria_base = 'https://dom.ria.com/uk/'
dim_ria_img_url = "https://cdn.riastatic/com/photos/"


def get_new_homes():
    resp = request(method='get', url=dim_ria_api_homes)
    home_ids = json.loads(resp.content)["items"]

    new_homes = []
    for home_id in home_ids:
        home = request("get", dim_ria_api_home + str(home_id))
        data = json.loads(home.content)

        home_dict = {
            'site': 'dim_ria',
            'title': "В" + data['street_name'] + " " + data['building_number_str'],
            'link': dim_ria_base + data['beautiful_url'],
            'price': data['price_total'],
            'description': '',
            'images': __convert_img_urls(data['photos'])[:9]
        }
        if not database.check_and_add_home(home_dict['link'], home_dict['title'], home_dict['price']):
            new_homes.append(home_dict)

    logging.info(f"{datetime.datetime.now()} - Dim Ria - Found {len(new_homes)} new homes")
    return new_homes


def __convert_img_urls(photos):
    xl_urls = []
    for value in photos.values():
        url = value["file"]
        parts = url.rsplit('/', 1)
        path = parts[0]
        filename = parts[1].replace('.jpg', 'xl.jpg')
        xl_urls.append(dim_ria_img_url + path + "/" + filename)
    return xl_urls


if __name__ == "__main__":
    new_homes = get_new_homes()
    for home in new_homes:
        print(home)
