import os
import telebot
import threading
import time
import logging
from dotenv import load_dotenv

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID do canal do Telegram
ADMIN_ID = os.getenv("ADMIN_ID")  # Seu ID para receber notificações
bot = telebot.TeleBot(TOKEN)

# Mensagens do Railway
START_MESSAGE = os.getenv("START_MESSAGE")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

# Lista para armazenar os usuários que já interagiram com o bot
users = set()

# Configurar logging para salvar as interações do bot
logging.basicConfig(
    filename="bot_interactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8"
)

### ✅ Método 1: Comando para o usuário ver seu próprio ID
@bot.message_handler(commands=["meuid"])
def enviar_id(message):
    user_id = message.chat.id
    bot.send_message(user_id, f"🆔 Seu ID é: `{user_id}`", parse_mode="Markdown")

### ✅ Método 2: Capturar e armazenar automaticamente os IDs dos usuários
@bot.message_handler(func=lambda message: True)
def capturar_id(message):
    user_id = message.chat.id
    users.add(user_id)  # Adiciona o usuário na lista
    
    # Registrar no log
    logging.info(f"Novo usuário interagiu: ID {user_id} - {message.chat.first_name}")
    
    # Enviar para o ADMIN_ID uma notificação
    if ADMIN_ID:
        bot.send_message(ADMIN_ID, f"📌 Novo usuário interagiu!\n🆔 ID: `{user_id}`\n👤 Nome: {message.chat.first_name}", parse_mode="Markdown")

    bot.send_message(user_id, "✅ Seu ID foi registrado!")

# 🚀 Manter o bot rodando
bot.polling()
