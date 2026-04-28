from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from storage import admins, groups, terms, add_admin, remove_admin, add_group, remove_group, add_term, remove_term
import requests

API_URL = "https://your-api.up.railway.app/search"

TOKEN = "8724329197:AAEO8O8hpqrT5CKQf3VclpmDniVgqJ9Vw_Y"

# ---------- Helpers ----------
def is_admin(user_id):
    return user_id in admins

async def send_to_groups(app, text):
    for gid in groups:
        try:
            await app.bot.send_message(chat_id=gid, text=text)
        except:
            pass

# ---------- Commands ----------

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
/add <term> - add search term
/remove <term> - remove term
/call - force call now
/addadmin <id>
/deleteadmin <id>
/addgroup - set this group
/deletegroup - remove this group
/help - show commands
"""
    await update.message.reply_text(text)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    term = " ".join(context.args)
    add_term(term)
    await update.message.reply_text(f"Added: {term}")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    term = " ".join(context.args)
    remove_term(term)
    await update.message.reply_text(f"Removed: {term}")

async def call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await run_search(context.application)

async def addadmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    add_admin(int(context.args[0]))
    await update.message.reply_text("Admin added")

async def deladmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    remove_admin(int(context.args[0]))
    await update.message.reply_text("Admin removed")

async def addgroup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    add_group(update.effective_chat.id)
    await update.message.reply_text("Group added")

async def delgroup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    remove_group(update.effective_chat.id)
    await update.message.reply_text("Group removed")

# ---------- Core logic ----------

async def run_search(app):
    for term in terms:
        try:
            r = requests.get(API_URL, params={"term": term}, timeout=20)
            data = r.json()

            text = f"🔍 {term}\n"

            for r in data["results"]:
                text += f"- {r}\n"

            await send_to_groups(app, text)

        except Exception as e:
            await send_to_groups(app, f"Error for {term}")

# ---------- Start bot ----------

def start_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("call", call))
    app.add_handler(CommandHandler("addadmin", addadmin_cmd))
    app.add_handler(CommandHandler("deleteadmin", deladmin_cmd))
    app.add_handler(CommandHandler("addgroup", addgroup_cmd))
    app.add_handler(CommandHandler("deletegroup", delgroup_cmd))

    return app
