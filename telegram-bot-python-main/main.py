import os
import telebot
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Obter token e mensagens
TOKEN = os.getenv("TELEGRAM_TOKEN")
START_MESSAGE = os.getenv("START_MESSAGE")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

bot = telebot.TeleBot(TOKEN)

# Enviar mensagem inicial antes do usuário digitar /start
def send_initial_message(user_id):
    bot.send_message(user_id, START_MESSAGE)

# Responder ao comando /start com a mensagem de pagamento
@bot.message_handler(commands=['start'])
def send_checkout(message):
    bot.send_message(message.chat.id, CHECKOUT_MESSAGE)

# Manter o bot rodando
bot.polling()
