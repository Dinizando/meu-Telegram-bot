import os
import telebot
import threading
import time
from dotenv import load_dotenv

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID do canal do Telegram
ADMIN_ID = os.getenv("ADMIN_ID")  # ID do administrador

bot = telebot.TeleBot(TOKEN)

# Mensagens do Railway
START_MESSAGE = os.getenv("START_MESSAGE")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

# Lista para armazenar os usuários que já interagiram com o bot
users = set()

# Comando /start para organizar as mensagens corretamente
@bot.message_handler(commands=["start"])
def send_checkout(message):
    user_id = message.chat.id
    
    if str(user_id) == ADMIN_ID:
        bot.send_message(user_id, "✅ Você está autenticado como ADMIN.")
    else:
        users.add(user_id)  # Adiciona o usuário à lista de notificações futuras
    
        # Envia a mensagem de boas-vindas
        bot.send_message(user_id, WELCOME_MESSAGE)

        # Envia os benefícios do VIP em um bloco separado
        bot.send_message(user_id, VIP_BENEFITS)

        # Aguarda 2 segundos antes de enviar o checkout
        time.sleep(2)

        # Envia o checkout
        bot.send_message(user_id, CHECKOUT_MESSAGE)

# Mantém o bot rodando
bot.polling()
