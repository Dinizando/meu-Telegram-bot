import os
import telebot
import threading
import time
import logging
from dotenv import load_dotenv

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID do canal do Telegram
bot = telebot.TeleBot(TOKEN)

# Mensagens do Railway
START_MESSAGE = os.getenv("START_MESSAGE")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
VIP_BENEFITS = os.getenv("VIP_BENEFITS")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

# Lista para armazenar os usuários que já interagiram com o bot
users = set()

# 📜 **CONFIGURAR LOGGING PARA SALVAR AS CONVERSAS**
logging.basicConfig(
    filename="bot_interactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8"
)

# Função para registrar mensagens no arquivo de log
def l
