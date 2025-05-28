import datetime
import json
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

lun = (
    'https://lun.ua/rent/kyiv/flats?price_max=15000&currency=UAH&room_count=2&room_count=3&sort=insert_time')


def get_new_homes():
    lun = (
        'https://lun.ua/rent/kyiv/flats?price_max=15000&currency=UAH&room_count=2&room_count=3&sort=insert_time')

    res = request('get', lun)
    soup = bs4.BeautifulSoup(res.content, features="html.parser")
    homes = json.loads(soup.find("script", id="schema-real-estate").contents[0]).get('itemListElement')

    new_homes = []
    for home in homes:
        item = home["item"]
        name = item["name"]
        images = item["image"]
        price = item["offers"]["price"]
        availability_starts = item["offers"]["availabilityStarts"]
        link = name + "|" + str(price)

        if not database.check_and_add_home(link, name, price):
            home_dict = {
                'site' : 'lun',
                'title': name,
                'link': lun,
                'price': price,
                'description': '',
                'images': images
            }

            new_homes.append(home_dict)

    logging.info(f"{datetime.datetime.now()} - LUN - Found {len(new_homes)} new homes")
    return new_homes


