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
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID do canal onde o bot envia mensagens automáticas
ADMIN_ID_1 = os.getenv("ADMIN_ID_1")  # ID do admin (EUA)
ADMIN_ID_2 = os.getenv("ADMIN_ID_2")  # ID do admin (Brasil)
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")  # Canal privado para logs do admin

bot = telebot.TeleBot(TOKEN)

# Mensagens do Railway
AUTOMATIC_MESSAGE = os.getenv("AUTOMATIC_MESSAGE")  # Mensagem automática no canal
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

# Lista para armazenar usuários que interagiram com o bot
users = set()
last_auto_message_time = None  # Para evitar mensagens duplicadas no mesmo dia

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

# Função para enviar mensagem automática ao canal às 12h e 00h
def scheduled_broadcast():
    global last_auto_message_time
    while True:
        now = datetime.now()
        if now.hour in [12, 0] and now.date() != last_auto_message_time:
            try:
                bot.send_message(CHANNEL_ID, AUTOMATIC_MESSAGE)
                bot.send_message(LOG_CHANNEL_ID, "📢 Mensagem automática enviada ao canal.")
                last_auto_message_time = now.date()  # Atualiza o último envio
            except Exception as e:
                bot.send_message(LOG_CHANNEL_ID, f"⚠ Erro ao enviar mensagem automática: {e}")
        time.sleep(3600)  # Verifica a cada hora

# Iniciar a thread para envio automático ao canal
threading.Thread(target=scheduled_broadcast, daemon=True).start()

# Comando para enviar mensagens de Broadcast manualmente
@bot.message_handler(commands=["broadcast"])
def broadcast_media(message):
    user_id = str(message.chat.id)
    
    if user_id not in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(user_id, "🚫 Você não tem permissão para usar este comando.")
        return

    args = message.text.split(" ", 1)
    if len(args) < 2:
        bot.send_message(user_id, "⚠ Erro: Envie a mensagem no formato `/broadcast <texto>`.")
        return
    
    broadcast_text = args[1]

    try:
        bot.send_message(CHANNEL_ID, broadcast_text)
        bot.send_message(user_id, "✅ Mensagem enviada com sucesso ao canal!")
    except Exception as e:
        bot.send_message(user_id, f"⚠ Erro ao enviar mensagem: {e}")

# Comando para enviar mídia (foto ou vídeo) junto com texto
@bot.message_handler(content_types=["photo", "video", "document"])
def handle_media(message):
    user_id = str(message.chat.id)

    if user_id not in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(user_id, "🚫 Você não tem permissão para enviar mídia.")
        return

    caption = message.caption if message.caption else "📢 Nova atualização!"

    try:
        if message.photo:
            file_id = message.photo[-1].file_id
            bot.send_photo(CHANNEL_ID, file_id, caption=caption)
        elif message.video:
            file_id = message.video.file_id
            bot.send_video(CHANNEL_ID, file_id, caption=caption)
        elif message.document:
            file_id = message.document.file_id
            bot.send_document(CHANNEL_ID, file_id, caption=caption)

        bot.send_message(user_id, "✅ Mídia enviada com sucesso ao canal!")
    except Exception as e:
        bot.send_message(user_id, f"⚠ Erro ao enviar mídia: {e}")

# Comando para verificar o status do bot
@bot.message_handler(commands=["status"])
def status_command(message):
    user_id = str(message.chat.id)

    if user_id not in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(user_id, "🚫 Você não tem permissão para ver essas informações.")
        return

    now = datetime.now()
    status_message = f"📊 **Status do Bot**\n\n" \
                     f"🟢 Online: Sim\n" \
                     f"⏰ Horário atual: {now.strftime('%Y-%m-%d %H:%M:%S')}\n" \
                     f"📌 Última mensagem automática: {last_auto_message_time}\n" \
                     f"👥 Total de usuários cadastrados: {len(users)}"

    bot.send_message(user_id, status_message, parse_mode="Markdown")

# Mantém o bot rodando
bot.polling()
