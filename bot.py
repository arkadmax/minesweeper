import os
import json
import asyncio
from flask import Flask, request
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
WEB_APP_URL = os.environ.get('WEB_APP_URL', 'https://arkadmax.github.io/minesweeper/minesweeper-tma.html')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
PORT = int(os.environ.get('PORT',10000))

flask_app = Flask(__name__)
app = Application.builder().token(BOT_TOKEN).build()

async def start(update, context):
    keyboard = [[KeyboardButton(text='PLAY', web_app=WebAppInfo(url=WEB_APP_URL))]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('SAPER', reply_markup=reply_markup, parse_mode='HTML')

async def url_cmd(update, context):
    await update.message.reply_text(f'URL: {WEB_APP_URL}', parse_mode='HTML')

async def webapp_handler(update, context):
    if update.message and update.message.web_app_data:
        data = update.message.web_app_data.data
        if data:
            try:
                game_data = json.loads(data)
                await update.message.reply_text(f'Game over! Level: {game_data.get("level")}, Time: {game_data.get("time")}s')
            except:
                pass

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('url', url_cmd))
app.add_handler(MessageHandler(filters.ALL, webapp_handler))

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(force=True), app.bot)
        async def process():
            async with app:
                await app.process_update(update)
        asyncio.run(process())
    return 'OK'

@flask_app.route('/')
def index():
    return 'OK'

if __name__ == '__main__':
    if not BOT_TOKEN:
        print('ERROR: TOKEN MISSING')
        exit(1)
    print(f'TOKEN: OK')
    print(f'URL: {WEB_APP_URL}')
    if WEBHOOK_URL:
        print(f'WEBHOOK: {WEBHOOK_URL}')
        asyncio.run(app.bot.set_webhook(WEBHOOK_URL))
        flask_app.run(host='0.0.0.0', port=PORT)
    else:
        print('POLLING')
        app.run_polling(drop_pending_updates=True)