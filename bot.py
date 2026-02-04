import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from session_manager import SessionManager
from utils import get_flag_by_number, parse_combo

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# معلومات الدخول للوحة
PANEL_USER = "almoz3j"
PANEL_PASS = "hamoalmoz3j"
# توكن البوت (سيتم استبداله من قبل المستخدم)
BOT_TOKEN = "8373667774:AAELsngmB9k2NuofrA-8QIrP968VveH-mgw"
# أيدي حسابك في تليجرام (ضعه هنا ليكون البوت خاصاً بك فقط)
DEVELOPER_ID = 5545530980  # استبدله بالأيدي الخاص بك

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.session_mgr = SessionManager(PANEL_USER, PANEL_PASS)
        self.developer_id = DEVELOPER_ID
        self.last_messages = []

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        # حماية البوت: السماح للمطور فقط باستخدام البوت
        if user.id != self.developer_id:
            await update.message.reply_text("⚠️ عذراً، هذا البوت خاص ومحمي. لا يمكنك استخدامه.")
            return
            
        # محاولة تسجيل الدخول للوحة عند تشغيل البوت
        success, msg = self.session_mgr.login()
        status_msg = "✅ تم تسجيل الدخول في اللوحة بنجاح" if success else f"❌ فشل تسجيل الدخول في اللوحة: {msg}"
        
        welcome_text = (
            f"مرحباً {user.first_name} في بوت الأرقام الوهمية 🤖\n\n"
            f"حالة اللوحة: {status_msg}\n\n"
            "استخدم الأزرار أدناه للتحكم:"
        )
        
        keyboard = [
            [InlineKeyboardButton("📊 حالة اللوحة", callback_data='check_status')],
            [InlineKeyboardButton("📩 سحب الرسائل", callback_data='fetch_messages')],
            [InlineKeyboardButton("🌍 إدارة الأرقام", callback_data='manage_numbers')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = update.effective_user
        
        if user.id != self.developer_id:
            await query.answer("⚠️ غير مسموح لك.", show_alert=True)
            return
            
        await query.answer()
        
        if query.data == 'check_status':
            success, msg = self.session_mgr.login()
            status = "✅ متصل" if success else f"❌ غير متصل: {msg}"
            await query.edit_message_text(f"حالة الاتصال باللوحة: {status}")
            
        elif query.data == 'fetch_messages':
            messages = self.session_mgr.get_messages()
            if not messages:
                await query.edit_message_text("📭 لا توجد رسائل جديدة حالياً.")
            else:
                text = "📥 آخر الرسائل المستلمة:\n\n"
                for m in messages[:10]:
                    flag = get_flag_by_number(m['number'])
                    text += f"{flag} الرقم: {m['number']}\n💬 الرسالة: {m['sms']}\n⏰ التاريخ: {m['date']}\n"
                    text += "------------------------\n"
                await query.edit_message_text(text)
        
        elif query.data.startswith('num_'):
            target_num = query.data.split('_')[1]
            await query.edit_message_text(f"🔍 جاري البحث عن كود للرقم {target_num}...")
            
            # محاولة البحث عن الكود (تكرار لعدة مرات)
            for _ in range(5):
                code, full_sms = self.session_mgr.find_code_for_number(target_num)
                if full_sms:
                    result_text = f"✅ تم استلام رسالة للرقم {target_num}:\n\n💬 النص: {full_sms}\n"
                    if code:
                        result_text += f"🔢 الكود المستخرج: `{code}`"
                    await query.edit_message_text(result_text)
                    return
                await asyncio.sleep(5) # انتظار 5 ثواني قبل المحاولة التالية
            
            await query.edit_message_text(f"❌ لم يتم استلام أي كود للرقم {target_num} حتى الآن. حاول مرة أخرى لاحقاً.")

    async def handle_combo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id != self.developer_id:
            return

        text = update.message.text
        numbers = parse_combo(text)
        
        if not numbers:
            return

        keyboard = []
        for n in numbers[:10]: # تحديد أول 10 أرقام لتجنب الرسائل الطويلة جداً
            btn_text = f"{n['flag']} {n['number']}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"num_{n['number']}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("✅ تم تحليل الأرقام، اختر الرقم لطلب الكود:", reply_markup=reply_markup)

    def run(self):
        application = ApplicationBuilder().token(self.token).build()
        
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_combo))
        
        print("Bot is running...")
        application.run_polling()

if __name__ == "__main__":
    # ملاحظة: يجب وضع التوكن الصحيح هنا
    bot = TelegramBot(BOT_TOKEN)
    # bot.run() # سيتم تشغيله لاحقاً
