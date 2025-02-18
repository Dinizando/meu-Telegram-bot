import os
import telebot
import threading
import time
import logging
from datetime import datetime
from telebot.types import InputMediaPhoto
from dotenv import load_dotenv

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID do canal onde o bot enviará mensagens automáticas
ADMIN_ID_1 = os.getenv("ADMIN_ID_1")  # ID da conta dos EUA
ADMIN_ID_2 = os.getenv("ADMIN_ID_2")  # ID da conta do Brasil
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")  # Canal privado para logs do admin

bot = telebot.TeleBot(TOKEN)

# Mensagens do Railway
AUTOMATIC_MESSAGE = os.getenv("AUTOMATIC_MESSAGE")  # Mensagem automática no canal
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

# Lista para armazenar usuários que interagiram com o bot
users = set()
last_auto_message_time = None  # Para armazenar a última vez que a mensagem automática foi enviada

# Configurar logging para salvar conversas
logging.basicConfig(
    filename="bot_interactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8",
)

# Função para registrar mensagens no log
def log_message(user_id, user_name, text):
    log_entry = f"User {user_name} ({user_id}): {text}"
    logging.info(log_entry)
    bot.send_message(LOG_CHANNEL_ID, log_entry)  # Enviar log para canal privado do admin

# 🕒 Função para enviar mensagem automática no canal às 12h e 00h
def send_scheduled_message():
    global last_auto_message_time
    while True:
        now = datetime.now()
        if now.hour == 12 or now.hour == 0:
            if last_auto_message_time != now.date():  # Evita mensagens duplicadas no mesmo dia
                bot.send_message(CHANNEL_ID, AUTOMATIC_MESSAGE)
                last_auto_message_time = now.date()
                bot.send_message(LOG_CHANNEL_ID, "✅ Mensagem automática enviada ao canal.")

        time.sleep(3600)  # Verifica a cada hora para evitar repetições

# Iniciar a thread para mensagens automáticas
threading.Thread(target=send_scheduled_message, daemon=True).start()

# 📌 Comando /me (somente para os administradores)
@bot.message_handler(commands=["me"])
def admin_info(message):
    user_id = message.chat.id
    if str(user_id) in [ADMIN_ID_1, ADMIN_ID_2]:
        total_users = len(users)
        bot_info = bot.get_chat(CHANNEL_ID)
        members_count = bot_info.get("members_count", "Indisponível")

        response = (
            f"🔹 **Painel Administrativo** 🔹\n\n"
            f"👥 **Membros no canal**: {members_count}\n"
            f"📊 **Usuários que interagiram**: {total_users}\n"
            f"📢 **Última mensagem automática**: {last_auto_message_time}\n\n"
            f"🛠 **Comandos Disponíveis:**\n"
            f"/status - Ver usuários ativos\n"
            f"/broadcast [mensagem] - Enviar mensagem ao canal\n"
            f"/forcar_mensagem - Enviar a mensagem automática imediatamente\n"
        )
        bot.send_message(user_id, response)
    else:
        bot.send_message(user_id, "🚫 Você não tem permissão para acessar este comando.")

# 📢 Comando /broadcast (somente para administradores, envia no canal)
@bot.message_handler(commands=["broadcast"])
def send_broadcast(message):
    user_id = message.chat.id
    if str(user_id) in [ADMIN_ID_1, ADMIN_ID_2]:
        text = message.text.replace("/broadcast ", "").strip()
        if text:
            bot.send_message(CHANNEL_ID, text)
            bot.send_message(LOG_CHANNEL_ID, "📢 Mensagem enviada manualmente ao canal.")
        else:
            bot.send_message(user_id, "⚠ Use `/broadcast [sua mensagem]` para enviar no canal.")
    else:
        bot.send_message(user_id, "🚫 Você não tem permissão para usar este comando.")

# 📌 Comando /forcar_mensagem - Envia a mensagem automática imediatamente no canal
@bot.message_handler(commands=["forcar_mensagem"])
def force_send_message(message):
    user_id = message.chat.id
    if str(user_id) in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(CHANNEL_ID, AUTOMATIC_MESSAGE)
        bot.send_message(LOG_CHANNEL_ID, "⚡ Mensagem automática enviada manualmente.")
    else:
        bot.send_message(user_id, "🚫 Você não tem permissão para usar este comando.")

# 📊 Comando /status - Mostra usuários que interagiram
@bot.message_handler(commands=["status"])
def send_status(message):
    user_id = message.chat.id
    if str(user_id) in [ADMIN_ID_1, ADMIN_ID_2]:
        if users:
            status_message = "📊 **Usuários que interagiram com o bot:**\n\n"
            for user in users:
                status_message += f"👤 User ID: {user}\n"
        else:
            status_message = "⚠️ Nenhum usuário interagiu com o bot ainda."

        bot.send_message(user_id, status_message)
    else:
        bot.send_message(user_id, "🚫 Você não tem permissão para ver essas informações.")

# 🚀 Mantém o bot rodando
bot.polling()
