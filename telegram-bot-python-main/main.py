import os
import telebot
import threading
import time
import logging
from datetime import datetime
from telebot.types import InputMediaPhoto, InputMediaVideo
from dotenv import load_dotenv

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Canal de divulgação
ADMIN_ID_1 = int(os.getenv("ADMIN_ID_1"))  # ID Admin EUA
ADMIN_ID_2 = int(os.getenv("ADMIN_ID_2"))  # ID Admin Brasil
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))  # Canal privado de logs do admin
VIP_GROUP_LINK = os.getenv("VIP_GROUP_LINK")  # Link do VIP

bot = telebot.TeleBot(TOKEN)

# Mensagens configuradas no Railway
AUTOMATIC_MESSAGE = os.getenv("AUTOMATIC_MESSAGE")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")
VIP_INVITE_MESSAGE = os.getenv("VIP_INVITE_MESSAGE")
START_MESSAGE = os.getenv("START_MESSAGE")
VIP_BUTTON_TEXT = os.getenv("VIP_BUTTON_TEXT")
IMAGE_URL = os.getenv("IMAGE_URL")

# Lista de usuários registrados
users = set()
pending_payments = {}  # Usuários aguardando confirmação de pagamento
last_auto_message_time = None  # Última mensagem automática enviada

# Configurar logging para registrar interações
logging.basicConfig(
    filename="bot_interactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8",
)

def log_message(user_id, user_name, text):
    log_entry = f"User {user_name} ({user_id}): {text}"
    logging.info(log_entry)
    bot.send_message(LOG_CHANNEL_ID, log_entry)

def scheduled_message():
    global last_auto_message_time
    while True:
        now = datetime.now()
        if now.hour in [12, 0] and now.date() != last_auto_message_time:
            bot.send_message(CHANNEL_ID, AUTOMATIC_MESSAGE)
            bot.send_message(LOG_CHANNEL_ID, "📢 Mensagem automática enviada ao canal.")
            last_auto_message_time = now.date()
        time.sleep(60)

threading.Thread(target=scheduled_message, daemon=True).start()

@bot.message_handler(commands=["start"])
def send_checkout(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name  

    if user_id in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(user_id, "✅ Você está autenticado como ADMIN.")
        return  
    
    users.add(user_id)  
    log_message(user_id, user_name, "/start")
    bot.send_message(ADMIN_ID_1, f"📌 Novo usuário interagiu!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")
    bot.send_message(ADMIN_ID_2, f"📌 Novo usuário interagiu!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")
    bot.send_message(user_id, WELCOME_MESSAGE)
    bot.send_message(user_id, VIP_BENEFITS)
    time.sleep(2)
    bot.send_message(user_id, CHECKOUT_MESSAGE)
    bot.send_message(user_id, "💳 Envie o comprovante de pagamento aqui para validação.")

@bot.message_handler(commands=["status"])
def admin_status(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(
            message.chat.id,
            f"📊 Status do Bot:\n🟢 Online: Sim\n⏰ Horário atual: {datetime.now()}\n📌 Última mensagem automática: {last_auto_message_time}\n👥 Total de usuários cadastrados: {len(users)}"
        )
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

@bot.message_handler(commands=["me"])
def list_admin_commands(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(
            message.chat.id,
            "🛠 **Comandos disponíveis:**\n/status - Exibir status do bot\n/msg <id> <texto> - Enviar mensagem para um usuário\n/broadcast <texto> - Enviar mensagem para o canal\n/aprovar <id> - Confirmar pagamento e liberar acesso ao VIP"
        )
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

@bot.message_handler(commands=["broadcast"])
def broadcast_message(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        if message.reply_to_message and (message.reply_to_message.photo or message.reply_to_message.video):
            caption = message.text.replace("/broadcast ", "")
            if message.reply_to_message.photo:
                bot.send_photo(CHANNEL_ID, message.reply_to_message.photo[-1].file_id, caption=caption)
            elif message.reply_to_message.video:
                bot.send_video(CHANNEL_ID, message.reply_to_message.video.file_id, caption=caption)
            bot.send_message(message.chat.id, "📢 Mídia enviada ao canal.")
        else:
            text = message.text.replace("/broadcast ", "")
            bot.send_message(CHANNEL_ID, text)
            bot.send_message(message.chat.id, "📢 Mensagem enviada ao canal.")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para este comando.")

bot.polling()
