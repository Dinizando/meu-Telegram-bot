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
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID do canal para envio de mensagens automáticas
ADMIN_ID_1 = int(os.getenv("ADMIN_ID_1"))  # ID da conta dos EUA
ADMIN_ID_2 = int(os.getenv("ADMIN_ID_2"))  # ID da conta do Brasil
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))  # Canal privado para logs do admin
VIP_GROUP_LINK = os.getenv("VIP_GROUP_LINK")  # Link do grupo VIP

bot = telebot.TeleBot(TOKEN)

# Mensagens configuradas no Railway
AUTOMATIC_MESSAGE = os.getenv("AUTOMATIC_MESSAGE")  # Mensagem automática no canal
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")
VIP_INVITE_MESSAGE = os.getenv("VIP_INVITE_MESSAGE")

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

# Envia mensagem automática no canal às 12h e 00h
def scheduled_message():
    global last_auto_message_time
    while True:
        now = datetime.now()
        if now.hour in [12, 0] and now.date() != last_auto_message_time:
            bot.send_message(CHANNEL_ID, AUTOMATIC_MESSAGE)
            bot.send_message(LOG_CHANNEL_ID, "📢 Mensagem automática enviada ao canal.")
            last_auto_message_time = now.date()
        time.sleep(60)

# Iniciar a thread para envio automático de mensagens no canal
threading.Thread(target=scheduled_message, daemon=True).start()

# Comando /start para enviar mensagens corretamente
@bot.message_handler(commands=["start"])
def send_checkout(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name  

    # Se for admin, apenas informa que ele está autenticado
    if user_id in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(user_id, "✅ Você está autenticado como ADMIN.")
        return  

    # Se for usuário normal, envia sequência de mensagens
    users.add(user_id)  
    log_message(user_id, user_name, "/start")  

    # Notifica os administradores sobre um novo usuário
    bot.send_message(ADMIN_ID_1, f"📌 Novo usuário interagiu!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")
    bot.send_message(ADMIN_ID_2, f"📌 Novo usuário interagiu!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")

    # Envia mensagens ao usuário
    bot.send_message(user_id, WELCOME_MESSAGE)
    bot.send_message(user_id, VIP_BENEFITS)
    time.sleep(2)
    bot.send_message(user_id, CHECKOUT_MESSAGE)
    bot.send_message(user_id, "💳 Envie o comprovante de pagamento aqui para validação.")

# Comando /status para admins verificarem métricas
@bot.message_handler(commands=["status"])
def admin_status(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(
            message.chat.id,
            f"📊 Status do Bot:\n👥 Usuários interagidos: {len(users)}\n📨 Última mensagem automática: {last_auto_message_time}"
        )
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

# Comando /me para exibir comandos disponíveis para administradores
@bot.message_handler(commands=["me"])
def list_admin_commands(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(
            message.chat.id,
            "🛠 **Comandos disponíveis:**\n"
            "/status - Exibir status do bot\n"
            "/msg <id> <texto> - Enviar mensagem para um usuário\n"
            "/broadcast <texto> - Enviar mensagem para o canal\n"
            "/aprovar <id> - Confirmar pagamento e liberar acesso ao VIP\n"
        )
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

# Comando para administradores enviarem mensagens diretas
@bot.message_handler(commands=["msg"])
def send_admin_message(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        try:
            msg_parts = message.text.split(" ", 2)
            target_user_id = int(msg_parts[1])
            admin_message = msg_parts[2]
            bot.send_message(target_user_id, f"📩 Mensagem do ADMIN:\n{admin_message}")
            bot.send_message(message.chat.id, "✅ Mensagem enviada com sucesso.")
        except:
            bot.send_message(message.chat.id, "⚠ Erro: Use `/msg <user_id> <mensagem>`")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para este comando.")

# Comando /broadcast para enviar mensagens ao canal
@bot.message_handler(commands=["broadcast"])
def broadcast_message(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        text = message.text.replace("/broadcast ", "")
        bot.send_message(CHANNEL_ID, text)
        bot.send_message(message.chat.id, "📢 Mensagem enviada ao canal.")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para este comando.")

# Processa envio de comprovantes de pagamento
@bot.message_handler(content_types=["photo", "document"])
def receber_comprovante(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name  

    # Notifica os admins
    if message.photo or message.document:
        pending_payments[user_id] = user_name  
        bot.send_message(ADMIN_ID_1, f"📩 Novo pagamento recebido!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")
        bot.send_message(ADMIN_ID_2, f"📩 Novo pagamento recebido!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")

        bot.forward_message(ADMIN_ID_1, user_id, message.message_id)
        bot.forward_message(ADMIN_ID_2, user_id, message.message_id)
        bot.send_message(user_id, "📨 Seu pagamento foi enviado para análise. Aguarde confirmação.")

# Comando /aprovar para confirmar pagamento e enviar link do VIP
@bot.message_handler(commands=["aprovar"])
def confirmar_pagamento(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        try:
            target_user_id = int(message.text.split(" ", 1)[1])
            bot.send_message(target_user_id, f"🎉 Seu pagamento foi confirmado! Acesse o VIP: {VIP_GROUP_LINK}")
            bot.send_message(message.chat.id, f"✅ Acesso VIP liberado para {target_user_id}.")
        except:
            bot.send_message(message.chat.id, "⚠ Erro: Use `/aprovar <user_id>`")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para este comando.")

# Mantém o bot rodando
bot.polling()
