import os
import telebot
import threading
import time
from dotenv import load_dotenv

# Carregar variáveis de ambiente do Railway
load_dotenv()

# Obter Token do Bot
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Obter mensagens das variáveis do Railway
START_MESSAGE = os.getenv("START_MESSAGE")  # Mensagem de urgência
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")  # Mensagem de pagamento

# Lista para armazenar os usuários que já interagiram com o bot
users = set()

# Função para enviar a mensagem de urgência "Última Chamada!" automaticamente após 24h
def send_urgent_message():
    while True:
        time.sleep(86400)  # Espera 24 horas (86400 segundos)

        for user_id in users:
            bot.send_message(user_id, START_MESSAGE)

# Iniciar a thread para mensagens automáticas
threading.Thread(target=send_urgent_message, daemon=True).start()

# Quando o usuário digita /start, adiciona na lista e envia apenas a mensagem de checkout
@bot.message_handler(commands=['start'])
def send_checkout(message):
    user_id = message.chat.id
    users.add(user_id)  # Adiciona o usuário à lista de notificações futuras
    bot.send_message(user_id, CHECKOUT_MESSAGE)  # Envia APENAS a mensagem de pagamento

# Mantém o bot rodando
bot.polling()
