import os
import telebot
import threading
import time
from dotenv import load_dotenv

# Carregar variáveis de ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Mensagem de urgência (busca do Railway)
START_MESSAGE = os.getenv("START_MESSAGE")

# Mensagem de pagamento (busca do Railway)
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

# Lista para armazenar os usuários que já interagiram com o bot
users = set()

# Função para enviar a mensagem "Última Chamada" automaticamente
def send_urgent_message():
    while True:
       time.sleep(60)  # Espera 1 minuto antes de enviar de novo
        for user_id in users:
            bot.send_message(user_id, START_MESSAGE)

# Iniciar a thread para mensagens automáticas
threading.Thread(target=send_urgent_message, daemon=True).start()

# Quando alguém digita /start, adiciona na lista de usuários e envia as mensagens
@bot.message_handler(commands=['start'])
def send_checkout(message):
    user_id = message.chat.id
    users.add(user_id)  # Adiciona o usuário à lista de notificações futuras

    # Enviar mensagem de urgência
    bot.send_message(user_id, START_MESSAGE)

    # Enviar mensagem de pagamento
    bot.send_message(user_id, CHECKOUT_MESSAGE)

# Manter o bot rodando
bot.polling()
