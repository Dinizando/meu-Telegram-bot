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
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")  # Mensagem de boas-vindas
VIP_BENEFITS = os.getenv("VIP_BENEFITS")  # Benefícios do VIP
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")  # Mensagem de checkout

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
def send_scheduled_message():
    global last_auto_message_time
    while True:
        now = datetime.now()
        if now.hour in [12, 0] and (last_auto_message_time is None or last_auto_message_time.date() != now.date()):
            bot.send_message(CHANNEL_ID, AUTOMATIC_MESSAGE)
            bot.send_message(LOG_CHANNEL_ID, "📢 Mensagem automática enviada ao canal.")
            last_auto_message_time = now
        time.sleep(3600)  # Verifica a cada 1 hora

# Iniciar thread para enviar mensagens automáticas no canal
threading.Thread(target=send_scheduled_message, daemon=True).start()

# Comando /start para novos usuários
@bot.message_handler(commands=["start"])
def send_checkout(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name  # Obtém o nome do usuário
    
    users.add(user_id)  # Adiciona o usuário à lista de notificações futuras
    log_message(user_id, user_name, "/start")  # Registra a interação
    
    # Envia notificação ao administrador sobre um novo usuário
    bot.send_message(LOG_CHANNEL_ID, f"📌 Novo usuário interagiu!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")

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

# Comando /me para exibir comandos administrativos disponíveis
@bot.message_handler(commands=["me"])
def show_admin_commands(message):
    if str(message.chat.id) in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(
            message.chat.id,
            "📌 Comandos disponíveis:\n"
            "/status - Ver status do bot\n"
            "/broadcast <mensagem> - Enviar mensagem para o canal\n"
            "/forcar_mensagem - Forçar envio da mensagem automática\n"
        )
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

# Comando /status para verificar estatísticas do bot
@bot.message_handler(commands=["status"])
def bot_status(message):
    if str(message.chat.id) in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(
            message.chat.id,
            f"📊 **Status do Bot:**\n"
            f"👥 Usuários interagidos: {len(users)}\n"
            f"📢 Última mensagem automática enviada: {last_auto_message_time}\n"
            f"📌 Canal de Divulgação: {CHANNEL_ID}\n"
        )
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para ver essas informações.")

# Comando /broadcast para enviar uma mensagem para o canal do Telegram
@bot.message_handler(commands=["broadcast"])
def send_broadcast(message):
    if str(message.chat.id) in [ADMIN_ID_1, ADMIN_ID_2]:
        text = message.text.replace("/broadcast", "").strip()
        if text:
            bot.send_message(CHANNEL_ID, text)
            bot.send_message(LOG_CHANNEL_ID, "📢 Mensagem enviada ao canal.")
        else:
            bot.send_message(message.chat.id, "⚠ Erro: Envie a mensagem no formato `/broadcast <texto>`.")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para usar este comando.")

# Comando /forcar_mensagem para enviar a mensagem automática imediatamente
@bot.message_handler(commands=["forcar_mensagem"])
def force_send_message(message):
    if str(message.chat.id) in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(CHANNEL_ID, AUTOMATIC_MESSAGE)
        bot.send_message(LOG_CHANNEL_ID, "📢 Mensagem automática forçada.")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para usar este comando.")

# Mantém o bot rodando
bot.polling()
