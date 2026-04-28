from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from storage import admins, groups, terms, apis, add_admin, remove_admin, add_group, remove_group, add_term, remove_term, add_api, remove_api
import requests
import urllib3

# ✅ disable SSL warnings (Railway fix)
urllib3.disable_warnings()

TOKEN = "8724329197:AAEO8O8hpqrT5CKQf3VclpmDniVgqJ9Vw_Y"

def is_admin(user_id):
    return user_id in admins

async def send_to_groups(app, text):
    for gid in groups:
        try:
            await app.bot.send_message(chat_id=gid, text=text)
        except Exception as e:
            print("Send error:", e)

# ---------------- COMMANDS ----------------

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
/add <term>
/remove <term>
/call

/api <url>
/deleteapi <url>
/listapi

/addadmin <id>
/deleteadmin <id>

/addgroup
/deletegroup
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

# ---------------- API COMMANDS ----------------

async def add_api_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("❌ Provide API URL")
        return

    url = context.args[0]

    if not url.startswith("http"):
        await update.message.reply_text("❌ Use full https:// URL")
        return

    add_api(url)
    await update.message.reply_text(f"API added:\n{url}")

async def delete_api_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    url = context.args[0]
    remove_api(url)
    await update.message.reply_text("API removed")

async def list_api_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not apis:
        await update.message.reply_text("No APIs added")
        return

    text = "APIs:\n"
    for a in apis:
        text += f"- {a}\n"

    await update.message.reply_text(text)

# ---------------- CORE FIXED ----------------

async def run_search(app):
    if not apis:
        await send_to_groups(app, "❌ No APIs configured")
        return

    if not terms:
        await send_to_groups(app, "❌ No terms added")
        return

    for term in terms:
        for api in apis:
            try:
                print("Calling:", api, term)

                # ✅ RETRY LOGIC
                for attempt in range(3):
                    try:
                        r = requests.get(
                            api,
                            params={"term": term},
                            timeout=60,     # ✅ FIXED (was 20)
                            verify=False
                        )

                        if r.status_code != 200:
                            raise Exception(f"HTTP {r.status_code}")

                        data = r.json()
                        break

                    except Exception as e:
                        if attempt == 2:
                            raise e

                text = f"🔍 {term}\n"

                for res in data.get("results", []):
                    text += f"- {res}\n"

                await send_to_groups(app, text)

            except Exception as e:
                await send_to_groups(
                    app,
                    f"❌ Error: {term}\nAPI: {api}\n{str(e)}"
                )

# ---------------- START ----------------

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

    app.add_handler(CommandHandler("api", add_api_cmd))
    app.add_handler(CommandHandler("deleteapi", delete_api_cmd))
    app.add_handler(CommandHandler("listapi", list_api_cmd))

    return app
