import telebot
import cloudscraper
import uuid
import re
import time

API_TOKEN = '8488920682:AAGhoJ-R5q5Xd4nVULrdmSxM2YfSch6j2RU'
bot = telebot.TeleBot(API_TOKEN)

def check_email_fixed(email):
    # إنشاء متصفح يحاكي الواقع لتخطى الـ IP Block
    scraper = cloudscraper.create_scraper()
    
    # توليد بيانات جهاز عشوائية تماماً
    device_id = str(uuid.uuid4())
    guid = str(uuid.uuid4())
    
    url = "https://i.instagram.com/api/v1/accounts/send_password_reset/"
    
    headers = {
        "User-Agent": "Instagram 269.1.0.18.231 Android (29/10; 480dpi; 1080x2280; samsung; SM-G973F; beyond1; exynos9820; en_US; 441001473)",
        "X-IG-App-ID": "936619743392459",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    # البيانات بصيغة تطبيق الأندرويد لعام 2024
    data = {
        "user_email": email,
        "device_id": f"android-{device_id[:16]}",
        "guid": guid,
        "_csrftoken": "missing"
    }
    
    try:
        # إرسال الطلب
        response = scraper.post(url, data=data, headers=headers, timeout=15)
        res_text = response.text
        
        # إنستغرام يرسل 'status':'ok' إذا كان الإيميل موجود فعلاً
        if '"status":"ok"' in res_text or 'obfuscated_email' in res_text:
            return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ تم تحديث المحرك لتجاوز حماية إنستغرام الجديدة.\nأرسل الإيميل الآن للفحص.")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message.text)
    if not emails:
        bot.reply_to(message, "⚠️ ارسل إيميل صالح.")
        return

    for email in emails:
        status = check_email_fixed(email)
        if status:
            bot.send_message(message.chat.id, f"✅ مربوط: {email}")
        else:
            bot.send_message(message.chat.id, f"❌ غير مربوط أو محظور: {email}")

bot.polling()
