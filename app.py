import os as os
import chatbot
import storage

from dotenv import load_dotenv
from telegram import Update, File, constants, User, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from messages import help_text

# Config
load_dotenv()
BOT_TOKEN = os.environ.get('TELEGRAM_ACCESS_TOKEN')
BOT_USERNAME = os.environ.get('TELEGRAM_BOT_USERNAME')
# APP_URL = os.environ.get('GOOGLE_APP_ENGINE_URL')


def get_intro(username: str):
    return f'''Hey {username}! I'm Thabo 🦛, Singapore's 2 year old 'Moo Deng'. I'm a pygmy hippo, and I'm here to help you find nature spots nearby or guide you through journaling to reflect on your experiences with nature!🌲

Use /settings to set some preferences, so I can tailor my chat with you, or /help to find more about what I can do!    
'''


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: User = update.message.from_user
    thread_id: str = chatbot.create_thread()
    storage.set_user(username=user.username, thread_id=thread_id)
    print(f"User ({user.username}) started new thread: {thread_id}\n")
    await update.message.reply_text(get_intro(user.first_name))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_text, parse_mode='MarkdownV2')


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("Exploring as a...", callback_data="demographic")],
        [InlineKeyboardButton("Choose your vibe", callback_data="vibe")],
    ]
    reply_markup = InlineKeyboardMarkup(kb)
    await update.message.reply_text("Choose a setting to configure!", reply_markup=reply_markup)

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("<a href='https://docs.google.com/forms/d/e/1FAIpQLSeg0eqmFfeVPPzxxdY_oFLUXs0UrI3-FdmsHwnBnIStSz4ybw/viewform?usp=sf_link'>Give us feedback!</a>", parse_mode='HTML')

# Responses
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
    message_type: str = update.message.chat.type
    text: str = update.message.text
    user: User = update.message.from_user

    print(f'User ({user.username}) in {message_type}: "{text}"')
    auth: str = storage.get_user(user.username)
    if not auth:
        await update.message.reply_text("Use the /start command to chat with me!")
        return
    response: str = chatbot.message_locator(thread_id=auth.get('thread_id'), user=user.first_name, demo=auth.get('demo'), vibe=auth.get('vibe'), content=text)
    await update.message.reply_text(response, parse_mode='Markdown')


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: User = update.message.from_user
    auth = storage.get_user(user.username)
    if not auth:
        await update.message.reply_text("Use the /start command to chat with me!")
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
    photo_sizes = update.message.photo
    file_id: str = None
    for size in photo_sizes:
        if size.width <= 640 and size.height <= 640:
            file_id = size.file_id
    if not file_id:
        file_id = photo_sizes[-1].file_id

    caption: str = update.message.caption
    print(f'User ({user.username}): "{caption}"')
    image: File = await context.bot.get_file(file_id)
    path: str = os.path.join('tmp', os.path.basename(image.file_path))
    image_path = await image.download_to_drive(path)
    with open(image_path, 'rb') as image_rb:
        response: str = chatbot.message_journaller(thread_id=auth.get('thread_id'), user=user.first_name, demo=auth.get('demo'), vibe=auth.get('vibe'), image=image_rb, caption=caption)
    os.remove(path)
    await update.message.reply_text(response, parse_mode='Markdown')



# Preferences Settings
async def preferences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    username = query.from_user.username
    await query.answer()  # Acknowledge the callback
    help_text: str = "Ask me for any nature recommendations and I'll cater it to your preference! 😇"

    # If "Next Options" was clicked, show new buttons
    if query.data == 'demographic':
        keyboard = [
            [InlineKeyboardButton("Mama/Papa Hippo", callback_data='parent')],
            [InlineKeyboardButton("Free Spirit", callback_data='solo')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Exploring as a...", reply_markup=reply_markup)

    elif query.data == 'vibe':
        keyboard = [
            [InlineKeyboardButton("Adventurous", callback_data='adventurous')],
            [InlineKeyboardButton("Chill", callback_data='chill')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Exploring as a...", reply_markup=reply_markup)
    
    elif query.data == 'parent' or query.data == 'solo':
        print(f"Updated ({username})'s demographic to {query.data}\n")
        storage.update_demographic(username=username, demo=query.data)
        await query.edit_message_text(text=f"Got it! Let's go hippo friend! {help_text}")

    elif query.data == 'adventurous' or query.data == 'chill': 
        print(f"Updated ({username})'s vibe to {query.data}\n")
        storage.update_vibe(username=username, vibe=query.data)
        await query.edit_message_text(text=f"Alright! There are many {query.data} activities for you to connect with nature! {help_text}")


# Errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update.update_id} caused error "{context.error}"')

# Entrypoint
if __name__ == '__main__':
    print('Starting bot...')
    chatbot.openai_init()
    chatbot.delete_files()
    app: Application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('settings', settings_command))
    app.add_handler(CommandHandler('feedback', feedback_command))
    app.add_handler(CallbackQueryHandler(preferences))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, handle_image))

    # Errors
    app.add_error_handler(error)
    app.run_polling(poll_interval=2, drop_pending_updates=True)