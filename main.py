import telebot
import requests
import re
import uuid
import hashlib
import json
from user_agent import generate_user_agent
import concurrent.futures

API_TOKEN = '8488920682:AAGhoJ-R5q5Xd4nVULrdmSxM2YfSch6j2RU'
bot = telebot.TeleBot(API_TOKEN)

def generate_signed_body(email):
    # توليد UUID و Device ID عشوائي لكل طلب لتخطي الحماية
    device_id = f"android-{uuid.uuid4().hex[:16]}"
    guid = str(uuid.uuid4())
    data = {
        "user_email": email,
        "device_id": device_id,
        "guid": guid,
        "_csrftoken": "missing"
    }
    json_data = json.dumps(data)
    # التوقيع الجديد (HMAC-SHA256 محاكى)
    signed_body = f"9d18e1d526e03883a826471e9a2636412e8c9c612666270438f6b8c8d8c8d8c8.{json_data}"
    return signed_body

def check_email(email):
    try:
        url = "https://i.instagram.com/api/v1/accounts/send_password_reset/"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': generate_user_agent(),
            'X-IG-Connection-Type': 'WIFI',
            'X-IG-Capabilities': 'AQ==',
            'Accept-Language': 'en-US',
            'Host': 'i.instagram.com'
        }
        
        payload = {
            'ig_sig_key_version': '4',
            'signed_body': generate_signed_body(email)
        }

        response = requests.post(url, data=payload, headers=headers, timeout=10)
        
        # إذا كانت النتيجة تحتوي على obfuscated_email أو تم إرسال الإيميل فعلاً
        if 'obfuscated_email' in response.text or '"status":"ok"' in response.text:
            return True
        return False
    except:
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🔥 أهلاً Dexr! أرسل الإيميلات الآن وسأفحصها لك بالتقنية الجديدة.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message.text)
    if not emails:
        bot.reply_to(message, "❌ ارسل ايميلات صالحة.")
        return

    bot.send_message(message.chat.id, f"🔎 جاري فحص {len(emails)} إيميل...")
    
    for email in emails:
        if check_email(email):
            bot.send_message(message.chat.id, f"✅ مربوط حتماً: {email}")
        else:
            bot.send_message(message.chat.id, f"❌ غير مربوط: {email}")

bot.polling()
