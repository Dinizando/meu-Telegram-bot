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
ADMIN_ID_1 = int(os.getenv("ADMIN_ID_1"))  # ID da conta dos EUA (convertido para int)
ADMIN_ID_2 = int(os.getenv("ADMIN_ID_2"))  # ID da conta do Brasil (convertido para int)
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

# Função para enviar mensagem automática no canal às 12h e 00h
def scheduled_message():
    global last_auto_message_time
    while True:
        now = datetime.now()
        if now.hour in [12, 0] and now.date() != last_auto_message_time:  # Evita mensagens duplicadas no mesmo dia
            bot.send_message(CHANNEL_ID, AUTOMATIC_MESSAGE)
            bot.send_message(LOG_CHANNEL_ID, "📢 Mensagem automática enviada ao canal.")
            last_auto_message_time = now.date()  # Atualiza o último envio
        time.sleep(60)  # Verifica a cada minuto se chegou o horário

# Iniciar a thread para envio de mensagens no canal
threading.Thread(target=scheduled_message, daemon=True).start()

# Comando /start para organizar as mensagens corretamente
@bot.message_handler(commands=["start"])
def send_checkout(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name  # Obtém o nome do usuário
    
    # Verifica se o usuário é administrador
    if user_id == ADMIN_ID_1 or user_id == ADMIN_ID_2:
        bot.send_message(user_id, "✅ Você está autenticado como ADMIN.")
    else:
        users.add(user_id)  # Adiciona o usuário à lista de notificações futuras
        log_message(user_id, user_name, "/start")  # Registra a interação
        
        # Envia notificação ao administrador sobre um novo usuário
        bot.send_message(ADMIN_ID_1, f"📌 Novo usuário interagiu!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")
        bot.send_message(ADMIN_ID_2, f"📌 Novo usuário interagiu!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")

        # Envia a mensagem de boas-vindas
        bot.send_message(user_id, WELCOME_MESSAGE)

        # Envia os benefícios do VIP em um bloco separado
        bot.send_message(user_id, VIP_BENEFITS)

        # Aguarda 2 segundos antes de enviar o checkout
        time.sleep(2)

        # Envia o checkout
        bot.send_message(user_id, CHECKOUT_MESSAGE)

        # Solicita envio do comprovante
        bot.send_message(user_id, "💳 Envie o comprovante de pagamento aqui para validação.")

# Comando /me para admins verificarem estatísticas
@bot.message_handler(commands=["me"])
def admin_status(message):
    if message.chat.id == ADMIN_ID_1 or message.chat.id == ADMIN_ID_2:
        bot.send_message(
            message.chat.id,
            f"📊 Estatísticas do Bot:\n👥 Usuários interagidos: {len(users)}\n📨 Última mensagem automática enviada: {last_auto_message_time}",
        )
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

# Função para permitir que o ADMIN envie mensagens para qualquer usuário registrado
@bot.message_handler(commands=["msg"])
def send_admin_message(message):
    if message.chat.id == ADMIN_ID_1 or message.chat.id == ADMIN_ID_2:
        try:
            msg_parts = message.text.split(" ", 2)  # Divide o comando em partes
            target_user_id = int(msg_parts[1])  # ID do usuário que vai receber a mensagem
            admin_message = msg_parts[2]  # Mensagem a ser enviada

            bot.send_message(target_user_id, f"📩 Mensagem do ADMIN:\n{admin_message}")
            bot.send_message(message.chat.id, "✅ Mensagem enviada com sucesso.")
        except:
            bot.send_message(message.chat.id, "⚠ Erro: Use o formato correto: `/msg <user_id> <mensagem>`")

# Função para processar o envio de comprovantes de pagamento
@bot.message_handler(content_types=["photo", "document"])
def receber_comprovante(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name  # Obtém o nome do usuário

    # Se o usuário enviar um comprovante, notifica o admin
    if message.photo or message.document:
        bot.send_message(
            ADMIN_ID_1,
            f"📩 Novo pagamento recebido!\n🆔 ID: {user_id}\n👤 Nome: {user_name}\nAguarde confirmação.",
        )
        bot.send_message(
            ADMIN_ID_2,
            f"📩 Novo pagamento recebido!\n🆔 ID: {user_id}\n👤 Nome: {user_name}\nAguarde confirmação.",
        )

        bot.forward_message(ADMIN_ID_1, user_id, message.message_id)  # Encaminha ao admin 1
        bot.forward_message(ADMIN_ID_2, user_id, message.message_id)  # Encaminha ao admin 2
        bot.send_message(user_id, "📨 Seu pagamento foi enviado para análise. Aguarde a confirmação.")

# Função para confirmar pagamento e enviar link do grupo VIP
@bot.message_handler(commands=["aprovar"])
def confirmar_pagamento(message):
    if message.chat.id == ADMIN_ID_1 or message.chat.id == ADMIN_ID_2:
        try:
            msg_parts = message.text.split(" ", 1)  # Divide o comando em partes
            target_user_id = int(msg_parts[1])  # ID do usuário que fez o pagamento
            
            bot.send_message(
                target_user_id,
                f"🎉 Parabéns! Seu pagamento foi confirmado. Aqui está seu acesso ao VIP: {os.getenv('VIP_GROUP_LINK')}",
            )
            bot.send_message(message.chat.id, f"✅ Acesso VIP liberado para {target_user_id}.")
        except:
            bot.send_message(message.chat.id, "⚠ Erro: Use o formato correto: `/aprovar <user_id>`")

# Mantém o bot rodando
bot.polling()
