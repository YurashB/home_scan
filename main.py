import logging
import os
import sys
import threading
import time

import telebot
from dotenv import load_dotenv
from telebot import types

import database
import log
import maps
import sites.olx as olx
import sites.lun as lun
import sites.rieltor_ua as rieltor_ua
import sites.dim_ria as dim_ria


# === Налаштування логера ===
log.init_logger()
logging.info("Logger initialized")

# === Налаштування бота ===
load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# === Константи ===
CHAT_ID = -4862542990
REPEAT_INTERVAL = 200


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.reply_to(message, f"Привіт! Я бот на Telebot. Ваш chat_id: {CHAT_ID}")


@bot.message_handler(commands=['log'])
def send_welcome(message):
    with open('bot.log', 'r') as f:
        lines = f.readlines()
        log = lines[-3:]
        bot.reply_to(message, str(log))

@bot.message_handler(func=lambda msg: msg.text and msg.text.lower().startswith("delete"))
def handle_street_message(message):
    n = message.text.split(" ")[1]
    try:
        database.delete_last_n_rows(n)
        bot.reply_to(message, f"Deleted last {n} rows from the database.")
    except Exception as e:
        bot.reply_to(message, f"❌ Не вийшло розрахувати маршрут: {e}")

# === Обробка повідомлень з вулицями ===
@bot.message_handler(func=lambda msg: msg.text and msg.text.lower().startswith("вул"))
def handle_street_message(message):
    street_name = message.text.strip()
    try:
        maps_info = maps.get_maps_info(street_name)
        caption = (
            f"Capgemini: {maps_info[0]}, час: {maps_info[1]}\n"
            f"Betonenergo: {maps_info[2]}, час: {maps_info[3]}"
        )
        bot.send_photo(chat_id=message.chat.id, photo=maps_info[4], caption=caption, reply_to_message_id=message.id)
    except Exception as e:
        bot.reply_to(message, f"❌ Не вийшло розрахувати маршрут: {e}")


# === Основна логіка перевірки нових квартир ===
def check_data():
    global CHAT_ID

    if CHAT_ID == 0:
        logging.info("CHAT_ID не заданий. Очікування оновлення...")
        schedule_next_check()
        return

    # olx_homes = olx.get_new_homes()
    # lun_homes = lun.get_new_homes()
    # rieltor_homes = rieltor_ua.get_new_homes()
    dim_ria_homes = dim_ria.get_new_homes()

    new_homes = dim_ria_homes

    if not new_homes:
        schedule_next_check()
        return

    for home in new_homes:
        site = home['site']
        title = home['title']
        link = home['link']
        price = home['price']
        imgs = home['images']

        if site in {'lun', 'rieltor_ua'}:
            title = f"Вул. {title}, Київ"

        route_info_text = ""
        try:
            maps_info = maps.get_maps_info(title)
            route_info_text = (
                f"Capgemini: {maps_info[0]}, час: {maps_info[1]}\n"
                f"Betonenergo: {maps_info[2]}, час: {maps_info[3]}"
            )
            location_image = maps_info[4]
            if location_image:
                imgs[0] = location_image
        except Exception as e:
            logging.warning(f"Не вдалося отримати маршрут для '{title}': {e}")

        caption = (
            f"*{title}*\n"
            f"💰 Ціна: {price}\n"
            f"👉 *{site}*:[Переглянути оголошення]({link})\n"
            f"{route_info_text}"
        )

        media_group = []
        for i, img_url in enumerate(imgs):
            if i == 0:
                media_group.append(types.InputMediaPhoto(media=img_url, caption=caption, parse_mode="Markdown"))
            else:
                media_group.append(types.InputMediaPhoto(media=img_url))

        try:
            bot.send_media_group(chat_id=CHAT_ID, media=media_group[:9])  # 10 cause exceptions
            # TODO check if 31 can be
            time.sleep(61)
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"❌ Помилка при надсиланні: {e}\nLink: {link}\nTitle: {title}")

    time.sleep(REPEAT_INTERVAL)
    schedule_next_check()


def schedule_next_check():
    threading.Timer(REPEAT_INTERVAL, check_data).start()


# === Старт першої перевірки ===
threading.Timer(10, check_data).start()

# === Запуск бота ===
logging.info("Bot started")
bot.polling()
