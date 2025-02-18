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
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID do canal público de geração de desejo
ADMIN_ID_1 = os.getenv("ADMIN_ID_1")  # ID da conta dos EUA
ADMIN_ID_2 = os.getenv("ADMIN_ID_2")  # ID da conta do Brasil
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")  # Canal privado para logs do admin

bot = telebot.TeleBot(TOKEN)

# Mensagens do Railway
AUTOMATIC_MESSAGE = os.getenv("AUTOMATIC_MESSAGE")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

# Lista para armazenar os usuários que interagiram com o bot
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
def scheduled_broadcast():
    global last_auto_message_time
    while True:
        now = datetime.now()
        if now.hour in [12, 0] and (last_auto_message_time is None or last_auto_message_time.date() != now.date()):
            bot.send_message(CHANNEL_ID, AUTOMATIC_MESSAGE)
            bot.send_message(LOG_CHANNEL_ID, "📢 Mensagem automática enviada ao canal.")
            last_auto_message_time = now  # Atualiza o horário do último envio
        time.sleep(60)  # Verifica a cada minuto

# Iniciar a thread para envio automático no canal
threading.Thread(target=scheduled_broadcast, daemon=True).start()

# Comando /start para organizar as mensagens corretamente
@bot.message_handler(commands=["start"])
def send_checkout(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name  # Obtém o nome do usuário
    
    # Verifica se o usuário é administrador
    if str(user_id) in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(user_id, "✅ Você está autenticado como ADMIN.")
    else:
        users.add(user_id)  # Adiciona o usuário à lista de notificações futuras
        log_message(user_id, user_name, "/start")  # Registra a interação
        
        # Envia notificação ao administrador sobre um novo usuário
        bot.send_message(ADMIN_ID_1, f"📌 Novo usuário interagiu!\n🆔 ID: {user_id}\n👤 Nome: {user_name}")

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

# Comando /broadcast para enviar mensagem no canal
@bot.message_handler(commands=["broadcast"])
def send_broadcast(message):
    if str(message.chat.id) in [ADMIN_ID_1, ADMIN_ID_2]:
        text = message.text.replace("/broadcast", "").strip()
        
        if text:
            bot.send_message(CHANNEL_ID, text)
            bot.send_message(LOG_CHANNEL_ID, "📢 Mensagem de texto enviada ao canal.")
        else:
            bot.send_message(message.chat.id, "⚠ Erro: Envie a mensagem no formato `/broadcast <texto>` ou envie uma **foto/vídeo** com legenda.")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para usar este comando.")

# Função para processar mídia (foto ou vídeo) enviada pelo admin
@bot.message_handler(content_types=["photo", "video"])
def broadcast_media(message):
    if str(message.chat.id) in [ADMIN_ID_1, ADMIN_ID_2]:
        caption = message.caption if message.caption else "📢 Nova atualização!"
        
        # Se for foto
        if message.photo:
            bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=caption)
            bot.send_message(LOG_CHANNEL_ID, "📸 Foto enviada ao canal.")
        
        # Se for vídeo
        elif message.video:
            bot.send_video(CHANNEL_ID, message.video.file_id, caption=caption)
            bot.send_message(LOG_CHANNEL_ID, "🎥 Vídeo enviado ao canal.")

        bot.send_message(message.chat.id, "✅ Mídia enviada com sucesso!")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para usar este comando.")

# Comando /me para exibir informações do administrador
@bot.message_handler(commands=["me"])
def admin_info(message):
    if str(message.chat.id) in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(message.chat.id, f"📊 ID do ADMIN: {message.chat.id}\n🛠 Comandos disponíveis:\n"
                                          "/me - Informações do admin\n"
                                          "/broadcast - Enviar mensagem no canal\n"
                                          "/status - Ver estatísticas\n"
                                          "/forcar_mensagem - Enviar mensagem automática manualmente")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para acessar este comando.")

# Comando /status para ver estatísticas do bot
@bot.message_handler(commands=["status"])
def bot_status(message):
    if str(message.chat.id) in [ADMIN_ID_1, ADMIN_ID_2]:
        total_users = len(users)
        bot.send_message(message.chat.id, f"📊 Status do Bot:\n👥 Usuários registrados: {total_users}\n📢 Última mensagem automática: {last_auto_message_time}")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para ver essas informações.")

# Comando /forcar_mensagem para enviar mensagem automática no canal imediatamente
@bot.message_handler(commands=["forcar_mensagem"])
def force_send_message(message):
    if str(message.chat.id) in [ADMIN_ID_1, ADMIN_ID_2]:
        bot.send_message(CHANNEL_ID, AUTOMATIC_MESSAGE)
        bot.send_message(message.chat.id, "✅ Mensagem automática enviada ao canal.")
    else:
        bot.send_message(message.chat.id, "⛔ Você não tem permissão para usar este comando.")

# Mantém o bot rodando
bot.polling()
