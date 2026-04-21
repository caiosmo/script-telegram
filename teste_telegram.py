import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_telegram(msg):
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "SEU_TOKEN_AQUI":
        print("Token do Telegram não configurado.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    response = requests.post(url, data=data)
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")

# Teste
enviar_telegram("Teste de mensagem do bot OLX")