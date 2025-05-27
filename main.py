import logging
import os
import sys
import threading
import time
import schedule
import telebot
from dotenv import load_dotenv
from telebot import types

import maps
import olx


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


load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
CHAT_ID = -4862542990


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.reply_to(message, "Привіт! Я бот на Telebot " + str(CHAT_ID))

@bot.message_handler(commands=['search'])
def send_welcome(message):
    check_data()


@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith("вул"))
def handle_street_message(message):
    street_name = message.text.strip()
    try:
        maps_info = maps.get_maps_info(street_name)
    except Exception as e:
        bot.reply_to(message, f"❌ Не вийшло розрахувати маршрут: {e}")
        return
    text = (f"Capgemini: {maps_info[0]}, час: {maps_info[1]}\n"
            f"Betonenergo: {maps_info[2]}, час: {maps_info[3]}")
    bot.reply_to(message, text)


def check_data():
    global CHAT_ID
    if CHAT_ID == 0:

        logging.info("CHAT_ID не заданий")
        threading.Timer(300, check_data).start()
        return

    new_homes = olx.get_new_homes()

    if not new_homes:

        threading.Timer(300, check_data).start()
        return

    for idx, home in enumerate(new_homes):
        if idx > 5: break
        title = home['title']
        link = home['link']
        price = home['price']
        description = home['description']
        imgs_urls = home['images']

        caption = f"*{title}*\n💰 Ціна: {price}\n👉 [Переглянути оголошення]({link})"

        media = []
        for i, img_url in enumerate(imgs_urls):
            if i == 0:
                media.append(types.InputMediaPhoto(media=img_url, caption=caption, parse_mode="Markdown"))
            else:
                media.append(types.InputMediaPhoto(media=img_url))

        try:
            print(f"Found new home: {title}, link: {link}, price: {price}")
            bot.send_media_group(chat_id=CHAT_ID, media=media)
            time.sleep(31)
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"❌ Помилка при надсиланні: {e}")

    # 🕐 Запускаємо повторно через 5 хв
    threading.Timer(300, check_data).start()


threading.Timer(10, check_data).start()

logging.info('Start bot')
bot.polling()
