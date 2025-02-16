import os
import telebot
import logging
from dotenv import load_dotenv

# Carregar variáveis do ambiente do Railway
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")  # Seu ID de administrador
bot = telebot.TeleBot(TOKEN)

# Configurar logging para registrar interações
logging.basicConfig(
    filename="bot_interactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8"
)

# Comando para solicitar comprovante de pagamento
@bot.message_handler(commands=["pagamento"])
def solicitar_pagamento(message):
    user_id = message.chat.id
    bot.send_message(user_id, "💳 Envie seu comprovante de pagamento aqui. Pode ser uma imagem ou um documento.")

# Captura e encaminha imagens ou documentos para o admin
@bot.message_handler(content_types=["photo", "document"])
def receber_comprovante(message):
    user_id = message.chat.id
    if message.photo:
        file_id = message.photo[-1].file_id  # Pega a melhor qualidade da foto
        bot.send_photo(ADMIN_ID, file_id, caption=f"📌 Novo comprovante de pagamento de {user_id}.")
    elif message.document:
        file_id = message.document.file_id
        bot.send_document(ADMIN_ID, file_id, caption=f"📌 Novo comprovante de pagamento de {user_id}.")

    bot.send_message(user_id, "✅ Comprovante recebido! Aguarde a verificação.")

# Permitir que o admin responda aos usuários pelo bot
@bot.message_handler(commands=["responder"])
def responder_usuario(message):
    try:
        dados = message.text.split(" ", 2)
        if len(dados) < 3:
            bot.send_message(ADMIN_ID, "❌ Formato incorreto! Use: /responder <ID do usuário> <mensagem>")
            return
        
        user_id = dados[1]
        resposta = dados[2]

        bot.send_message(user_id, resposta)
        bot.send_message(ADMIN_ID, f"📨 Resposta enviada para {user_id}!")

    except Exception as e:
        bot.send_message(ADMIN_ID, f"Erro ao responder: {str(e)}")

# Mantém o bot rodando
bot.polling()
