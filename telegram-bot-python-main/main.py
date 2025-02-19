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
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID do canal para envio de mensagens automáticas
ADMIN_IDS = [int(os.getenv("ADMIN_ID_1")), int(os.getenv("ADMIN_ID_2"))]  # IDs dos administradores
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))  # Canal privado para logs do admin
VIP_GROUP_LINK = os.getenv("VIP_GROUP_LINK")  # Link do grupo VIP

bot = telebot.TeleBot(TOKEN)

# Mensagens configuradas no Railway
AUTOMATIC_MESSAGE = os.getenv("AUTOMATIC_MESSAGE")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")
VIP_INVITE_MESSAGE = os.getenv("VIP_INVITE_MESSAGE")

# Lista de usuários registrados
users = set()
pending_payments = {}  # Usuários aguardando confirmação de pagamento
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
    bot.send_message(LOG_CHANNEL_ID, log_entry)

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

# Comando /start
def send_checkout(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name
    
    if user_id in ADMIN_IDS:
        bot.send_message(user_id, "✅ Você está autenticado como ADMIN.")
        return

    users.add(user_id)
    log_message(user_id, user_name, "/start")
    
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, f"📌 Novo usuário interagiu!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")
    
    bot.send_message(user_id, WELCOME_MESSAGE)
    bot.send_message(user_id, VIP_BENEFITS)
    time.sleep(2)
    bot.send_message(user_id, CHECKOUT_MESSAGE)
    bot.send_message(user_id, "💳 Envie o comprovante de pagamento aqui para validação.")

bot.message_handler(commands=["start"])(send_checkout)

# Comando /status para admins verificarem métricas
def admin_status(message):
    if message.chat.id in ADMIN_IDS:
        bot.send_message(
            message.chat.id,
            f"📊 **Status do Bot:**\n👥 Usuários interagidos: {len(users)}\n📨 Última mensagem automática: {last_auto_message_time}\n📢 Canal de Divulgação: {CHANNEL_ID}"
        )
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

bot.message_handler(commands=["status"])(admin_status)

# Comando /me para exibir comandos disponíveis para administradores
def list_admin_commands(message):
    if message.chat.id in ADMIN_IDS:
        bot.send_message(
            message.chat.id,
            "🛠 **Comandos disponíveis:**\n"
            "/status - Ver status do bot\n"
            "/broadcast <mensagem> - Enviar mensagem para o canal\n"
            "/forcar_mensagem - Forçar envio da mensagem automática\n"
            "/aprovar <id> - Confirmar pagamento e liberar acesso ao VIP"
        )
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

bot.message_handler(commands=["me"])(list_admin_commands)

# Comando /broadcast para enviar mensagens ao canal (com mídia opcional)
def broadcast_message(message):
    if message.chat.id in ADMIN_IDS:
        if message.text.startswith("/broadcast") and len(message.text.split()) > 1:
            text = message.text.replace("/broadcast ", "")
            bot.send_message(CHANNEL_ID, text)
            bot.send_message(message.chat.id, "📢 Mensagem enviada ao canal.")
        elif message.photo:
            file_id = message.photo[-1].file_id
            caption = message.caption if message.caption else ""
            bot.send_photo(CHANNEL_ID, file_id, caption=caption)
            bot.send_message(message.chat.id, "📢 Foto enviada ao canal.")
        elif message.video:
            file_id = message.video.file_id
            caption = message.caption if message.caption else ""
            bot.send_video(CHANNEL_ID, file_id, caption=caption)
            bot.send_message(message.chat.id, "📢 Vídeo enviado ao canal.")
        else:
            bot.send_message(message.chat.id, "⚠ Envie a mensagem no formato `/broadcast <texto>` ou envie uma **foto/vídeo** com legenda.")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para este comando.")

bot.message_handler(commands=["broadcast"], content_types=["text", "photo", "video"])(broadcast_message)

# Mantém o bot rodando
bot.polling()
