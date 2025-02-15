import os
import telebot
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Mensagens
START_MESSAGE = os.getenv("START_MESSAGE")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

# Mensagem automática antes do /start
WELCOME_MESSAGE = """🔥 Última Chamada! 🔥

🔑 Conteúdos raros e exclusivos te esperam no nosso Canal VIP! 💎

⏰ Garanta agora ou perca para sempre! 🚨

👉🏻👉🏻 Digite /start para continuar"""

# Enviar mensagem inicial antes do usuário digitar /start
@bot.message_handler(func=lambda message: True, content_types=['new_chat_members'])
def send_welcome(message):
    bot.send_message(message.chat.id, WELCOME_MESSAGE)

# Comando /start
@bot.message_handler(commands=['start'])
def send_initial_message(message):
    bot.send_message(message.chat.id, START_MESSAGE)
    bot.send_message(message.chat.id, CHECKOUT_MESSAGE)

# Manter o bot rodando
bot.polling()
