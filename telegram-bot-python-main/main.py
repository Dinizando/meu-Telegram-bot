import os
import telebot
import threading
import time
import logging
from datetime import datetime
from telebot.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from dotenv import load_dotenv

# Carregar variáveis do ambiente
load_dotenv()

# Verificação crítica das variáveis de ambiente
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS").split(",")] if os.getenv("ADMIN_IDS") else []
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
VIP_GROUP_LINK = os.getenv("VIP_GROUP_LINK")

if not all([TOKEN, CHANNEL_ID, ADMIN_IDS, LOG_CHANNEL_ID]):
    raise ValueError("Variáveis de ambiente essenciais faltando!")

bot = telebot.TeleBot(TOKEN)

# Configuração de logging
logging.basicConfig(
    filename="bot_interactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8",
)

# Dados persistentes
users = set()
pending_payments = {}
last_auto_message_time = None

# Carrega mensagens do ambiente
MESSAGES = {
    "start": os.getenv("START_MESSAGE", "👋 Bem-vindo!"),
    "welcome": os.getenv("WELCOME_MESSAGE", "ℹ️ Informações importantes..."),
    "vip_benefits": os.getenv("VIP_BENEFITS", "🌟 Benefícios VIP..."),
    "checkout": os.getenv("CHECKOUT_MESSAGE", "💰 Informações de pagamento..."),
    "automatic": os.getenv("AUTOMATIC_MESSAGE", "📢 Mensagem automática..."),
    "vip_invite": os.getenv("VIP_INVITE_MESSAGE", f"🎉 Acesse nosso grupo VIP: {VIP_GROUP_LINK}")
}

def log_message(user_id, user_name, text):
    """Registra interações no log e envia para o canal de admin"""
    log_entry = f"User {user_name} ({user_id}): {text}"
    logging.info(log_entry)
    try:
        bot.send_message(LOG_CHANNEL_ID, log_entry)
    except Exception as e:
        logging.error(f"Falha ao enviar log: {e}")

def send_automatic_messages():
    """Envia mensagens automáticas no horário programado"""
    while True:
        try:
            now = datetime.now()
            # Envia a cada 24 horas (ajuste conforme necessário)
            if last_auto_message_time is None or (now - last_auto_message_time).total_seconds() >= 86400:
                bot.send_message(CHANNEL_ID, MESSAGES["automatic"])
                last_auto_message_time = now
                logging.info("Mensagem automática enviada")
            time.sleep(3600)  # Verifica a cada hora
        except Exception as e:
            logging.error(f"Erro no envio automático: {e}")
            time.sleep(300)

# Inicia thread para mensagens automáticas
threading.Thread(target=send_automatic_messages, daemon=True).start()

@bot.message_handler(commands=["start"])
def send_welcome(message):
    """Handler para comando /start"""
    user_id = message.chat.id
    user_name = message.from_user.first_name

    users.add(user_id)
    log_message(user_id, user_name, "/start")

    try:
        bot.send_message(user_id, MESSAGES["welcome"])
        bot.send_message(user_id, MESSAGES["vip_benefits"])
        time.sleep(2)
        bot.send_message(user_id, MESSAGES["checkout"])
        bot.send_message(user_id, "💳 Envie o comprovante aqui para validação.")
        
        if user_id in ADMIN_IDS:
            bot.send_message(user_id, "✅ Você é um administrador.")
    except Exception as e:
        logging.error(f"Erro no /start: {e}")

@bot.message_handler(content_types=["photo", "document"])
def handle_payment_proof(message):
    """Processa comprovantes de pagamento"""
    user_id = message.chat.id
    pending_payments[user_id] = {
        "proof": message.photo[-1].file_id if message.photo else message.document.file_id,
        "type": "photo" if message.photo else "document",
        "date": datetime.now()
    }
    
    try:
        bot.send_message(user_id, "🔄 Comprovante recebido! Aguarde a validação.")
        
        # Notifica todos os admins
        for admin_id in ADMIN_IDS:
            bot.send_message(
                admin_id,
                f"⚠️ NOVO PAGAMENTO PENDENTE\n"
                f"Usuário: @{message.from_user.username}\n"
                f"ID: {user_id}\n"
                f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                f"Use /aprovar {user_id} para liberar acesso."
            )
    except Exception as e:
        logging.error(f"Erro ao processar pagamento: {e}")

@bot.message_handler(commands=["aprovar"])
def approve_payment(message):
    """Aprova pagamentos (admin only)"""
    if message.chat.id not in ADMIN_IDS:
        bot.reply_to(message, "⛔ Acesso negado.")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id not in pending_payments:
            bot.reply_to(message, "⚠️ Nenhum pagamento pendente para este usuário.")
            return

        # Envia mensagem de aprovação ao usuário
        bot.send_message(
            user_id,
            f"✅ Pagamento aprovado!\n\n{MESSAGES['vip_invite']}"
        )
        
        # Remove da lista de pendentes
        del pending_payments[user_id]
        
        # Confirmação para o admin
        bot.reply_to(message, f"✅ Acesso VIP concedido para {user_id}")
        logging.info(f"Pagamento aprovado para {user_id}")
        
    except (IndexError, ValueError):
        bot.reply_to(message, "⚠️ Formato: /aprovar <ID_USUARIO>")
    except Exception as e:
        logging.error(f"Erro ao aprovar pagamento: {e}")
        bot.reply_to(message, "❌ Ocorreu um erro ao processar.")

@bot.message_handler(commands=["broadcast"])
def broadcast_handler(message):
    """Envia mensagens para o canal (admin only)"""
    if message.chat.id not in ADMIN_IDS:
        return

    try:
        text = message.text.replace("/broadcast", "").strip()
        if text:
            bot.send_message(CHANNEL_ID, text)
            bot.reply_to(message, "📢 Mensagem enviada!")
        else:
            bot.reply_to(message, "⚠️ Adicione o texto após /broadcast")
    except Exception as e:
        logging.error(f"Erro no broadcast: {e}")
        bot.reply_to(message, "❌ Falha ao enviar mensagem.")

@bot.message_handler(commands=["status"])
def bot_status(message):
    """Mostra estatísticas do bot (admin only)"""
    if message.chat.id not in ADMIN_IDS:
        return

    status_msg = (
        f"🤖 Status do Bot\n\n"
        f"👥 Usuários registrados: {len(users)}\n"
        f"🔄 Pagamentos pendentes: {len(pending_payments)}\n"
        f"⏱ Última mensagem automática: {last_auto_message_time or 'Nunca'}"
    )
    bot.reply_to(message, status_msg)

# Loop principal com tratamento de erros
def run_bot():
    while True:
        try:
            logging.info("Iniciando bot...")
            bot.polling(none_stop=True, interval=3, timeout=30)
        except Exception as e:
            logging.error(f"ERRO NO BOT: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()
