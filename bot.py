import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ (ЗАМЕНИ НА СВОИ ДАННЫЕ!) ===
TELEGRAM_TOKEN = "8846781149:AAHTqscRWbBgHjyiFfCM512vWfYi7Dy5y14"
ANYTHINGLLM_API_URL = "http://localhost:3001/api/v1/workspace/ragg1_bot/chat"
ANYTHINGLLM_API_TOKEN = "60E83B7-9J04MRD-J2859BD-QJA96SP"
AUTH_PASSWORD = "7777"  # Простой пароль для доступа
# ========================================

# Словарь для хранения авторизованных пользователей
authorized_users = {}

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Функция проверки пароля
async def check_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in authorized_users:
        await update.message.reply_text("🔐 Доступ закрыт. Введите пароль для авторизации командой /auth <пароль>")
        return False
    return True

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤖 Привет! Я RAG-бот. Введи пароль командой /auth {AUTH_PASSWORD}")

# Обработчик команды /auth
async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.args and context.args[0] == AUTH_PASSWORD:
        authorized_users[user_id] = True
        await update.message.reply_text("✅ Авторизация успешна! Теперь задавай свои вопросы.")
    else:
        await update.message.reply_text("❌ Неверный пароль.")

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update, context):
        return

    user_message = update.message.text
    await update.message.reply_text("🤔 Думаю над ответом...")

    headers = {
        "Authorization": f"Bearer {ANYTHINGLLM_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
    "message": user_message,
    "mode": "query",
    "stream": False
}

    try:
        response = requests.post(ANYTHINGLLM_API_URL, json=data, headers=headers, timeout=30)
        if response.status_code == 200:
            ai_response = response.json().get("textResponse", "Не удалось получить ответ.")
            await update.message.reply_text(ai_response)
        else:
            await update.message.reply_text(f"❌ Ошибка API: {response.status_code}")

    except Exception as e:
        logging.error(f"Ошибка при запросе к AnythingLLM: {e}")
        await update.message.reply_text("⚠️ Произошла внутренняя ошибка. Попробуй позже.")

# Точка входа
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("auth", auth))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Бот запущен и готов к работе!")
    app.run_polling()
