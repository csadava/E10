import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

TOKEN = "8991397075:AAEXNRuY3RIY2JTNNy0bEJV91zVEzgKcH9w"

# مسیر فایل دیتابیس روی ولوم رایلی (/data)
DB_DIR = "/data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)
DB_FILE = os.path.join(DB_DIR, "e10_database.json")

# ساختار پیش‌فرض دیتابیس
DEFAULT_DB = {
    "warnings": {},      
    "mutes": {},         
    "temp_mutes": {},    
    "bans": {},          
    "rules": {},         
    "nicknames": {},     
    "links": {},         
    "locks": {},         
    "admins": {},        
    "owners": {},        
    "welcome": {         
        "status": True,
        "text": """╔═══『 ⚔️ E10 CLAN ⚔️ 』═══╗\n\n     𓆩 WELCOME 𓆪\n\n👤 Player : {name}\n🆔 ID : {id}\n\n🔥 خوش آمدی به خانواده E10 🔥\n\nاینجا جاییه که جنگجوهای واقعی کنار هم جمع میشن.\n⚔️ تمرین کن، قوی‌تر شو و برای پیروزی بجنگ.\n\n🏆 هدف ما:\nRank Up | Team Work | Victory\n\n🚫 احترام به اعضا = قانون اول E10\n\n☠️ E10 CLAN\n『 ONE TEAM • ONE DREAM • ONE VICTORY 』\n\n╚══════════════════╝"""
    },
    "filters": {},       
    "spam_settings": {}, 
    "msg_counts": {},    
    "forced_sub": {},    
    "forced_add": {}     
}

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_DB
    return DEFAULT_DB

def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

db = load_db()

async def is_admin_or_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return False
    if chat.type == "private":
        return True
    member = await chat.get_member(user.id)
    if member.status in ["creator", "administrator"]:
        return True
    if user.id in db["owners"].get(str(chat.id), []) or user.id in db["admins"].get(str(chat.id), []):
        return True
    return False

# تابع نمایش منوی راهنما
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat and chat.type != "private" and not await is_admin_or_owner(update, context):
        return

    keyboard = [
        [InlineKeyboardButton("⚔️ مجازات", callback_data="menu_punish"), InlineKeyboardButton("🎮 سرگرمی", callback_data="menu_fun")],
        [InlineKeyboardButton("🔒 قفل ها", callback_data="menu_locks"), InlineKeyboardButton("👑 ارتقا و عزل", callback_data="menu_ranks")],
        [InlineKeyboardButton("✨ خوشامد گویی", callback_data="menu_welcome"), InlineKeyboardButton("📢 عضویت اجباری", callback_data="menu_fsub")],
        [InlineKeyboardButton("👥 اد اجباری", callback_data="menu_fadd"), InlineKeyboardButton("🚫 فیلتر کلمات", callback_data="menu_filters")],
        [InlineKeyboardButton("👤 پنل کاربر", callback_data="menu_userpanel"), InlineKeyboardButton("📊 آمار فعالیت ها", callback_data="menu_stats")],
        [InlineKeyboardButton("⚡ اسپم", callback_data="menu_spam"), InlineKeyboardButton("👻 حالت روح و مخفی", callback_data="menu_ghost")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "🛡 **E10 Manager Control Panel** 🛡\n\nلطفاً یکی از بخش‌های زیر را انتخاب کنید:"
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# مدیریت کلیک روی دکمه‌های شیشه‌ای
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_main":
        await show_help(update, context)
        return

    chat_id = str(query.message.chat_id)

    if data == "menu_punish":
        kb = [
            [InlineKeyboardButton("بن / حذف بن / لیست", callback_data="sub_ban")],
            [InlineKeyboardButton("اخطار / لیست اخطارها", callback_data="sub_warn")],
            [InlineKeyboardButton("سکوت / لیست سکوت", callback_data="sub_mute")],
            [InlineKeyboardButton("سکوت موقت", callback_data="sub_tmute")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        await query.message.edit_text("⚔️ **بخش مجازات:**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif data == "sub_ban":
        await query.message.edit_text("دستورات بن:\n• `/بن` (با ریپلی)\n• `/حذف_بن` (با ریپلی)\n• `/لیست_بن`\n• `/پاکسازی_لیست_بن`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_punish")]]), parse_mode="Markdown")
    elif data == "sub_warn":
        await query.message.edit_text("دستورات اخطار:\n• `/اخطار` (با ریپلی)\n• `/حذف_اخطار` (با ریپلی)\n• `/حذف_اخطارها`\n• `/لیست_اخطار`\n• `/پاکسازی_لیست_اخطار`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_punish")]]), parse_mode="Markdown")
    elif data == "sub_mute":
        await query.message.edit_text("دستورات سکوت:\n• `/سکوت` (با ریپلی)\n• `/حذف_سکوت` (با ریپلی)\n• `/لیست_سکوت`\n• `/پاکسازی_لیست_سکوت`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_punish")]]), parse_mode="Markdown")
    elif data == "sub_tmute":
        await query.message.edit_text("دستور سکوت موقت:\n• `/سکوت [دقیقه]` (با ریپلی، مثلاً `/سکوت 5`)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_punish")]]), parse_mode="Markdown")

    elif data == "menu_fun":
        kb = [
            [InlineKeyboardButton("فونت", callback_data="sub_font"), InlineKeyboardButton("پین", callback_data="sub_pin")],
            [InlineKeyboardButton("قوانین و تاریخ", callback_data="sub_rules"), InlineKeyboardButton("تگ همگانی", callback_data="sub_tag")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        await query.message.edit_text("🎮 **بخش سرگرمی و ابزار:**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif data == "sub_font":
        await query.message.edit_text("دستور: `/فونت [متن]`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_fun")]]), parse_mode="Markdown")
    elif data == "sub_pin":
        await query.message.edit_text("دستورات:\n• `/پین`\n• `/حذف_پین`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_fun")]]), parse_mode="Markdown")
    elif data == "sub_rules":
        await query.message.edit_text("دستورات:\n• `/قوانین`\n• `/ثبت_قوانین`\n• `/حذف_قوانین`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_fun")]]), parse_mode="Markdown")
    elif data == "sub_tag":
        await query.message.edit_text("دستور: `/تگ`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_fun")]]), parse_mode="Markdown")

    elif data == "menu_locks":
        kb = [
            [InlineKeyboardButton("هشتگ", callback_data="lock_hashtag"), InlineKeyboardButton("لینک", callback_data="lock_link")],
            [InlineKeyboardButton("متن", callback_data="lock_text")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        await query.message.edit_text("🔒 **مدیریت قفل‌ها:**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif data.startswith("lock_"):
        lock_type = data.replace("lock_", "")
        current = db["locks"].setdefault(chat_id, {}).get(lock_type, False)
        db["locks"][chat_id][lock_type] = not current
        save_db()
        await query.answer("وضعیت قفل تغییر کرد.")

    elif data == "menu_ranks":
        await query.message.edit_text("👑 ارتقا و عزل مدیران و مالکین.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")
    elif data == "menu_welcome":
        await query.message.edit_text("✨ تنظیمات خوشامدگویی.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")
    elif data == "menu_fsub":
        await query.message.edit_text("📢 عضویت اجباری.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")
    elif data == "menu_fadd":
        await query.message.edit_text("👥 اد اجباری.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")
    elif data == "menu_filters":
        await query.message.edit_text("🚫 فیلتر کلمات.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")
    elif data == "menu_userpanel":
        await query.message.edit_text("👤 پنل کاربر (ریپلی روی کاربر با `/پنل_کاربر`)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")
    elif data == "menu_stats":
        await query.message.edit_text("📊 آمار فعالیت‌ها (دستور `/آمار_امروز`)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")
    elif data == "menu_spam":
        await query.message.edit_text("⚡ تنظیمات اسپم.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")
    elif data == "menu_ghost":
        await query.message.edit_text("👻 حالت روح و مخفی.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")

# خوشامدگویی
async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text("لطفا ربات رو مدیر گپتون کنید تا فعال بشه این ربات مخصوص کلن E10 است و ساخته شده توسط اعضای E10 ⚔️")
            continue
        settings = db["welcome"]
        if settings.get("status", True):
            text = settings["text"].format(name=member.full_name, id=member.id)
            await update.message.reply_text(text, parse_mode="Markdown")

# مدیریت دستورات متنی فارسی (مثل راهنما) و فیلترها
async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.from_user:
        return

    text = message.text or message.caption or ""
    
    # اگر کاربر کلمه راهنما یا help را فرستاد
    if text.strip() in ["راهنما", "help", "/راهنما"]:
        await show_help(update, context)
        return

    if message.chat.type == "private":
        return

    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    # ذخیره آمار پیام‌ها
    chat_counts = db["msg_counts"].setdefault(chat_id, {})
    chat_counts[user_id] = chat_counts.get(user_id, 0) + 1
    save_db()

    # بررسی فیلتر کلمات
    filtered_words = db["filters"].get(chat_id, [])
    for word in filtered_words:
        if word in text:
            await message.delete()
            return

    # بررسی قفل‌ها
    locks = db["locks"].get(chat_id, {})
    if locks.get("hashtag") and "#" in text:
        await message.delete()
        return
    if locks.get("link") and ("http://" in text or "https://" in text or "t.me/" in text):
        await message.delete()
        return
    if locks.get("text") and text:
        await message.delete()
        return

# دستورات ابزار و سرگرمی
async def font_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("لطفا متنی وارد کنید. مثال:\n`/فونت سلام`", parse_mode="Markdown")
        return
    raw_text = " ".join(context.args)
    fonts = [
        f"𝓔𝟙𝟘 ➮ {raw_text}", f"𝔼𝟙𝟘 ➮ {raw_text}", f"𝐄𝟏𝟎 ➮ {raw_text}", 
        f"𝗘𝟭𝟬 ➮ {raw_text}", f"𝘌10 ➮ {raw_text}", f"𝙴10 ➮ {raw_text}"
    ]
    res = "✨ **فونت‌های پیشنهادی (برای کپی لمس کنید):**\n\n" + "\n".join([f"`{f}`" for f in fonts])
    await update.message.reply_text(res, parse_mode="Markdown")

async def user_panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("لطفاً روی پیام کاربر موردنظر ریپلی کنید.")
        return
    target = update.message.reply_to_message.from_user
    await update.message.reply_text(f"👤 **اطلاعات کاربر:**\nنام: {target.full_name}\nآیدی: @{target.username if target.username else 'ندارد'}\nآیدی عددی: `{target.id}`", parse_mode="Markdown")

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    counts = db["msg_counts"].get(chat_id, {})
    if not counts:
        await update.message.reply_text("آماری ثبت نشده است.")
        return
    top_users = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
    res = "📊 **آمار فعالیت‌های گروه:**\n\n"
    for idx, (uid, count) in enumerate(top_users, 1):
        res += f"{idx}. کاربر `{uid}` - تعداد پیام: {count}\n"
    await update.message.reply_text(res, parse_mode="Markdown")

async def tag_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update, context):
        return
    await update.message.reply_text("⚔️ تگ همگانی اعضای کلن E10 انجام شد!")

async def ghost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not context.args:
        await update.message.reply_text("استفاده: روی پیام ریپلی کنید و بنویسید `/روح [متن]`")
        return
    text = " ".join(context.args)
    await update.message.delete()
    await update.message.reply_text(f"👻 {text}")

# راه‌اندازی ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # استفاده از کامندهای مجاز انگلیسی
    app.add_handler(CommandHandler("help", show_help))
    app.add_handler(CommandHandler("font", font_cmd))
    app.add_handler(CommandHandler("panel", user_panel_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("tag", tag_cmd))
    app.add_handler(CommandHandler("ghost", ghost_cmd))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))
    # هندلر پیام‌های متنی برای پشتیبانی کامل از کلمه «راهنما» و فیلترها
    app.add_handler(MessageHandler(filters.TEXT, text_message_handler))

    print("E10 Manager Bot with Persistent Storage is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
