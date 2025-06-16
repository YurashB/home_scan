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

olx = (
    'https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?currency=UAH&search%5Border%5D=created_at:desc&search%5Bfilter_float_price:to%5D=16500&search%5Bfilter_enum_number_of_rooms_string%5D%5B0%5D=dvuhkomnatnye')


def get_new_homes():
    logging.info(f"{datetime.datetime.now()} - Start parsing homes")
    res = request('get', olx)
    soup = bs4.BeautifulSoup(res.content, features="html.parser")

    list_of_homes = soup.find(class_='css-j0t2x2').find_all(class_='css-1g5933j')

    new_homes = []
    first_home_at_list = ''
    for idx, home in enumerate(list_of_homes):

        title = home.find(class_='css-u2ayx9').a.h4.contents[0]
        link = 'https://www.olx.ua' + home.find(class_='css-u2ayx9').a['href']
        price = home.find(class_='css-uj7mm0').contents[0]

        if not database.check_and_add_home(link, title, price):
            description, imgs_urls = get_home_details(link)
            home_dict = {
                'site': 'olx',
                'title': title,
                'link': link,
                'price': price,
                'description': description,
                'images': imgs_urls
            }

            new_homes.append(home_dict)

    logging.info(f"{datetime.datetime.now()} - OLX - Found {len(new_homes)} new homes")
    return new_homes


def get_images(url):
    # Створити ім'я файлу з назви URL (можна зробити унікальне або взяти ID)
    filename = url.split("/files/")[1].split("/")[0] + ".jpg"
    filename = os.path.join('tmp', filename)

    # Завантажити зображення
    response = requests.get(url.split(';')[0])
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        logging.info(f"Зображення збережено як {filename}")
        return filename
    else:
        logging.info(f"Помилка завантаження: {response.status_code}")
        return None


def get_home_details(url):
    res = request('get', url)
    soup = bs4.BeautifulSoup(res.content, features="html.parser")

    description = soup.find(class_='css-19duwlz').text
    imgs = soup.find_all(class_='swiper-zoom-container')
    imgs_urls = []
    for imgs in imgs:
        img = imgs.find('img')['src']
        imgs_urls.append(img)

    return description, imgs_urls
