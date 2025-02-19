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
CHANNEL_ID = os.getenv("CHANNEL_ID")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
ADMIN_ID_1 = os.getenv("ADMIN_ID_1")
ADMIN_ID_2 = os.getenv("ADMIN_ID_2")
VIP_GROUP_LINK = os.getenv("VIP_GROUP_LINK")

# Converter IDs para inteiros (evita erro de None)
try:
    ADMIN_ID_1 = int(ADMIN_ID_1) if ADMIN_ID_1 else None
    ADMIN_ID_2 = int(ADMIN_ID_2) if ADMIN_ID_2 else None
    CHANNEL_ID = int(CHANNEL_ID) if CHANNEL_ID else None
    LOG_CHANNEL_ID = int(LOG_CHANNEL_ID) if LOG_CHANNEL_ID else None
except ValueError:
    raise ValueError("Erro ao converter IDs. Verifique as variáveis de ambiente.")

bot = telebot.TeleBot(TOKEN)

# Mensagens armazenadas no Railway
AUTOMATIC_MESSAGE = os.getenv("AUTOMATIC_MESSAGE")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

# Lista para armazenar os usuários que interagiram com o bot
users = set()
pending_payments = {}

# Configurar logging para salvar interações
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
    bot.send_message(LOG_CHANNEL_ID, log_entry)

# Enviar mensagem automática no canal às 12h e 00h
def scheduled_message():
    global last_auto_message_time
    while True:
        try:
            now = datetime.now()
            if now.hour in [12, 0] and now.date() != last_auto_message_time:
                bot.send_message(CHANNEL_ID, AUTOMATIC_MESSAGE)
                bot.send_message(LOG_CHANNEL_ID, "📢 Mensagem automática enviada ao canal.")
                last_auto_message_time = now.date()
            time.sleep(60)
        except Exception as e:
            bot.send_message(LOG_CHANNEL_ID, f"⚠ Erro ao enviar mensagem automática: {e}")
            time.sleep(60)

# Iniciar a thread de envio automático
threading.Thread(target=scheduled_message, daemon=True).start()

# 🚀 **Comando /start corrigido**
@bot.message_handler(commands=["start"])
def send_checkout(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name

    # Se for admin, apenas confirma a autenticação
    if user_id in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(user_id, "✅ Você está autenticado como ADMIN.")
        return

    # Adiciona usuário na lista de interações
    if user_id not in users:
        users.add(user_id)
        log_message(user_id, user_name, "/start")

        # Envia notificação para os administradores
        bot.send_message(ADMIN_ID_1, f"📌 Novo usuário interagiu! 🆔 ID: {user_id} 👤 Nome: {user_name}")
        bot.send_message(ADMIN_ID_2, f"📌 Novo usuário interagiu! 🆔 ID: {user_id} 👤 Nome: {user_name}")

    # 🚀 **Correção da separação das mensagens**
    bot.send_message(user_id, WELCOME_MESSAGE)
    time.sleep(1)

    bot.send_message(user_id, VIP_BENEFITS)
    time.sleep(2)

    bot.send_message(user_id, CHECKOUT_MESSAGE)
    time.sleep(1)

    bot.send_message(user_id, "💳 Envie o comprovante de pagamento aqui para validação.")

# Comando /me para admins verificarem estatísticas
@bot.message_handler(commands=["me"])
def admin_status(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(
            message.chat.id,
            f"📊 Estatísticas do Bot:\n👥 Usuários interagidos: {len(users)}\n📨 Última mensagem automática enviada: {last_auto_message_time}",
        )
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

# Enviar mídia (foto ou vídeo) no canal
@bot.message_handler(content_types=["photo", "video"])
def handle_media(message):
    user_id = message.chat.id

    if user_id not in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(user_id, "🚫 Você não tem permissão para enviar mídia.")
        return

    caption = message.caption if message.caption else "📢 Nova atualização!"

    try:
        if message.photo:
            bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=caption)
        elif message.video:
            bot.send_video(CHANNEL_ID, message.video.file_id, caption=caption)

        bot.send_message(user_id, "✅ Mídia enviada ao canal!")
    except Exception as e:
        bot.send_message(user_id, f"⚠ Erro ao enviar mídia: {e}")

# Comando para admins enviarem mensagens personalizadas
@bot.message_handler(commands=["msg"])
def send_admin_message(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        try:
            parts = message.text.split(" ", 2)
            target_user_id = int(parts[1])
            admin_message = parts[2]

            bot.send_message(target_user_id, f"📩 Mensagem do ADMIN:\n{admin_message}")
            bot.send_message(message.chat.id, "✅ Mensagem enviada com sucesso.")
        except:
            bot.send_message(message.chat.id, "⚠ Erro: Use o formato `/msg <user_id> <mensagem>`")

# Comando para aprovar pagamento
@bot.message_handler(commands=["aprovar"])
def confirmar_pagamento(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        try:
            parts = message.text.split(" ", 1)
            target_user_id = int(parts[1])

            if target_user_id in pending_payments:
                bot.send_message(
                    target_user_id,
                    f"🎉 Parabéns! Seu pagamento foi confirmado. Aqui está seu acesso ao VIP: {VIP_GROUP_LINK}",
                )
                bot.send_message(message.chat.id, f"✅ Acesso VIP liberado para {target_user_id}.")
                del pending_payments[target_user_id]
            else:
                bot.send_message(message.chat.id, "⚠ Este usuário não tem pagamento pendente.")
        except:
            bot.send_message(message.chat.id, "⚠ Erro: Use `/aprovar <user_id>`")

# Rodar o bot
bot.polling()
