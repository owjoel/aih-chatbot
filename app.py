import os as os
import chatbot
import storage

from io import BytesIO
from dotenv import load_dotenv
from telegram import Update, File, constants, User
from telegram.ext import ApplicationBuilder, Application, CommandHandler, ContextTypes, MessageHandler, filters


# Config
load_dotenv()
BOT_TOKEN = os.environ.get('TELEGRAM_ACCESS_TOKEN')
BOT_USERNAME = os.environ.get('TELEGRAM_BOT_USERNAME')
# APP_URL = os.environ.get('GOOGLE_APP_ENGINE_URL')


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    thread_id = chatbot.create_thread()
    storage.set_user(username=user.username, thread_id=thread_id)
    print(thread_id)
    await update.message.reply_text(f"Hey {user.first_name}! Let's connect with nature today🌲")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is the help command')

# Responses
def handle_response(thread_id: str, user: str, content: str) -> str:
    return chatbot.message_locator(thread_id=thread_id, user=user, content=content)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
    message_type: str = update.message.chat.type
    text: str = update.message.text
    user: User = update.message.from_user

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    auth: str = storage.get_user(user.username)
    if not auth:
        await update.message.reply_text("Use the /start command to chat with me!")
        return
    print(auth)
    response: str = handle_response(thread_id=auth.get('thread_id'), user=user, content=text)
    await update.message.reply_text(response, parse_mode='Markdown')

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: User = update.message.from_user
    auth: str = storage.get_user(user.username)
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
    print(f'User ({update.message.chat.id}): "{caption}"')
    image: File = await context.bot.get_file(file_id)
    path: str = os.path.join('tmp', os.path.basename(image.file_path))
    image_path = await image.download_to_drive(path)
    with open(image_path, 'rb') as image_rb:
        response: str = chatbot.message_journaller(thread_id=auth.get('thread_id'), user=user.first_name, image=image_rb, caption=caption)
    os.remove(path)
    await update.message.reply_text(response, parse_mode='Markdown')



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

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, handle_image))

    # Errors
    app.add_error_handler(error)
    app.run_polling(poll_interval=2, drop_pending_updates=True)

    # FUCK THIS SHIT
    # print(APP_URL)
    # app.run_webhook(
    #     listen='0.0.0.0',
    #     port='80',
    #     webhook_url="https://04ee-39-109-176-16.ngrok-free.app"
    # )