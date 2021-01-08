from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton, Message, Bot, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship

# creating database
sqlID = ''
sqlPASSWORD = ''
URI = 'mysql://' + sqlID + ':' + sqlPASSWORD + '@localhost/todolist'
engine = create_engine(URI, echo = True)
Base = declarative_base()

class Tasks(Base):
    __tablename__ = "tasks"

    username=Column(String(100), ForeignKey('username'), primary_key=True)
    username_id=Column()
    day = Column(Integer)
    time = Column(Integer)
    event_name = Column(String(100))

    def __init__(self, username, day, time, event_name):
        self.username = username
        self.day = day
        self.time = time
        self.event_name = event_name

class Users(Base):  
    __tablename__ = 'users'
    username = Column(String(100),primary_key=True)

    def __init__(self, username, tasks):
        self.username = username

    tasks = relationship("Tasks", back_populates="users")

Tasks.user = relationship(
    "Users", order_by=Users.username, back_populates="tasks"
)

Base.metadata.create_all(engine)

# starting session
Session = sessionmaker(bind = engine)
session = Session()

# Keyboard Buttons
def main_options_keyboard():
    keyboard = [
        [InlineKeyboardButton("Add Task", callback_data='add_task')],
        [InlineKeyboardButton("Delete Task", callback_data='delete_task'), InlineKeyboardButton("Complete Task", callback_data='complete_task')],
        [InlineKeyboardButton("Edit Prompt Time", callback_data='edit_time')],
        [InlineKeyboardButton("View Completed Tasks", callback_data='completed_tasks')]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start function
SHOW_KEYBOARD, PROMPT_DATE, PROMPT_TIME, END_ADD_TASK = range(4)
def start(update, context):
    chat_id=update.message.chat.id
    global username
    username=update.message.from_user.username

    text = "Welcome to the most annoying bot of your life, @" + username + ". First, may I know when you want to be annoyed? (e.g. 0930)"
    context.bot.send_message(
        chat_id=chat_id,
        text=text
    )
    return SHOW_KEYBOARD

def keyboard_buttons(update, context):
    chat_id=update.message.chat.id
    user_input=update.message.text

    if not (user_input.isdigit() and len(user_input) == 4):
        context.bot.send_message(
            chat_id=chat_id,
            text="What are you doing dummy? Input in this format: 0930"
        )

        return SHOW_KEYBOARD

    text = "What are you waiting for? Complete these tasks! \n---------TASKS TO COMPLETE----------"
    # give the list of tasks on SQL table
    update.message.reply_text(
        text=text,
        reply_markup=main_options_keyboard()
    )

    return ConversationHandler.END

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
    user_input=update.message.text

    global user_event_name
    user_event_name = user_input

    context.bot.send_message(
        chat_id=chat_id,
        text='When do you need to complete this task by? (e.g. YYMMDD)'
    )

    return PROMPT_TIME

def prompt_time(update, context):
    chat_id=update.message.chat.id
    user_input=update.message.text.replace(" ", "")

    if not (user_input.isdigit() and len(user_input) == 6):
        context.bot.send_message(
            chat_id=chat_id,
            text="What are you doing dummy? Input in this format: YYMMDD"
        )

        return PROMPT_TIME

    global user_day
    user_day = user_input

    context.bot.send_message(
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

    global user_time
    user_time = user_input

    task = Tasks(username=username, day=user_day, time=user_time, event_name=user_event_name)
    user = Users(username=username, tasks=task)

    session.add(user)
    session.add(task)
    session.commit()

    context.bot.send_message(
        chat_id=chat_id,
        text="Your event has been added."
    )

    text="What are you waiting for? Complete these tasks! \n -----TASKS TO COMPLETE-------"
    #give list of tasks on SQL

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=main_options_keyboard()
    )

    return ConversationHandler.END

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
                END_ADD_TASK: [MessageHandler(Filters.text, end_add_task)]
            },
            fallbacks=[],
            per_user=False
        )
    )

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()


