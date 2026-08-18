import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8670114208:AAH6CLCSVto9RET2tElugSQty1bHc9RMKKc"
VIP_CHANNEL_ID = -1004424341978

logging.basicConfig(level=logging.INFO)

def get_allowed_ids():
    try:
        with open("trader_ids.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **Binary VIP Verification Bot-এ স্বাগতম!**\n\n"
        "আমাদের VIP গ্রুপে যুক্ত হতে আপনার **Trader ID** পাঠালুন (যেমন: 123456)।"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def verify_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_input = update.message.text.strip()
    allowed_ids = get_allowed_ids()
    
    if user_id_input in allowed_ids:
        await update.message.reply_text("✅ আপনার Trader ID সঠিক পাওয়া গেছে! VIP ইনভাইট লিংক তৈরি হচ্ছে...")
        try:
            invite_link = await context.bot.create_chat_invite_link(
                chat_id=VIP_CHANNEL_ID,
                member_limit=1
            )
            await update.message.reply_text(
                f"🎉 অভিনন্দন! আপনার VIP গ্রুপের ইনভাইট লিংক:\n\n{invite_link.invite_link}\n\n"
                "⚠️ *নোট: এই লিংকটি শুধু একবার ব্যবহার করা যাবে।*",
                parse_mode="Markdown"
            )
        except Exception as e:
            await update.message.reply_text("❌ VIP লিংক তৈরি করতে সমস্যা হচ্ছে। নিশ্চিত করুন বটটি আপনার VIP গ্রুপে অ্যাডমিন আছে।")
            print(f"Error: {e}")
    else:
        await update.message.reply_text(
            "❌ **Trader ID পাওয়া যায়নি!**\n\n"
            "দয়া করে নিশ্চিত করুন আপনার আইডি সঠিক এবং ডিপোজিট সম্পন্ন করেছেন।"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verify_id))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
