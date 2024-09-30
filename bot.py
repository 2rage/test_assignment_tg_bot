import os
import logging
import time
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

user_data = {}
cached_rate = None
cached_time = 0
CACHE_TIMEOUT = 60


async def start(update: Update, context):
    keyboard = [['/usd']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Добрый день. Как вас зовут?', reply_markup=reply_markup)


async def handle_name(update: Update, context):
    chat_id = update.message.chat_id
    name = update.message.text
    user_data[chat_id] = name
    await update.message.reply_text(f'Рад знакомству, {name}! Теперь вы можете запросить курс доллара, используя команду /usd.')


async def usd(update: Update, context):
    chat_id = update.message.chat_id
    name = user_data.get(chat_id, 'пользователь')
    exchange_rate = get_cached_exchange_rate()
    if exchange_rate:
        await update.message.reply_text(f'{name}, курс доллара сегодня: {exchange_rate}р')
    else:
        await update.message.reply_text('Не удалось получить курс доллара. Попробуйте позже.')


def get_cached_exchange_rate():
    global cached_rate, cached_time
    current_time = time.time()
    if current_time - cached_time > CACHE_TIMEOUT:
        exchange_rate = get_exchange_rate()
        if exchange_rate:
            cached_rate = exchange_rate
            cached_time = current_time
        return exchange_rate
    else:
        return cached_rate


def get_exchange_rate():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        response = requests.get(url)
        data = response.json()
        return data['rates']['RUB']
    except Exception as e:
        logging.error(f"Ошибка при получении курса доллара: {e}")
        return None


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))
    application.add_handler(CommandHandler('usd', usd))
    application.run_polling()
