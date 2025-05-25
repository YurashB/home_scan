import os
import threading
import time
import schedule
import telebot
from dotenv import load_dotenv
from telebot import types

import maps
import olx

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
CHAT_ID = -4862542990


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.reply_to(message, "Привіт! Я бот на Telebot " + str(CHAT_ID))


@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith("вул"))
def handle_street_message(message):
    street_name = message.text.strip()
    maps_info = maps.get_maps_info(street_name)
    text = (f"Capgemini: {maps_info[0]}, час: {maps_info[1]}\n"
            f"Betonenergo: {maps_info[2]}, час: {maps_info[3]}")
    bot.reply_to(message, text)


def check_data():
    global CHAT_ID
    if CHAT_ID == 0:
        print("CHAT_ID не заданий")
        threading.Timer(300, check_data).start()
        return

    new_homes = olx.get_new_homes()

    if not new_homes:

        threading.Timer(300, check_data).start()
        return

    for home in new_homes:
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
            bot.send_media_group(chat_id=CHAT_ID, media=media)
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"❌ Помилка при надсиланні: {e}")

    # 🕐 Запускаємо повторно через 5 хв
    threading.Timer(300, check_data).start()


threading.Timer(10, check_data).start()
print('Start bot')
bot.polling()
