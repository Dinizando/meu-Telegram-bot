import os
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load token and messages
TOKEN = os.getenv("TELEGRAM_TOKEN")
START_MESSAGE = os.getenv("START_MESSAGE")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, START_MESSAGE)  # Responde com a mensagem configurada

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.polling()
