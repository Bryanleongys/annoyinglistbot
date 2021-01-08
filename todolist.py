from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton, Message, Bot, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext

# Keyboard Buttons
def main_options_keyboard():
    keyboard = [
        [InlineKeyboardButton("Add Task", callback_data='add_task')],
        [InlineKeyboardButton("Delete Task", callback_data='delete_task')],
        [InlineKeyboardButton("Edit Prompt Time", callback_data='edit_time')]
        [InlineKeyboardButton("View Completed Tasks", callback_data='completed_tasks')]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start function
SHOW_KEYBOARD, PROMPT_DATE, PROMPT_TIME, END_ADD_TASK = range(3)
def start(update, context):
    chat_id=update.message.chat.id
    username=update.message.from_user.username

    text = "Welcome to the most annoying bot of your life, @" + username + ". First, may I know when you want to be annoyed?"
    context.bot.send_message(
        chat_id=chat_id,
        text=text
    )
    return SHOW_KEYBOARD

def keyboard_buttons(update, context):
    chat_id=update.message.chat.id

    text = "What are you waiting for? Complete these tasks!"
    update.message.reply_text(
        text=text,
        reply_markup=main_options_keyboard()
    )

# Add Task function
def prompt_event(update, context):
    query=update.callback_query

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = 'What task do you need to do?'
    )
    return PROMPT_DATE

def prompt_date(update, context):
    chat_id=update.message.chat.id
    user_input = update.message.text

    #input data into SQL here!

    context.bot.edit_message_text(
        chat_id=chat_id,
        text='When do you need to complete this task by? (e.g. YY/MM/DD)'
    )

    return PROMPT_TIME

def prompt_time(update, context):
    chat_id=update.message.chat.id
    user_input=update.message.text.replace(" ", "")

    if not (user_input.isdigit() and len(user_input) == 6):
        context.bot.edit_message_text(
            chat_id=chat_id,
            text="What are you doing dummy? Input in this format: YY/MM/DD"
        )

        return PROMPT_TIME

    #input data into SQL here!
    context.bot.edit_message_text(
        chat_id=chat_id,
        text="What time of the day do you need to complete this by? (e.g. 0930)"
    )

    return END_ADD_TASK

def end_add_task(update, context):
    chat_id=update.message.chat.id
    user_input=update.message.text.replace(" ", "")
    
    if not (user_input.isdigit() and len(user_input) == 4):
        context.bot.edit_message_text(
            chat_id=chat_id,
            text="What are you doing dummy? Input in this format: 0930"
        )

        return END_ADD_TASK

    context.bot.edit_message_text(
        chat_id=chat_id,
        text="Your event has been added. Following are the events you have to complete: ",
        reply_markup=main_options_keyboard()
    )

BOT_TOKEN = "1556459123:AAFwqwpHyZIgBdRF1gicdMVCpHq8Tjd5_cQ"
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # put your handlers here
    #/start function
    dp.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                SHOW_KEYBOARD: [MessageHandler(Filters.text, keyboard_buttons)]
            },
            fallbacks=[],
            per_user=False
        )
    )

    dp.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(prompt_event, pattern='add_task')],
            states={
                PROMPT_DATE: [MessageHandler(Filters.text, prompt_date)],
                PROMPT_TIME: [MessageHandler(Filters.text, prompt_time)],
                

            }
        )
    )
    

