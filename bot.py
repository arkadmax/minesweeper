# pip install python-telegram-bot flask python-dotenv
import os
import json
import asyncio
from flask import Flask, request
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# Токен бота из .env
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# URL вашего Mini App (после деплоя)
WEB_APP_URL = os.environ.get('WEB_APP_URL', 'https://your-domain.com/minesweeper-tma.html')

# URL для webhook (для продакшена)
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
PORT = int(os.environ.get('PORT', 5000))

# Flask приложение
flask_app = Flask(__name__)

# Создаём приложение Telegram
app = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - показывает кнопку запуска игры"""
    
    keyboard = [
        [KeyboardButton(
            text="🎮 Играть в Сапера",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "💣 <b>Сапер</b>\n\n"
        "Классическая игра в сапера!\n\n"
        "Нажмите кнопку ниже, чтобы начать играть:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка данных из Mini App"""
    data = update.message.web_app_data.data
    if data:
        try:
            game_data = json.loads(data)
            await update.message.reply_text(
                f"Игра завершена!\n"
                f"Уровень: {game_data.get('level')}\n"
                f"Время: {game_data.get('time')} сек\n"
                f"Результат: {'Победа! 🎉' if game_data.get('won') else 'Поражение 💥'}"
            )
        except:
            pass

# Обработчики
app.add_handler(CommandHandler("start", start))

# Фильтр для web_app_data
async def webapp_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.web_app_data:
        await webapp_data(update, context)

app.add_handler(MessageHandler(filters.ALL, webapp_data_handler))

# Webhook endpoint для продакшена
@flask_app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(force=True), app.bot)
        asyncio.run(app.process_update(update))
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
    
    # Если есть WEBHOOK_URL - используем webhook (продакшн)
    if WEBHOOK_URL:
        print(f"🌐 Webhook URL: {WEBHOOK_URL}")
        print(f"🚀 Бот запущен через webhook...")
        
        # Устанавливаем webhook при запуске
        async def set_webhook():
            await app.bot.set_webhook(WEBHOOK_URL)
            print(f"✅ Webhook установлен")
        
        asyncio.run(set_webhook())
        
        # Запускаем Flask
        flask_app.run(host='0.0.0.0', port=PORT)
    else:
        # Иначе polling (локальная разработка)
        print(f"🚀 Бот запущен через polling...")
        app.run_polling(drop_pending_updates=True)
