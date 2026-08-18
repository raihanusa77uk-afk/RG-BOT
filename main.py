import logging
import os
import requests
import time
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. Web Server for Render Free Tier ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "VIP Verification & Management Bot is Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

def ping_self():
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        return
    while True:
        time.sleep(600)
        try:
            requests.get(url)
        except Exception:
            pass

def start_ping_thread():
    t = Thread(target=ping_self)
    t.daemon = True
    t.start()

# --- 2. Bot Configurations ---
BOT_TOKEN = "8670114208:AAH6CLCSVto9RET2tElugSQty1bHc9RMKKc"
VIP_CHANNEL_ID = -1004424341978

# ⚠️ আপনার এবং বাকি অ্যাডমিনদের Telegram Numeric User ID এখানে দিন
ADMIN_IDS = [123456789, 987654321] 

logging.basicConfig(level=logging.INFO)

# --- Helper Functions ---
def get_allowed_ids():
    try:
        with open("trader_ids.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_allowed_ids(ids_list):
    with open("trader_ids.txt", "w") as f:
        for tid in ids_list:
            f.write(f"{tid}\n")

def save_user_id(user_id):
    users = get_all_users()
    if str(user_id) not in users:
        with open("users.txt", "a") as f:
            f.write(f"{user_id}\n")

def get_all_users():
    try:
        with open("users.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

# --- User Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user_id(update.effective_user.id)
    welcome_text = (
        "👋 **Binary VIP Verification Bot-এ স্বাগতম!**\n\n"
        "আমাদের VIP গ্রুপে যুক্ত হতে আপনার **Trader ID** পাঠান (যেমন: 123456)।"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def verify_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user_id(update.effective_user.id)
    user_id_input = update.message.text.strip()
    allowed_ids = get_allowed_ids()
    
    if user_id_input in allowed_ids:
        await update.message.reply_text("✅ আপনার Trader ID সঠিক পাওয়া গেছে! VIP ইনভাইট লিংক তৈরি হচ্ছে...")
        try:
            # ১ জন মেম্বার এবং ২৪ ঘণ্টার মেয়াদ সহ ইনভাইট লিংক
            expire_date = int(time.time()) + 86400  # 24 Hours
            invite_link = await context.bot.create_chat_invite_link(
                chat_id=VIP_CHANNEL_ID,
                member_limit=1,
                expire_date=expire_date
            )
            await update.message.reply_text(
                f"🎉 অভিনন্দন! আপনার VIP গ্রুপের ইনভাইট লিংক:\n\n{invite_link.invite_link}\n\n"
                "⚠️ *নোট: এই লিংকটি ১ বার ব্যবহারযোগ্য এবং আগামী ২৪ ঘণ্টা পর্যন্ত কার্যকর থাকবে।*",
                parse_mode="Markdown"
            )
        except Exception as e:
            await update.message.reply_text("❌ VIP লিংক তৈরি করতে সমস্যা হচ্ছে। নিশ্চিত করুন বটটি আপনার VIP গ্রুপে Admin পদে আছে।")
            print(f"Error: {e}")
    else:
        await update.message.reply_text(
            "❌ **Trader ID পাওয়া যায়নি!**\n\n"
            "দয়া করে নিশ্চিত করুন আপনার আইডি সঠিক এবং ডিপোজিট সম্পন্ন করেছেন।"
        )

# --- Admin Panel Commands ---
async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    help_text = (
        "⚙️ **Advanced Admin Panel**\n\n"
        "• `/add <ID>` - আইডি যোগ করুন\n"
        "• `/remove <ID>` - আইডি মুছুন\n"
        "• `/search <ID>` - আইডি চেক করুন\n"
        "• `/list` - নিবন্ধিত সব আইডির তালিকা\n"
        "• `/stats` - বটের মেম্বার সংখ্যা ও ডাটা\n"
        "• `/broadcast <মেসেজ>` - সব ইউজারকে মেসেজ পাঠান\n"
        "• **ফাইল আপলোড:** `.txt` ফাইল পাঠালে একসাথে অনেক আইডি যোগ হবে।"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ ব্যবহার পদ্ধতি: `/add 123456`", parse_mode="Markdown")
        return

    new_id = context.args[0].strip()
    allowed_ids = get_allowed_ids()

    if new_id in allowed_ids:
        await update.message.reply_text("⚠️ এই Trader ID-টি আগেই যুক্ত আছে।")
    else:
        allowed_ids.append(new_id)
        save_allowed_ids(allowed_ids)
        await update.message.reply_text(f"✅ Trader ID `{new_id}` সফলভাবে যোগ করা হয়েছে!", parse_mode="Markdown")

async def remove_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text("⚠️ ব্যবহার পদ্ধতি: `/remove 123456`", parse_mode="Markdown")
        return

    target_id = context.args[0].strip()
    allowed_ids = get_allowed_ids()

    if target_id in allowed_ids:
        allowed_ids.remove(target_id)
        save_allowed_ids(allowed_ids)
        await update.message.reply_text(f"🗑️ Trader ID `{target_id}` সফলভাবে মুছে ফেলা হয়েছে।", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ এই Trader ID-টি তালিকায় পাওয়া যায়নি।")

async def search_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text("⚠️ ব্যবহার পদ্ধতি: `/search 123456`", parse_mode="Markdown")
        return

    target_id = context.args[0].strip()
    allowed_ids = get_allowed_ids()

    if target_id in allowed_ids:
        await update.message.reply_text(f"🔍 **Trader ID `{target_id}` তালিকায় বিদ্যমান আছে!**", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Trader ID `{target_id}` তালিকায় নেই।", parse_mode="Markdown")

async def list_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    allowed_ids = get_allowed_ids()
    if not allowed_ids:
        await update.message.reply_text("📂 তালিকায় কোনো Trader ID নেই।")
        return

    ids_text = "\n".join([f"• `{tid}`" for tid in allowed_ids[:50]]) # প্রথম ৫০টি দেখাবে
    await update.message.reply_text(
        f"📋 **অনুমোদিত ID (মোট {len(allowed_ids)} টি):**\n\n{ids_text}", 
        parse_mode="Markdown"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    allowed_ids = get_allowed_ids()
    users = get_all_users()
    
    stat_msg = (
        "📊 **Bot Statistics**\n\n"
        f"• মোট অনুমোদিত Trader ID: `{len(allowed_ids)}` টি\n"
        f"• বট স্টার্ট করা মোট ইউজার: `{len(users)}` জন"
    )
    await update.message.reply_text(stat_msg, parse_mode="Markdown")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text("⚠️ ব্যবহার পদ্ধতি: `/broadcast আপনার মেসেজ`", parse_mode="Markdown")
        return

    msg = " ".join(context.args)
    users = get_all_users()
    success = 0

    for uid in users:
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 **অফিসিয়াল নোটিশ:**\n\n{msg}", parse_mode="Markdown")
            success += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ সর্বমোট `{success}` জন ইউজারের কাছে নোটিশটি পাঠানো হয়েছে।", parse_mode="Markdown")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    doc = update.message.document
    if doc.file_name.endswith('.txt'):
        file = await context.bot.get_file(doc.file_id)
        content = await file.download_as_bytearray()
        lines = content.decode('utf-8').splitlines()
        
        allowed_ids = get_allowed_ids()
        count = 0
        for line in lines:
            tid = line.strip()
            if tid and tid not in allowed_ids:
                allowed_ids.append(tid)
                count += 1
                
        save_allowed_ids(allowed_ids)
        await update.message.reply_text(f"📁 ফাইল থেকে নতুন `{count}` টি Trader ID যুক্ত করা হয়েছে!", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ শুধুমাত্র `.txt` ফাইল আপলোড করুন।")

# --- Main App ---
def main():
    keep_alive()
    start_ping_thread()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # User Handlers
    app.add_handler(CommandHandler("start", start))
    
    # Admin Handlers
    app.add_handler(CommandHandler("admin", admin_help))
    app.add_handler(CommandHandler("add", add_id))
    app.add_handler(CommandHandler("remove", remove_id))
    app.add_handler(CommandHandler("search", search_id))
    app.add_handler(CommandHandler("list", list_ids))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    # File Handler for Admins
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Text Verification
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verify_id))
    
    print("Advanced VIP Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
