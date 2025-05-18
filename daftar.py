from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

# 🔒 Bot tokeningiz va admin ID’sini shu yerda sozlang
TOKEN = '7970640999:AAFV3zwmAcFahpL6PnUdaZdOvGOLeg7jFeY'  # <-- Bu yerga o'z bot tokeningizni yozing
ADMIN_CHAT_ID = 5189578374  # <-- Bu yerga admin Telegram ID’sini yozing (raqam ko'rinishida)

# Bosqichlar nomlari
ASK_NAME, ASK_SURNAME, ASK_CONTACT = range(3)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Iltimos, ismingizni to'g'ri kiritishingizni so'raymiz .:")
    return ASK_NAME

# Ismni olish
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['first_name'] = update.message.text
    await update.message.reply_text("Endi familiyangizni kiriting.Buni ham to'g'ri kiritshingizni so'raymiz:")
    return ASK_SURNAME

# Familiyani olish
async def ask_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['last_name'] = update.message.text
    button = KeyboardButton("📞 Raqamni yuborish", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Iltimos, telefon raqamingizni yuboring:", reply_markup=reply_markup)
    return ASK_CONTACT

# Raqamni olish va admin ga yuborish
async def ask_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact and contact.phone_number:
        context.user_data['phone'] = contact.phone_number
        full_name = f"{context.user_data['first_name']} {context.user_data['last_name']}"

        # Foydalanuvchiga tasdiqlovchi xabar
        await update.message.reply_text(
            f"Rahmat!\n✅ Ma'lumotlaringiz biz shu bo'yicha sizga sovg'a ajratamiz:\n"
            f"Ism: {context.user_data['first_name']}\n"
            f"Familiya: {context.user_data['last_name']}\n"
            f"Telefon raqam: {context.user_data['phone']}"
        )

        # Adminga yuboriladigan xabar
        message_to_admin = (
            f"📥 Yangi foydalanuvchi ma'lumotlari:\n\n"
            f"👤 Ism: {context.user_data['first_name']}\n"
            f"👤 Familiya: {context.user_data['last_name']}\n"
            f"📞 Telefon raqam: {context.user_data['phone']}\n"
            f"🆔 Telegram ID: {update.message.from_user.id}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_to_admin)

        return ConversationHandler.END
    else:
        # Agar foydalanuvchi noto‘g‘ri malumot yuborsa
        button = KeyboardButton("📞 Raqamni yuborish", request_contact=True)
        reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "❗ Iltimos, tugmadan foydalanib telefon raqamingizni yuboring.",
            reply_markup=reply_markup
        )
        return ASK_CONTACT

# Jarayonni bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Jarayon bekor qilindi.")
    return ConversationHandler.END

# Asosiy bot funksiyasi
def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_surname)],
            ASK_CONTACT: [
                MessageHandler(filters.CONTACT, ask_contact),
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_contact)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()



