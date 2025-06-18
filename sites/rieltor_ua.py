import datetime
import logging

import bs4
from requests import request
import database

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"}
site = (
    'https://rieltor.ua/flats-rent/2-rooms/?district%5B0%5D=81&district%5B1%5D=85&district%5B2%5D=76&district%5B3%5D=82&district%5B4%5D=78&district%5B5%5D=86&district%5B6%5D=80&district%5B7%5D=79&price_max=16500&radius=20&sort=bycreated#9.6/50.444/30.5336')


def get_new_homes():
    res = request('get', site, headers=headers)
    soup = bs4.BeautifulSoup(res.content, features="html.parser")

    list_of_homes = soup.find(class_='catalog-items-container').find_all(class_='catalog-card')

    new_homes = []
    for idx, home in enumerate(list_of_homes):

        title = home.select_one('.catalog-card-address').get_text(strip=True)
        link = home.select_one('a.catalog-card-media')['href']
        price = home.select_one('.catalog-card-price-title').get_text(strip=True)
        description = ''

        imgs = home.select('.offer-photo-slider-slide img')
        imgs_urls = []
        for img in imgs:
            if 'src' in img.attrs:
                high_res_url = img['src'].replace('crop/400x300/', 'crop/1200x900/')
                imgs_urls.append(high_res_url)

        if not database.check_and_add_home(link, title, price):
            home_dict = {
                'site': 'rieltor_ua',
                'title': title,
                'link': link,
                'price': price,
                'description': description,
                'images': imgs_urls[:9]
            }

            new_homes.append(home_dict)

    logging.info(f"{datetime.datetime.now()} - Rieltor UA - Found {len(new_homes)} new homes")
    return new_homes


if __name__ == "__main__":
    new_homes = get_new_homes()
    for home in new_homes:
        print(home)
