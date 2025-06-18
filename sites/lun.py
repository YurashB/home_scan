import datetime
import json
import logging
import bs4
from requests import request
import database


site = (
    'https://lun.ua/rent/kyiv/flats?price_max=16500&currency=UAH&room_count=2&room_count=3&sort=insert_time')


def get_new_homes():
    res = request('get', site)
    soup = bs4.BeautifulSoup(res.content, features="html.parser")
    try:
        homes = json.loads(soup.find("script", id="schema-real-estate").contents[0]).get('itemListElement')
    except Exception as e:
        logging.info(f"{datetime.datetime.now()} - LUN - Error parsing homes: {e}")
        return []

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
                'site': 'lun',
                'title': name,
                'link': site,
                'price': price,
                'description': '',
                'images': images[:9]
            }

            new_homes.append(home_dict)

    logging.info(f"{datetime.datetime.now()} - LUN - Found {len(new_homes)} new homes")
    return new_homes
