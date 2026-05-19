import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

import telebot
import py3langid as langid
from diller import langs


from bot.models import DetectionLog, FindLog


TOKEN = ""
bot = telebot.TeleBot(TOKEN)

st_text = (
    "Hi! I'm a bot that can recognize languages.\n"
    "You can send me any text, and I will automatically detect which language it is written in.\n"
    "This makes it easier to understand, translate, or simply explore different languages.\n"
    "/detect\n"
    "/find\n"
    "/help\n"
)

help_text = (
    "Hello! This bot can recognize languages and check if a specific language is in the database.\n\n"
    "/start – shows a welcome message and a short description of what the bot can do.\n"
    "/detect – activates detection mode. Send any text, and the bot will identify the language.\n"
    "/find – activates search mode. Type the name of a language (e.g. English or French).\n"
    "/help – displays this help message."
)

def get_username(message):
    user = message.from_user
    if user.username:
        return f"@{user.username}"
    elif user.last_name:
        return f"{user.first_name} {user.last_name}"
    else:
        return user.first_name or "Unknown"

def detekt(message):
    if not message.text.strip():
        bot.send_message(message.chat.id, "Пожалуйста, введите текст.")
        return
    # lang_code, _ = langid.classify(message.text)
    # lang = langs.get(lang_code, "Unknown")
    lang_code, _ = langid.classify(message.text)
    lang = langs.get(lang_code, "Unknown")

    DetectionLog.objects.create(
        user_id=message.chat.id,
        username=get_username(message),
        input_text=message.text,
        detected=lang
    )

    bot.send_message(message.chat.id, f'This is {lang}')



def find_l(message):
    found = False
    for code, name in langs.items():
        if name.lower() == message.text.lower():
            bot.send_message(message.chat.id, f'{message.text} is in our list')
            found = True
            break
    FindLog.objects.create(
        user_id=message.chat.id,
        username=get_username(message),
        query=message.text,
        found=found
    )

    if not found:
        bot.send_message(message.chat.id, f'{message.text} is not in our list')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, st_text)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, help_text)


state = {}


@bot.message_handler(commands=['detect'])
def detect(message):
    state[message.chat.id] = 'detect'
    bot.send_message(message.chat.id, "Send me text to detect language")


@bot.message_handler(commands=['find'])
def find(message):
    state[message.chat.id] = 'find'
    bot.send_message(message.chat.id, 'Send me language to find in our data')


@bot.message_handler(content_types=['text'])
def process(message):
    mode = state.get(message.chat.id)
    if mode == 'detect':
        detekt(message)
    elif mode == 'find':
        find_l(message)
    else:
        bot.send_message(message.chat.id, "Choose a command first: /detect or /find")


if __name__ == '__main__':
    bot.infinity_polling()
