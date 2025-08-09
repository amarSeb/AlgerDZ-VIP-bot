# handlers.py
import telebot
from telebot import types
import uuid
import config
from utils import main_menu, payment_menu
from datetime import datetime
import json, csv, os, traceback

BOT = telebot.TeleBot(config.BOT_TOKEN, parse_mode="HTML")

# ملفات التخزين
DATA_JSON = "data.json"
DATA_CSV = "payments.csv"

def ensure_files():
    if not os.path.exists(DATA_JSON):
        with open(DATA_JSON, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
    if not os.path.exists(DATA_CSV):
        with open(DATA_CSV, "w", encoding="utf-8", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["record_id","user_id","username","name","payment_method","proof","date","confirmed"])

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_record(record: dict):
    ensure_files()
    # json
    try:
        with open(DATA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []
    data.append(record)
    with open(DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # csv
    with open(DATA_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            record.get("record_id"),
            record.get("user_id"),
            record.get("username"),
            record.get("name"),
            record.get("payment_method"),
            record.get("proof"),
            record.get("date"),
            record.get("confirmed", False)
        ])

# سجلات مؤقتة بالذاكرة: record_id -> record
PENDING = {}

# ===== Handlers registration =====
def register_handlers(bot: telebot.TeleBot):

    @bot.message_handler(commands=['start','menu'])
    def cmd_start(msg):
        bot.send_message(msg.chat.id, "مرحبًا 👋\nاختر من القائمة:", reply_markup=main_menu())

    @bot.message_handler(func=lambda m: m.text == "💳 الدفع والاشتراك")
    def show_pay(m):
        text, kb = payment_menu()
        bot.send_message(m.chat.id, text, reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "💰 الأسعار")
    def prices(m):
        bot.send_message(m.chat.id, f"💳 السعر: {config.PRICE_USD}\n🇩🇿 {config.PRICE_DZD}")

    @bot.message_handler(func=lambda m: m.text == "📚 كورس المبتدئين")
    def course(m):
        bot.send_message(m.chat.id, "📚 سيصلك الكورس بعد التفعيل. تابع القناة.")

    @bot.message_handler(func=lambda m: m.text == "🧠 القوانين")
    def rules(m):
        bot.send_message(m.chat.id, "📜 القوانين: الاحترام ـ ممنوع السبّ ـ لا نشر روابط/إعلانات")

    @bot.message_handler(func=lambda m: m.text == "👤 التواصل مع الدعم")
    def support(m):
        bot.send_message(m.chat.id, f"📩 تواصل مع الإدارة: tg://user?id={config.ADMIN_ID}")

    @bot.callback_query_handler(func=lambda c: True)
    def cb(c):
        try:
            uid = c.from_user.id
            data = c.data
            if data.startswith("pay_"):
                code = data.split("_",1)[1]
                mapping = {"paypal":"PayPal","baridi":"BaridiMob","usdt":"USDT"}
                method = mapping.get(code, code)
                bot.answer_callback_query(c.id, f"تم اختيار: {method}")
                if method == "PayPal":
                    bot.send_message(uid, f"💳 PayPal: <code>{config.PAYPAL_EMAIL}</code>\nأرسل إثبات الدفع أو اضغط 'إرسال إثبات الدفع'.", parse_mode="HTML")
                elif method == "BaridiMob":
                    bot.send_message(uid, f"📱 BaridiMob: <code>{config.BARIDIMOB_NUMBER}</code>\nأرسل إثبات الدفع أو اضغط 'إرسال إثبات الدفع'.", parse_mode="HTML")
                else:
                    lines = "\\n".join([f"• <code>{a}</code>" for a in config.USDT_ADDRESSES])
                    bot.send_message(uid, f"💸 USDT ({config.PRICE_USDT}):\\n{lines}\\nأرسل إثبات الدفع أو اضغط 'إرسال إثبات الدفع'.", parse_mode="HTML")
                # خزن آخر وسيلة بالذاكرة
                bot._last_payment = getattr(bot, "_last_payment", {})
                bot._last_payment[uid] = method
                return

            if data == "send_proof":
                bot.answer_callback_query(c.id, "أرسل إثبات الدفع الآن")
                bot.send_message(uid, "📸 أرسل الآن صورة/لقطة شاشة أو ملف إثبات الدفع.")
                return

            # approve / reject callbacks from admin (approve:RID, reject:RID)
            if data.startswith("approve:") or data.startswith("reject:"):
                if c.from_user.id != config.ADMIN_ID:
                    bot.answer_callback_query(c.id, "أنت لست الأدمن.")
                    return
                action, rid = data.split(":",1)
                rec = PENDING.get(rid)
                if not rec:
                    bot.answer_callback_query(c.id, "السجل غير موجود أو منتهي.")
                    return
                if action == "approve":
                    # حاول إنشاء invite link مؤقت إن كان VIP_CHAT_ID محدد
                    invite = config.VIP_INVITE_LINK
                    if config.VIP_CHAT_ID:
                        try:
                            inv = bot.create_chat_invite_link(config.VIP_CHAT_ID, member_limit=1)
                            invite = inv.invite_link
                        except Exception:
                            invite = config.VIP_INVITE_LINK
                    try:
                        bot.send_message(rec["user_id"], f"✅ تم تأكيد الدفع! تفضل رابط القناة:\n{invite}")
                        bot.send_message(config.ADMIN_ID, f"✅ تم تفعيل المستخدم {rec['user_id']}")
                        rec["confirmed"] = True
                        rec["confirmed_at"] = now()
                        save_record(rec)
                        # clean pending
                        del PENDING[rid]
                        bot.answer_callback_query(c.id, "تم التفعيل وإرسال الرابط.")
                    except Exception as e:
                        bot.answer_callback_query(c.id, f"خطأ إرسال الرابط: {e}")
                else:
                    # رفض
                    try:
                        bot.send_message(rec["user_id"], "❌ تم رفض إثبات الدفع. إذا كان هناك استفسار تواصل مع الإدارة.")
                        bot.send_message(config.ADMIN_ID, f"❌ تم رفض إثبات الدفع للمستخدم {rec['user_id']}")
                        rec["confirmed"] = False
                        rec["rejected_at"] = now()
                        save_record(rec)
                        del PENDING[rid]
                        bot.answer_callback_query(c.id, "تم رفض السجل.")
                    except Exception as e:
                        bot.answer_callback_query(c.id, f"خطأ أثناء الرفض: {e}")

        except Exception:
            traceback.print_exc()

    @bot.message_handler(content_types=['photo','document','text'])
    def receive_proof(m):
        try:
            # تجاهل أزرار القائمة
            if m.content_type == 'text' and m.text in ["💳 الدفع والاشتراك","💰 الأسعار","📚 كورس المبتدئين","🧠 القوانين","👤 التواصل مع الدعم"]:
                return

            uid = m.from_user.id
            username = getattr(m.from_user, "username", None)
            name = (getattr(m.from_user, "first_name", "") or "") + (" " + (getattr(m.from_user, "last_name", "") or "")).strip()
            method = getattr(bot, "_last_payment", {}).get(uid, "غير محدد")

            # forward media/text to admin and create pending record
            proof_summary = m.text if m.content_type == 'text' else m.content_type
            if m.content_type in ['photo','document']:
                try:
                    bot.forward_message(config.ADMIN_ID, m.chat.id, m.message_id)
                except Exception:
                    pass

            rid = uuid.uuid4().hex
            rec = {
                "record_id": rid,
                "user_id": uid,
                "username": username,
                "name": name,
                "payment_method": method,
                "proof": proof_summary,
                "date": now(),
                "confirmed": False
            }
            PENDING[rid] = rec
            save_record(rec)

            # send admin message with approve/reject buttons
            kb = types.InlineKeyboardMarkup(row_width=2)
            kb.add(
                types.InlineKeyboardButton("✅ قبول", callback_data=f"approve:{rid}"),
                types.InlineKeyboardButton("❌ رفض", callback_data=f"reject:{rid}")
            )
            admin_text = (
                f"📥 إثبات دفع جديد\n\n"
                f"👤 {rec['name']} (@{rec['username']})\n"
                f"🆔 <code>{rec['user_id']}</code>\n"
                f"💳 {rec['payment_method']}\n"
                f"🕒 {rec['date']}\n\n"
                "اضغط ✅ للموافقة أو ❌ للرفض."
            )
            try:
                bot.send_message(config.ADMIN_ID, admin_text, parse_mode="HTML", reply_markup=kb)
            except Exception:
                pass

            bot.send_message(uid, "✅ تم استلام إثبات الدفع. سيتم مراجعته من الإدارة خلال دقائق.")
        except Exception:
            traceback.print_exc()
                                              
