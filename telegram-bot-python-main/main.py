import os
import telebot
import threading
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID do canal
ADMIN_ID_1 = int(os.getenv("ADMIN_ID_1"))  # ID da conta dos EUA
ADMIN_ID_2 = int(os.getenv("ADMIN_ID_2"))  # ID da conta do Brasil
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))  # Canal para logs do admin
VIP_GROUP_LINK = os.getenv("VIP_GROUP_LINK")  # Link do grupo VIP

bot = telebot.TeleBot(TOKEN)

# Lista de usuários registrados
users = set()
pending_payments = {}  # Dicionário para armazenar pagamentos pendentes
last_auto_message_time = None

# Configuração de logging
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

# Enviar mensagens automáticas no canal

def scheduled_message():
    global last_auto_message_time
    while True:
        now = datetime.now()
        if now.hour in [12, 0] and now.date() != last_auto_message_time:
            bot.send_message(CHANNEL_ID, "📢 Mensagem automática enviada ao canal!")
            last_auto_message_time = now.date()
        time.sleep(60)

threading.Thread(target=scheduled_message, daemon=True).start()

# Comando /start
@bot.message_handler(commands=["start"])
def send_checkout(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name

    if user_id in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(user_id, "✅ Você está autenticado como ADMIN.")
        return  
    
    users.add(user_id)
    log_message(user_id, user_name, "/start")  

    bot.send_message(user_id, "Bem-vindo ao VIP!")
    bot.send_message(user_id, "Aqui está como garantir seu acesso:")
    time.sleep(2)
    bot.send_message(user_id, "💳 Envie o comprovante de pagamento aqui para validação.")

# Comando /broadcast melhorado para suportar mídia
@bot.message_handler(commands=["broadcast"])
def broadcast_message(message):
    if message.chat.id in [ADMIN_ID_1, ADMIN_ID_2]:
        if message.reply_to_message:
            # Verifica se há mídia anexada
            if message.reply_to_message.photo:
                file_id = message.reply_to_message.photo[-1].file_id
                bot.send_photo(CHANNEL_ID, file_id, caption=message.text.replace("/broadcast ", ""))
            elif message.reply_to_message.video:
                file_id = message.reply_to_message.video.file_id
                bot.send_video(CHANNEL_ID, file_id, caption=message.text.replace("/broadcast ", ""))
            else:
                bot.send_message(CHANNEL_ID, message.text.replace("/broadcast ", ""))
            bot.send_message(message.chat.id, "📢 Mensagem enviada ao canal.")
        else:
            bot.send_message(message.chat.id, "⚠ Responda a uma foto, vídeo ou mensagem para enviar um broadcast.")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para este comando.")

# Mantém o bot rodando
bot.polling()
