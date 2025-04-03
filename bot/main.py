from article_list import first_page, handle_pagination
import article_list
from miniflux_client import get_started, mark_read, init_miniflux

import logging
import os
import dotenv
from telegram import Update, User
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler

COMMANDS = [
    ("start", "Get the strrated articles"),
    ("mark_read", "Mark an article as readed and unstarred"),
]

dotenv.load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def block_strangers(user: User, update: Update) -> bool:
    if "TG_USERNAME" not in os.environ or os.environ["TG_USERNAME"] == "":
        return False
    if user.username != os.environ["TG_USERNAME"]:
        await update.message.reply_text("You are not allowed to use this bot")
        return True
    return False

def block_strangers_wapper(func):
    async def wrapper(update: Update, context: CallbackContext):
        if await block_strangers(update.message.from_user, update):
            return
        return await func(update, context)
    return wrapper

@block_strangers_wapper
async def start(update: Update, context: CallbackContext) -> None:
    # Update article list
    article_list.ALIST = get_started()
    await first_page(update, context)

@block_strangers_wapper
async def mark_readed(update: Update, context: CallbackContext) -> None:
    try:
        article = article_list.ALIST[int(context.args[0])]
        await update.message.reply_text(f"Marking {article.title} (ID: {article.id}) as readed and unstarred")
        if mark_read(article):
            await update.message.reply_text("Done")
        else:
            await update.message.reply_text("Failed")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    init_miniflux()
    article_list.ALIST = get_started()

    application = ApplicationBuilder().token(os.environ["TG_TOKEN"]).build()

    start_handler = CommandHandler('start', start)
    mark_read_handler = CommandHandler('mark_read', mark_readed, has_args=1)
    application.add_handler(CallbackQueryHandler(handle_pagination))
    application.add_handler(start_handler)
    application.add_handler(mark_read_handler)

    application.run_polling()