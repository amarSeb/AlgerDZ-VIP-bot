# main.py
import time
import handlers
from handlers import BOT

print("✅ Bot is starting (polling)...")

# تسجيل المعالجات
handlers.register_handlers(BOT)

# احذف أي webhook قديم لتفادي التعارض (محاولة صامتة)
import requests, config
try:
    requests.get(f"https://api.telegram.org/bot{config.BOT_TOKEN}/deleteWebhook", timeout=5)
except Exception:
    pass

# تشغيل البوت مع retry على استثناءات
while True:
    try:
        BOT.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("Polling error:", e)
        time.sleep(5)
      
