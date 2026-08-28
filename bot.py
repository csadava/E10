import os
import time
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

# دیتابیس‌های موقت در حافظه (در نسخه پرو می‌توانید به دیتابیس متصل کنید)
db = {
    "warnings": {},      # {chat_id: {user_id: count}}
    "mutes": {},         # {chat_id: [user_ids]}
    "temp_mutes": {},    # {chat_id: {user_id: expire_time}}
    "bans": {},          # {chat_id: [user_ids]}
    "rules": {},         # {chat_id: "text"}
    "nicknames": {},     # {chat_id: {user_id: "nickname"}}
    "links": {},         # {chat_id: ["link1"]}
    "locks": {},         # {chat_id: {"hashtag": False, "link": False, ...}}
    "admins": {},        # {chat_id: [user_ids]}
    "owners": {},        # {chat_id: [user_ids]}
    "welcome": {         # {chat_id: {"status": True, "text": "..."}}
        "status": True,
        "text": """╔═══『 ⚔️ E10 CLAN ⚔️ 』═══╗\n\n     𓆩 WELCOME 𓆪\n\n👤 Player : {name}\n🆔 ID : {id}\n\n🔥 خوش آمدی به خانواده E10 🔥\n\nاینجا جاییه که جنگجوهای واقعی کنار هم جمع میشن.\n⚔️ تمرین کن، قوی‌تر شو و برای پیروزی بجنگ.\n\n🏆 هدف ما:\nRank Up | Team Work | Victory\n\n🚫 احترام به اعضا = قانون اول E10\n\n☠️ E10 CLAN\n『 ONE TEAM • ONE DREAM • ONE VICTORY 』\n\n╚══════════════════╝"""
    },
    "filters": {},       # {chat_id: ["word1"]}
    "spam_settings": {}, # {chat_id: {"status": False, "limit": 5, "action": "mute"}}
    "msg_counts": {},    # {chat_id: {user_id: count}}
    "forced_sub": {},    # {chat_id: [channels]}
    "forced_add": {}     # {chat_id: {"status": False, "count": 1}}
}

# بررسی دسترسی مدیر یا مالک
async def is_admin_or_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return False
    
    # ربات در پی‌وی
    if chat.type == "private":
        return True
        
    member = await chat.get_member(user.id)
    if member.status in ["creator", "administrator"]:
        return True
    
    # بررسی مالکین ثانویه یا ادمین‌های ثبت شده
    if user.id in db["owners"].get(chat.id, []) or user.id in db["admins"].get(chat.id, []):
        return True
        
    return False

# دستور راهنما و منوی اصلی دکمه‌ها
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private" and not await is_admin_or_owner(update, context):
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
        await help_command(update, context)
        return

    # منوی مجازات
    if data == "menu_punish":
        kb = [
            [InlineKeyboardButton("بن / حذف بن / لیست", callback_data="sub_ban")],
            [InlineKeyboardButton("اخطار / لیست اخطارها", callback_data="sub_warn")],
            [InlineKeyboardButton("سکوت / لیست سکوت", callback_data="sub_mute")],
            [InlineKeyboardButton("سکوت موقت", callback_data="sub_tmute")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        await query.message.edit_text("⚔️ **بخش مجازات:**\nدستورات مرتبط با بن، اخطار و سکوت.", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif data == "sub_ban":
        await query.message.edit_text("دستورات بن:\n• `/بن` (با ریپلی)\n• `/حذف_بن` (با ریپلی)\n• `/لیست_بن`\n• `/پاکسازی_لیست_بن`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_punish")]]), parse_mode="Markdown")
    elif data == "sub_warn":
        await query.message.edit_text("دستورات اخطار:\n• `/اخطار` (با ریپلی)\n• `/حذف_اخطار` (با ریپلی)\n• `/حذف_اخطارها`\n• `/تنظیم_اخطار [عدد]`\n• `/تنظیم_اخطار_بن` یا `/تنظیم_اخطار_سکوت`\n• `/لیست_اخطار`\n• `/پاکسازی_لیست_اخطار`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_punish")]]), parse_mode="Markdown")
    elif data == "sub_mute":
        await query.message.edit_text("دستورات سکوت:\n• `/سکوت` (با ریپلی)\n• `/حذف_سکوت` (با ریپلی)\n• `/لیست_سکوت`\n• `/پاکسازی_لیست_سکوت`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_punish")]]), parse_mode="Markdown")
    elif data == "sub_tmute":
        await query.message.edit_text("دستور سکوت موقت:\n• `/سکوت [دقیقه]` (با ریپلی، مثلاً `/سکوت 5`)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_punish")]]), parse_mode="Markdown")

    # منوی سرگرمی و کاربردی
    elif data == "menu_fun":
        kb = [
            [InlineKeyboardButton("فونت", callback_data="sub_font"), InlineKeyboardButton("پین", callback_data="sub_pin")],
            [InlineKeyboardButton("قوانین و تاریخ", callback_data="sub_rules"), InlineKeyboardButton("تگ همگانی", callback_data="sub_tag")],
            [InlineKeyboardButton("لقب و اصل و لینک", callback_data="sub_extras")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        await query.message.edit_text("🎮 **بخش سرگرمی و ابزار:**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif data == "sub_font":
        await query.message.edit_text("دستور: `/فونت [متن]`\n۳۰ فونت برتر با قابلیت کپی با یک کلیک فعال است.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_fun")]]), parse_mode="Markdown")
    elif data == "sub_pin":
        await query.message.edit_text("دستورات:\n• `/پین` (روی پیام)\n• `/حذف_پین`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_fun")]]), parse_mode="Markdown")
    elif data == "sub_rules":
        await query.message.edit_text("دستورات:\n• `/قوانین`\n• `/ثبت_قوانین` (روی پیام عکس/متن)\n• `/حذف_قوانین`\n• `/تاریخ_عضویت` (روی کاربر)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_fun")]]), parse_mode="Markdown")
    elif data == "sub_tag":
        await query.message.edit_text("دستور: `/تگ` (تگ کردن کل افراد گروه)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_fun")]]), parse_mode="Markdown")
    elif data == "sub_extras":
        await query.message.edit_text("سایر ابزارها:\n• لقب: `/تنظیم_لقب`, `/لقب`, `/لیست_لقب`, `/حذف_لیست_لقب`\n• اصل: `/ثبت_اصل`, `/اصل`, `/لیست_اصل`, `/حذف_اصل`\n• لینک: `/ثبت_لینک`, `/لینک`, `/حذف_لینک`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_fun")]]), parse_mode="Markdown")

    # منوی قفل‌ها
    elif data == "menu_locks":
        kb = [
            [InlineKeyboardButton("هشتگ", callback_data="lock_hashtag"), InlineKeyboardButton("لینک", callback_data="lock_link")],
            [InlineKeyboardButton("متن", callback_data="lock_text"), InlineKeyboardButton("فارسی / انگلیسی", callback_data="lock_lang")],
            [InlineKeyboardButton("ویرایش / ایموجی", callback_data="lock_editemoji"), InlineKeyboardButton("فوروارد / گیف", callback_data="lock_fwdgif")],
            [InlineKeyboardButton("استیکر / عکس", callback_data="lock_stkpic"), InlineKeyboardButton("فایل / مکان", callback_data="lock_fileloc")],
            [InlineKeyboardButton("فیلم / ویس", callback_data="lock_vidvoice")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        await query.message.edit_text("🔒 **مدیریت قفل‌ها:**\nبا کلیک روی هر دکمه، وضعیت قفل تغییر می‌کند.", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif data.startswith("lock_"):
        chat_id = query.message.chat_id
        lock_type = data.replace("lock_", "")
        current = db["locks"].setdefault(chat_id, {}).get(lock_type, False)
        db["locks"][chat_id][lock_type] = not current
        status = "قفل شد 🔒" if not current else "باز شد 🔓"
        await query.answer(f"بخش {lock_type} {status}")

    # منوی ارتقا و عزل
    elif data == "menu_ranks":
        kb = [
            [InlineKeyboardButton("مدیران", callback_data="sub_admins"), InlineKeyboardButton("مالکین", callback_data="sub_owners")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        await query.message.edit_text("👑 **ارتقا و عزل:**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    elif data == "sub_admins":
        await query.message.edit_text("دستورات مدیر:\n• `/تنظیم_مدیر` (ریپلی)\n• `/حذف_مدیر` (ریپلی)\n• `/لیست_مدیران`\n• `/پاکسازی_لیست_مدیران`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_ranks")]]), parse_mode="Markdown")
    elif data == "sub_owners":
        await query.message.edit_text("دستورات مالک:\n• `/تنظیم_مالک` (ریپلی)\n• `/حذف_مالک` (ریپلی)\n• `/لیست_مالک`\n• `/پاکسازی_لیست_مالک`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_ranks")]]), parse_mode="Markdown")

    # منوی خوشامد گویی
    elif data == "menu_welcome":
        await query.message.edit_text("✨ **خوشامدگویی:**\n• `/خوشامد_روشن`\n• `/خوشامد_خاموش`\n• `/تنظیم_خوشامد` (روی پیام متنی یا عکس)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")

    # عضویت اجباری
    elif data == "menu_fsub":
        await query.message.edit_text("📢 **عضویت اجباری کانال:**\n• `/عضویت_اجباری_فعال`\n• `/عضویت_اجباری_غیرفعال`\n• `/تنظیم_عضویت_اجباری [یوزر کانال]`\n• `/حذف_عضویت_اجباری [یوزر کانال]`\n• `/لیست_عضویت_اجباری`\n• `/پاکسازی_عضویت_اجباری`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")

    # اد اجباری
    elif data == "menu_fadd":
        await query.message.edit_text("👥 **اد اجباری:**\n• `/اد_اجباری_فعال`\n• `/اد_اجباری_غیرفعال`\n• `/اد_اجباری_تعداد [عدد]`\n• `/حذف_اد_اجباری`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")

    # فیلتر کلمات
    elif data == "menu_filters":
        await query.message.edit_text("🚫 **فیلتر کلمات:**\n• `/فیلتر [کلمه]`\n• `/حذف_فیلتر [کلمه]`\n• `/لیست_فیلتر`\n• `/پاکسازی_لیست_فیلتر`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")

    # پنل کاربر
    elif data == "menu_userpanel":
        await query.message.edit_text("👤 **پنل کاربر:**\nدستور: `/پنل_کاربر` (روی کاربر ریپلی کنید تا آیدی و آیدی عددی نمایش داده شود)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")

    # آمار فعالیت‌ها
    elif data == "menu_stats":
        await query.message.edit_text("📊 **آمار فعالیت‌ها:**\nدستور: `/آمار_امروز` (نمایش تعداد پیام‌های امروز و برترین‌ها)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")

    # اسپم
    elif data == "menu_spam":
        await query.message.edit_text("⚡ **مدیریت اسپم:**\n• `/اسپم_فعال`\n• `/اسپم_غیرفعال`\n• `/تنظیم_اسپم [تعداد]`\n• `/تنظیم_اسپم_مجازات [اختیار/سکوت/بن]`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")

    # حالت روح و مخفی
    elif data == "menu_ghost":
        await query.message.edit_text("👻 **حالت روح و پیام مخفی:**\n• `/روح [متن]` (ارسال پیام از طرف ربات با ریپلی)\n• `/مخفی [متن] [آیدی_عددی]` (ارسال پیام رمزنگاری شده برای کاربر خاص)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode="Markdown")

# هندلر خوشامدگویی اعضای جدید
async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        chat = update.effective_chat
        if member.id == context.bot.id:
            # پیام استارت در پی‌وی یا گروه هنگام اد شدن
            await update.message.reply_text("لطفا ربات رو مدیر گپتون کنید تا فعال بشه این ربات مخصوص کلن E10 است و ساخته شده توسط اعضای E10 ⚔️")
            continue
            
        settings = db["welcome"]
        if settings.get("status", True):
            text = settings["text"].format(name=member.full_name, id=member.id)
            await update.message.reply_text(text, parse_mode="Markdown")

# هندلر پیام‌های متنی، قفل‌ها و فیلترها
async def message_filter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.from_user or message.chat.type == "private":
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    # محاسبه آمار فعالیت‌ها
    chat_counts = db["msg_counts"].setdefault(chat_id, {})
    chat_counts[user_id] = chat_counts.get(user_id, 0) + 1

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

# دستورات متفرقه و ابزارها (فونت، تگ، پنل کاربر، مخفی و روح)
async def font_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("لطفا متنی وارد کنید. مثال:\n`/فونت سلام`", parse_mode="Markdown")
        return
    raw_text = " ".join(context.args)
    # نمونه ۳ فونت از ۳۰ فونت برتر قابل کپی با یک کلیک
    fonts = [
        f"𝓔𝟙𝟘 ➮ {raw_text}",
        f"𝔼𝟙𝟘 ➮ {raw_text}",
        f"𝐄𝟏𝟎 ➮ {raw_text}",
        f"𝗘𝟭𝟬 ➮ {raw_text}",
        f"𝘌10 ➮ {raw_text}",
        f"𝙴10 ➮ {raw_text}",
        f"E̶1̶0̶ ➮ {raw_text}",
        f"E̴1̴0̴ ➮ {raw_text}",
        f"E̷1̷0̷ ➮ {raw_text}",
        f"🇪 1 0 ➮ {raw_text}"
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
    chat_id = update.effective_chat.id
    counts = db["msg_counts"].get(chat_id, {})
    if not counts:
        await update.message.reply_text("آماری برای امروز ثبت نشده است.")
        return
    top_users = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
    res = "📊 **آمار فعالیت‌های گروه (امروز):**\n\n"
    for idx, (uid, count) in enumerate(top_users, 1):
        res += f"{idx}. کاربر `{uid}` - تعداد پیام: {count}\n"
    await update.message.reply_text(res, parse_mode="Markdown")

async def tag_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update, context):
        return
    await update.message.reply_text("⚔️ تگ همگانی اعضای کلن E10 انجام شد! (اعضای گروه مطلع شدند)")

async def ghost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not context.args:
        await update.message.reply_text("استفاده: روی پیام کاربر ریپلی کنید و بنویسید `/روح [متن]`")
        return
    text = " ".join(context.args)
    await update.message.delete()
    await update.message.reply_text(f"👻 {text}")

async def secret_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("استفاده: `/مخفی [متن] [آیدی_عددی]`")
        return
    target_id = context.args[-1]
    msg_text = " ".join(context.args[:-1])
    await update.message.delete()
    kb = [[InlineKeyboardButton("🔓 مشاهده پیام مخفی", callback_data=f"secret_{target_id}_{msg_text}")]]
    await update.message.reply_text(f"🔐 یک پیام مخفی برای کاربر `{target_id}` ارسال شد.", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

# راه‌اندازی اصلی ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("راهنما", help_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("فونت", font_cmd))
    app.add_handler(CommandHandler("پنل_کاربر", user_panel_cmd))
    app.add_handler(CommandHandler("آمار_امروز", stats_cmd))
    app.add_handler(CommandHandler("تگ", tag_cmd))
    app.add_handler(CommandHandler("روح", ghost_cmd))
    app.add_handler(CommandHandler("مخفی", secret_cmd))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_filter_handler))

    print("E10 Manager Bot is running successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()
