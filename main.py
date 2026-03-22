import os
import random
import string
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

# -------- LOGGING -------- #
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# -------- TOKEN -------- #
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables!")

# -------- PASSWORD GENERATOR -------- #
def generate_password(length=12):
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()"

    # Ensure strong password (at least one of each)
    password = [
        random.choice(lower),
        random.choice(upper),
        random.choice(digits),
        random.choice(symbols),
    ]

    all_chars = lower + upper + digits + symbols
    password += random.choices(all_chars, k=max(0, length - 4))

    random.shuffle(password)
    return ''.join(password)


# -------- STRENGTH CHECK -------- #
def check_strength(password):
    score = 0

    if len(password) >= 8:
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()" for c in password):
        score += 1

    if score <= 2:
        return "Weak 😟"
    elif score <= 4:
        return "Medium ⚠️"
    else:
        return "Strong 💪"


# -------- /start -------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 *Password Generator Bot*\n\n"
        "Commands:\n"
        "/password 12 → Generate password\n"
        "/password 16 → Stronger password\n\n"
        "Example:\n"
        "`/password 14`",
        parse_mode="Markdown"
    )


# -------- /password -------- #
async def password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        length = int(context.args[0])
        if length < 6:
            length = 6
    except:
        length = 12

    pwd = generate_password(length)
    strength = check_strength(pwd)

    keyboard = [
        [InlineKeyboardButton("🔁 Regenerate", callback_data=f"regen_{length}")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🔐 *Password:*\n`{pwd}`\n\n*Strength:* {strength}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# -------- BUTTON HANDLER -------- #
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("regen_"):
        length = int(data.split("_")[1])

        pwd = generate_password(length)
        strength = check_strength(pwd)

        keyboard = [
            [InlineKeyboardButton("🔁 Regenerate", callback_data=f"regen_{length}")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🔐 *Password:*\n`{pwd}`\n\n*Strength:* {strength}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


# -------- MAIN -------- #
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("password", password))
    app.add_handler(CallbackQueryHandler(button))

    print("🚀 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
