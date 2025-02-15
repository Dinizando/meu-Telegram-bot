import os
import telebot
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Carregar variáveis de ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Mensagens (busca do Railway)
START_MESSAGE = os.getenv("START_MESSAGE")
CHECKOUT_MESSAGE = os.getenv("CHECKOUT_MESSAGE")

# Lista para armazenar usuários que já interagiram com o bot
users = set()

# Função para enviar a mensagem de urgência a cada 24h (86.400 segundos)
def send_urgent_message():
    while True:
        time.sleep(86400)  # Espera 24 horas
        for user_id in users:
            bot.send_message(user_id, START_MESSAGE)

# Iniciar a thread para mensagens automáticas
threading.Thread(target=send_urgent_message, daemon=True).start()

# Quando o usuário digita /start
@bot.message_handler(commands=['start'])
def send_checkout(message):
    user_id = message.chat.id
    users.add(user_id)  # Adiciona o usuário à lista de notificações futuras

    # Enviar mensagem do Checkout em blocos
    bot.send_message(user_id, "🔥 Bem-vindo ao VIP! Aqui está como garantir seu acesso:")
    
    # Criar botões interativos
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔒 Pagar Agora", url="https://seulinkdepagamento.com"))
    markup.add(InlineKeyboardButton("❓ Suporte", url="https://t.me/seuSuporte"))
    
    bot.send_message(user_id, CHECKOUT_MESSAGE, reply_markup=markup)

# Mantém o bot rodando
bot.polling()
