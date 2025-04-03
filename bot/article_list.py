from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from miniflux_client import articleType
from telegram.constants import ParseMode

ITEMS_PER_PAGE = 10

ALIST: list[articleType] = []

def get_page_content(page: int) -> str:
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    page_items = ALIST[start_index:end_index]
    page_items = [f"<strong>{start_index + i}.Title</strong>: {item.title} \n Source: {item.source} \n Publish time: {item.publish_time} \n URL: {item.url}"
                  + (f"\n Comment URL: {item.comment}" if item.comment else "")
                  + (f"\n Tags: {', '.join(item.tags)}" if item.tags else "")
                  + "\n"
                  for i, item in enumerate(page_items)]
    return "\n".join(page_items)

def build_pagination_keyboard(page: int) -> tuple[InlineKeyboardMarkup, int]:
    keyboard = []
    total_pages = (len(ALIST) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    if page > 1:
        keyboard.append(InlineKeyboardButton("Previous", callback_data=f'page_{page - 1}'))
    if page < total_pages:
        keyboard.append(InlineKeyboardButton("Next", callback_data=f'page_{page + 1}'))
    return InlineKeyboardMarkup([keyboard]), total_pages

async def handle_pagination(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if not query.data.startswith('page_'):
        return

    target_page = int(query.data.split('_')[1])
    total_pages = (len(ALIST) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    message = get_page_content(target_page)
    keyboard, _ = build_pagination_keyboard(target_page)

    print("Updating message")

    await query.edit_message_text(
        f"Page {target_page} ({total_pages} in total): \n{message}",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

async def first_page(update: Update, context: CallbackContext) -> None:
    current_page = 1
    message = get_page_content(current_page)
    keyboard, total_pages = build_pagination_keyboard(current_page)

    await update.message.reply_text(
        f"Page {current_page} ({total_pages} in total): \n{message}",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )