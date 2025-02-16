import os
import telebot
import threading
import time
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID do canal de geração de desejo
BOT_USERNAME = os.getenv("BOT_USERNAME")  # Nome de usuário do bot (@SeuBot)
IMAGE_URL = os.getenv("IMAGE_URL")  # URL da imagem que será enviada no canal
bot = telebot.TeleBot(TOKEN)

# Mensagens do Railway
START_MESSAGE = os.getenv("START_MESSAGE")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")
VIP_INVITE_MESSAGE = os.getenv("VIP_INVITE_MESSAGE")  # Mensagem VIP enviada no canal
VIP_BUTTON_TEXT = os.getenv("VIP_BUTTON_TEXT", "🔥 Falar com o Bot")  # Texto do botão

# Lista para armazenar os usuários que já interagiram com o bot
users = set()

# 🔹 Função para enviar a mensagem VIP no canal do Telegram com imagem e botão clicável a cada 24 horas
def send_vip_invite():
    while True:
        time.sleep(86400)  # 24 horas

        # Criar um botão clicável para falar com o bot
        markup = InlineKeyboardMarkup()
        bot_link = f"https://t.me/{BOT_USERNAME}"  # Link para o bot no Telegram
        button = InlineKeyboardButton(text=VIP_BUTTON_TEXT, url=bot_link)
        markup.add(button)

        # Enviar a imagem + mensagem + botão no canal
        bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=IMAGE_URL,
            caption=VIP_INVITE_MESSAGE,
            reply_markup=markup,
            parse_mode="Markdown"
        )

# 🔹 Iniciar a thread para envio automático da mensagem no canal
threading.Thread(target=send_vip_invite, daemon=True).start()

# 🔹 Comando /start para organizar as mensagens corretamente
@bot.message_handler(commands=["start"])
def send_checkout(message):
    user_id = message.chat.id
    users.add(user_id)  # Adiciona o usuário à lista de notificações futuras
    
    # Envia a mensagem de boas-vindas
    bot.send_message(user_id, WELCOME_MESSAGE)

    # Envia os benefícios do VIP em um bloco separado
    bot.send_message(user_id, VIP_BENEFITS)

    # Aguarda 2 segundos antes de enviar o checkout
    time.sleep(2)

    # Envia o checkout
    bot.send_message(user_id, CHECKOUT_MESSAGE)

# Mantém o bot rodando
bot.polling()
