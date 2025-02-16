import os
import telebot
import threading
import time
import logging
from telebot.types import InputMediaPhoto
from dotenv import load_dotenv

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID do canal público de geração de desejo
ADMIN_ID = os.getenv("ADMIN_ID")  # ID do administrador
VIP_GROUP_LINK = os.getenv("VIP_GROUP_LINK")  # Link do grupo VIP
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")  # Canal privado para logs do admin

bot = telebot.TeleBot(TOKEN)

# Mensagens do Railway
START_MESSAGE = os.getenv("START_MESSAGE")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")
VIP_INVITE_MESSAGE = os.getenv("VIP_INVITE_MESSAGE")

# Lista para armazenar os usuários que já interagiram com o bot
users = set()
pending_payments = {}  # Dicionário para armazenar usuários aguardando confirmação de pagamento

# Configurar logging para salvar as conversas
logging.basicConfig(
    filename="bot_interactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8",
)

# Função para registrar mensagens no arquivo de log
def log_message(user_id, user_name, text):
    log_entry = f"User {user_name} ({user_id}): {text}"
    logging.info(log_entry)
    bot.send_message(LOG_CHANNEL_ID, log_entry)  # Enviar log para canal privado do admin

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
    user_name = message.from_user.first_name  # Obtém o nome do usuário
    
    # Verifica se o usuário é administrador
    if str(user_id) == ADMIN_ID:
        bot.send_message(user_id, "✅ Você está autenticado como ADMIN.")
    else:
        users.add(user_id)  # Adiciona o usuário à lista de notificações futuras
        log_message(user_id, user_name, "/start")  # Registra a interação
        
        # Envia notificação ao administrador sobre um novo usuário
        bot.send_message(ADMIN_ID, f"📌 Novo usuário interagiu!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")

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

# Função para permitir que o ADMIN envie mensagens para qualquer usuário registrado
@bot.message_handler(commands=["msg"])
def send_admin_message(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            msg_parts = message.text.split(" ", 2)  # Divide o comando em partes
            target_user_id = msg_parts[1]  # ID do usuário que vai receber a mensagem
            admin_message = msg_parts[2]  # Mensagem a ser enviada

            bot.send_message(target_user_id, f"📩 Mensagem do ADMIN:\n{admin_message}")
            bot.send_message(ADMIN_ID, "✅ Mensagem enviada com sucesso.")
        except:
            bot.send_message(ADMIN_ID, "⚠ Erro: Use o formato correto: `/msg <user_id> <mensagem>`")

# Função para processar o envio de comprovantes de pagamento
@bot.message_handler(content_types=["photo", "document"])
def receber_comprovante(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name  # Obtém o nome do usuário

    # Se o usuário enviar um comprovante, notifica o admin
    if message.photo or message.document:
        pending_payments[user_id] = user_name  # Registra que este usuário enviou um pagamento
        bot.send_message(
            ADMIN_ID,
            f"📩 Novo pagamento recebido!\n🆔 ID: {user_id}\n👤 Nome: {user_name}\nAguarde confirmação.",
        )

        bot.forward_message(ADMIN_ID, user_id, message.message_id)  # Encaminha o comprovante ao admin
        bot.send_message(user_id, "📨 Seu pagamento foi enviado para análise. Aguarde a confirmação.")

# Função para confirmar pagamento e enviar link do grupo VIP
@bot.message_handler(commands=["aprovar"])
def confirmar_pagamento(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            msg_parts = message.text.split(" ", 1)  # Divide o comando em partes
            target_user_id = int(msg_parts[1])  # ID do usuário que fez o pagamento
            
            if target_user_id in pending_payments:
                bot.send_message(
                    target_user_id,
                    f"🎉 Parabéns! Seu pagamento foi confirmado. Aqui está seu acesso ao VIP: {VIP_GROUP_LINK}",
                )
                bot.send_message(ADMIN_ID, f"✅ Acesso VIP liberado para {target_user_id}.")
                del pending_payments[target_user_id]  # Remove da lista de pagamentos pendentes
            else:
                bot.send_message(ADMIN_ID, "⚠ Este usuário não tem pagamento pendente.")
        except:
            bot.send_message(ADMIN_ID, "⚠ Erro: Use o formato correto: `/aprovar <user_id>`")

# Função para enviar mensagem diária no canal do Telegram
def send_channel_message():
    while True:
        time.sleep(86400)  # 24 horas
        bot.send_message(CHANNEL_ID, VIP_INVITE_MESSAGE)
        bot.send_message(ADMIN_ID, "📢 Mensagem diária enviada ao canal.")

# Iniciar a thread para enviar mensagens ao canal
threading.Thread(target=send_channel_message, daemon=True).start()

# Função para registrar todas as mensagens no log e encaminhá-las ao admin
@bot.message_handler(func=lambda message: True)
def registrar_mensagem(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name
    text = message.text

    # Registra no log
    log_message(user_id, user_name, text)

    # Encaminha a mensagem para o canal privado do admin
    bot.forward_message(LOG_CHANNEL_ID, user_id, message.message_id)

# Mantém o bot rodando
bot.polling()
