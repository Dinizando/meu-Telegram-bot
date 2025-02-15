import os
import telebot
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

START_MESSAGE = os.getenv("START_MESSAGE", "🔥 Última Chamada! 🔥\n\n"
    "🔑 Conteúdos raros e exclusivos te esperam no nosso Canal VIP! 💎\n\n"
    "⏰ Garanta agora ou perca para sempre! 🛑\n\n"
    "👉 /start"
)

# Enviar a mensagem inicial antes do usuário digitar /start
@bot.message_handler(commands=['start'])
def send_checkout(message):
    checkout_message = "🚀 Você está a um passo de entrar no melhor VIP do Instagram! O que tem no VIP?\n\n"
    checkout_message += "💎 Acesso a conteúdos exclusivos\n"
    checkout_message += "📈 Estratégias para crescer no Instagram\n"
    checkout_message += "💬 Suporte VIP\n\n"
    checkout_message += "💳 Checkout disponível agora!"

    bot.send_message(message.chat.id, checkout_message)

# Enviar a mensagem inicial para novos usuários (manual ou por evento)
def send_initial_message(user_id):
    bot.send_message(user_id, START_MESSAGE)

# Mantém o bot rodando
bot.polling()
