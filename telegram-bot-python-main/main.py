import os
import telebot
import threading
import time
from dotenv import load_dotenv

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Mensagens do Railway
START_MESSAGE = os.getenv("START_MESSAGE")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

# Lista para armazenar os usuários que já interagiram com o bot
users = set()

# Função para enviar a mensagem de urgência a cada 24 horas
def send_urgent_message():
    while True:
        time.sleep(86400)  # 24 horas
        for user_id in users:
            bot.send_message(user_id, START_MESSAGE)

# Iniciar a thread para mensagens automáticas
threading.Thread(target=send_urgent_message, daemon=True).start()

# Comando /start para organizar as mensagens corretamente
@bot.message_handler(commands=["start"])
def send_checkout(message):
    user_id = message.chat.id
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
