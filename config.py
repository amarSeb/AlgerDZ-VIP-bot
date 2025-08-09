# config.py
import os

# الأفضل: ضع التوكن كمتغير بيئة في Render (BOT_TOKEN)
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "8218899898:AAEXxoTyv3tG6aiVz5c5rEX2wxyvFwttN9w"

# Admin ID (يمكنك وضعه هنا أو كمتغير بيئة ADMIN_ID)
ADMIN_ID = int(os.environ.get("ADMIN_ID") or "5130562279")

# رابط دعوة القناة (invite link) الافتراضي
VIP_INVITE_LINK = os.environ.get("VIP_INVITE_LINK") or "https://t.me/+jWHdmsigzz5hZDRk"

# (اختياري) إذا كنت تعرف numeric chat id للقناة (مثل -100123...), ضعها هنا أو كمتغير VIP_CHAT_ID
# عندما تضعه، والبوت أدمن في القناة، سيحاول إنشاء invite link مؤقت عند التفعيل.
VIP_CHAT_ID = os.environ.get("VIP_CHAT_ID") or None
if VIP_CHAT_ID:
    try:
        VIP_CHAT_ID = int(VIP_CHAT_ID)
    except:
        VIP_CHAT_ID = None

# بيانات الدفع (مملوءة حسب ما زودتني به)
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL") or "mimoucanadien01@gmail.com"
BARIDIMOB_NUMBER = os.environ.get("BARIDIMOB_NUMBER") or "00799999001806537421"
USDT_ADDRESSES = [
    os.environ.get("USDT1") or "0x1aaa53596e4a3fc411bdf5c8c9c315b2253bcbda",
    os.environ.get("USDT2") or "0x4ec85ef2dca621ed2cdd0dbed7a9ee2d5d688f20"
]

# الأسعار
PRICE_USD = os.environ.get("PRICE_USD") or "200$ (مدى الحياة)"
PRICE_DZD = os.environ.get("PRICE_DZD") or "48000 DA"
PRICE_USDT = os.environ.get("PRICE_USDT") or "200 USDT"
