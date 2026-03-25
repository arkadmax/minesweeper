import os
import json
import asyncio
from flask import Flask, request
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
WEB_APP_URL = os.environ.get('WEB_APP_URL', 'https://your-domain.com/minesweeper-tma.html')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
PORT = int(os.environ.get('PORT',10000))

flask_app = Flask(__name__)
app = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
 keyboard = [
 [KeyboardButton(
 text="🎮 Играть в Сапера",
 web_app=WebAppInfo(url=WEB_APP_URL)
 )]
 ]
 reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
 await update.message.reply_text(
 "💣<b>Сапер</b>\n\nКлассическая игра в сапера!\n\nНажмите кнопку ниже, чтобы начать играть:",
 reply_markup=reply_markup,
 parse_mode='HTML'
 )


async def url_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
 await update.message.reply_text(
 f"URL игры:\n<code>{WEB_APP_URL}</code>\n\nWEBHOOK_URL:\n<code>{WEBHOOK_URL or 'не задан'}</code>",
 parse_mode='HTML'
 )


async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
 data = update.message.web_app_data.data
 if data:
 try:
 game_data = json.loads(data)
 await update.message.reply_text(
 f"Игра завершена!\nУровень: {game_data.get('level')}\n"
 f"Время: {game_data.get('time')} сек\n"
 f"Результат: {'Победа!🎉' if game_data.get('won') else 'Поражение💥'}"
 )
 except Exception as e:
 print(f"Error: {e}")


async def webapp_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
 if update.message and update.message.web_app_data:
 await webapp_data(update, context)


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("url", url_command))
app.add_handler(MessageHandler(filters.ALL, webapp_data_handler))


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
 return '✅ Minesweeper Bot Running!'


if __name__ == '__main__':
 if not BOT_TOKEN:
 print("❌ Ошибка: TELEGRAM_BOT_TOKEN не найден в .env")
 exit(1)
    
 print(f"✅ Bot token загружен")
 print(f"📱 Web App URL: {WEB_APP_URL}")
    
 if WEBHOOK_URL:
 print(f"🌐 Webhook URL: {WEBHOOK_URL}")
 print(f"🚀 Бот запущен через webhook...")
        
 async def set_webhook():
 await app.bot.set_webhook(WEBHOOK_URL)
 print(f"✅ Webhook установлен")
        
 asyncio.run(set_webhook())
 flask_app.run(host='0.0.0.0', port=PORT)
 else:
 print(f"🚀 Бот запущен через polling...")
 app.run_polling(drop_pending_updates=True)
