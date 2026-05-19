import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from bot.models import DetectionLog, FindLog
from asgiref.sync import sync_to_async

import py3langid as langid
from diller import langs

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
#abiyamaha76-bit

TOKEN = "8288045739:AAGt35sPQeDnzehQIUuoxKXEkAmImEtJyGA"

main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🔍 Detect Language"), KeyboardButton("🌐 Find Language")],
        [KeyboardButton("❓ Help")]
    ],
    resize_keyboard=True
)

st_text = (
    "Hi! I'm a bot that can recognize languages.\n"
    "You can send me any text, and I will automatically detect which language it is written in.\n\n"
    "Use the buttons below or commands:\n"
    "/detect - detect language\n"
    "/find - find language in database\n"
    "/help - show commands\n"
)

help_text = (
    "Available commands:\n\n"
    "/start – welcome message\n"
    "/detect – activate language detection mode\n"
    "/find – search language in database\n"
    "/help – show this message"
)


def get_username(update: Update):
    user = update.effective_user
    if user.username:
        return f"@{user.username}"
    elif user.last_name:
        return f"{user.first_name} {user.last_name}"
    return user.first_name or "Unknown"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(st_text, reply_markup=main_keyboard)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_text, reply_markup=main_keyboard)


async def detect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'detect'
    await update.message.reply_text("Send me text to detect language 👇")


async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'find'
    await update.message.reply_text("Send me language to find in our data 👇")


async def process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "🔍 Detect Language":
        context.user_data['mode'] = 'detect'
        await update.message.reply_text("Send me text to detect language 👇")
        return
    elif text == "🌐 Find Language":
        context.user_data['mode'] = 'find'
        await update.message.reply_text("Send me language to find in our data 👇")
        return
    elif text == "❓ Help":
        await update.message.reply_text(help_text, reply_markup=main_keyboard)
        return

    mode = context.user_data.get('mode')

    if not text:
        await update.message.reply_text("Please enter some text.")
        return

    if mode == 'detect':
        lang_code, _ = langid.classify(text)
        lang = langs.get(lang_code, "Unknown")

        await sync_to_async(DetectionLog.objects.create)(
            user_id=update.effective_user.id,
            username=get_username(update),
            input_text=text,
            detected=lang
        )

        await update.message.reply_text(f"This is {lang} 🌍", reply_markup=main_keyboard)

    elif mode == 'find':
        found = False
        for code, name in langs.items():
            if name.lower() == text.lower():
                await update.message.reply_text(f"✅ {text} is in our list", reply_markup=main_keyboard)
                found = True
                break

        await sync_to_async(FindLog.objects.create)(
            user_id=update.effective_user.id,
            username=get_username(update),
            query=text,
            found=found
        )

        if not found:
            await update.message.reply_text(f"❌ {text} is not in our list", reply_markup=main_keyboard)

    else:
        await update.message.reply_text(
            "Please choose a mode first 👇",
            reply_markup=main_keyboard
        )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Unknown command. Use /help to see available commands.",
        reply_markup=main_keyboard
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("detect", detect))
    app.add_handler(CommandHandler("find", find))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.run_polling()

if __name__ == '__main__':
    main()