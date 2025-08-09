# utils.py
from telebot import types
import config

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💳 الدفع والاشتراك", "💰 الأسعار")
    kb.add("📚 كورس المبتدئين", "🧠 القوانين")
    kb.add("👤 التواصل مع الدعم")
    return kb

def payment_menu():
    text = (
        f"💳 **اشتراك VIP**\n\n"
        f"• السعر: {config.PRICE_USD}\n"
        f"• PayPal: {config.PAYPAL_EMAIL}\n"
        f"• BaridiMob: {config.BARIDIMOB_NUMBER}\n"
        f"• USDT (BEP20):\n  {config.USDT_ADDRESSES[0]}\n  {config.USDT_ADDRESSES[1]}\n\n"
        "بعد الدفع أرسل إثبات الدفع (صورة/لقطة شاشة) باستخدام زر 'إرسال إثبات الدفع'."
    )
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("💳 PayPal", callback_data="pay_paypal"),
        types.InlineKeyboardButton("📱 BaridiMob", callback_data="pay_baridi"),
        types.InlineKeyboardButton("💸 USDT", callback_data="pay_usdt"),
        types.InlineKeyboardButton("📨 إرسال إثبات الدفع", callback_data="send_proof")
    )
    return text, kb
  
