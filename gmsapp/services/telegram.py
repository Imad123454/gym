import requests
from gmsapp.models import Receptionist

BOT_TOKEN = "8500009801:AAEeoA7tEecathjS7JNDXnVR1LznBuUjrI4"

def send_inquiry_to_telegram(inquiry):
    # TEMP FIX: Hardcode chat_id if tenant lookup fails
    chat_id = None
    if inquiry.tenant:
        receptionist = Receptionist.objects.filter(
            tenant=inquiry.tenant,
            telegram_chat_id__isnull=False
        ).first()
        if receptionist:
            chat_id = receptionist.telegram_chat_id

    if not chat_id:
        # fallback: use your known chat_id
        chat_id = 8516821088

    text = (
        f"📩 NEW INQUIRY\n\n"
        f"From: {inquiry.created_by.username}\n"
        f"Subject: {inquiry.subject}\n"
        f"Message: {inquiry.message}"
    )

    if not text.strip():
        print("❌ Telegram text empty")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": text})
    print("✅ Telegram response:", response.status_code, response.text)
