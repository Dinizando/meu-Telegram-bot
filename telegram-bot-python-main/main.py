import os
import telebot
import threading
import time
import logging
from datetime import datetime
from telebot.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from dotenv import load_dotenv

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID do canal para envio de mensagens automáticas
ADMIN_ID_1 = int(os.getenv("ADMIN_ID_1"))  # ID da conta dos EUA
ADMIN_ID_2 = int(os.getenv("ADMIN_ID_2"))  # ID da conta do Brasil
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))  # Canal privado para logs do admin
VIP_GROUP_LINK = os.getenv("VIP_GROUP_LINK")  # Link do grupo VIP

bot = telebot.TeleBot(TOKEN)

# Lista de usuários registrados
users = set()
pending_payments = {}  # Dicionário para armazenar usuários aguardando confirmação de pagamento
last_auto_message_time = None  # Controla a última mensagem automática enviada

# Configurar logging para registrar interações
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

# Comando /broadcast para enviar mensagens no canal
@bot.message_handler(commands=["broadcast"])
def broadcast_text(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        text = message.text.replace("/broadcast ", "").strip()
        if text:
            bot.send_message(CHANNEL_ID, text)
            bot.send_message(message.chat.id, "📢 Mensagem enviada ao canal.")
        else:
            bot.send_message(message.chat.id, "⚠ Envie a mensagem no formato `/broadcast <texto>` ou envie uma **foto/vídeo/documento** com legenda.")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

# Permitir que o bot envie fotos, vídeos e documentos no /broadcast
@bot.message_handler(content_types=["photo", "video", "document"])
def broadcast_media(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        caption = message.caption if message.caption else ""
        
        if message.photo:
            bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=caption)
            bot.send_message(message.chat.id, "📢 Foto enviada ao canal.")
        elif message.video:
            bot.send_video(CHANNEL_ID, message.video.file_id, caption=caption)
            bot.send_message(message.chat.id, "📢 Vídeo enviado ao canal.")
        elif message.document:
            bot.send_document(CHANNEL_ID, message.document.file_id, caption=caption)
            bot.send_message(message.chat.id, "📢 Documento enviado ao canal.")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

# Mantém o bot rodando
bot.polling()
