import os
import telebot
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID do canal do Telegram
VIP_INVITE_MESSAGE = os.getenv("VIP_INVITE_MESSAGE")  # Mensagem VIP
VIP_GROUP_LINK = "https://t.me/SeuGrupoVIP"  # Substitua pelo link do seu grupo VIP

bot = telebot.TeleBot(TOKEN)

# Função para enviar a mensagem VIP no canal uma vez por dia
def send_vip_invite():
    while True:
        time.sleep(86400)  # Aguarda 24 horas

        # Criar um botão para direcionar ao grupo VIP
        markup = InlineKeyboardMarkup()
        btn_vip = InlineKeyboardButton("🔑 Acessar o VIP", url=VIP_GROUP_LINK)
        markup.add(btn_vip)

        # Enviar mensagem no canal com o botão
        bot.send_message(CHANNEL_ID, VIP_INVITE_MESSAGE, reply_markup=markup)

# Iniciar a thread para envio automático da mensagem VIP
threading.Thread(target=send_vip_invite, daemon=True).start()

# Mantém o bot rodando
bot.polling()
