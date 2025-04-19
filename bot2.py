from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from flask import Flask
from threading import Thread

# Replace with your actual bot token from BotFather
API_TOKEN = "7616920513:AAGnhctwnm_EjXjkXn_VMiDqFj8yMA65u1Y"

# Flask Web Server
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Dictionary to track user states
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Kusoo dhawow Xafiiska Hanti-dhawrka guud ee SSC-Khaatumo!"
    )
    await show_option_buttons(update, context)

async def show_option_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Taabo 1 si aad farriin u qorto", callback_data='text_message')],
        [InlineKeyboardButton("Taabo 2 si aad cod u duubto", callback_data='voice_recording')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_message.reply_text('Fadlan dooro mid ka mid ah:', reply_markup=reply_markup)

async def button_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    selection = query.data
    user_id = query.from_user.id

    if selection == 'voice_recording':
        user_states[user_id] = 'awaiting_voice'
        await query.edit_message_text('Fadlan dir codkaaga (voice message).')
    elif selection == 'text_message':
        user_states[user_id] = 'awaiting_text'
        await query.edit_message_text('Fadlan qor fariintaada (text message).')

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_states.get(user_id) == 'awaiting_voice':
        voice = update.message.voice
        file_id = voice.file_id
        await update.message.reply_text('Codkaaga waa la helay. Waad ku mahadsan tahay!')
        user_states[user_id] = None
    else:
        await update.message.reply_text('Fadlan dooro "Taabo 2 si aad cod u duubto" si aad cod u dirto.')

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_states.get(user_id) == 'awaiting_text':
        text = update.message.text
        await update.message.reply_text(f'Fariintaada waa la helay: "{text}"')
        user_states[user_id] = None
    else:
        await update.message.reply_text('Fadlan dooro "Taabo 1 si aad farriin u qorto" si aad fariin u dirto.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        'Waxaan kuu qaban karaa amarada soo socda:\n'
        '/start - Bilaabida bot-ka\n'
        '/help - Hel caawimo'
    )

def main():
    keep_alive()  # Start Flask server to keep alive with UptimeRobot

    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(button_selection_handler, pattern='^(voice_recording|text_message)$'))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    application.run_polling()

if __name__ == '__main__':
    main()
