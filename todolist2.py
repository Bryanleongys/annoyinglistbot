from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton, Message, Bot, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
import MySQLdb, sys

# creating database
sqlID = 'root'
sqlPASSWORD = 'Biryani158*'
URI = 'mysql://' + sqlID + ':' + sqlPASSWORD + '@localhost/todolist'
engine = create_engine(URI, echo = True)
Base = declarative_base()

task_id = 0

class User(Base):
    __tablename__ = 'Losers'
    task_id = Column(Integer, primary_key = True)
    username = Column(Integer)
    date = Column(String)
    time = Column(String)
    event_name = Column(String)

Base.metadata.create_all(engine)

#starting session
Session = sessionmaker(bind = engine)
session = Session()

# Keyboard Buttons
def main_options_keyboard():
    keyboard = [
        [InlineKeyboardButton("Add Task", callback_data='add_task')],
        [InlineKeyboardButton("Delete Task", callback_data='delete_task')]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start function
SHOW_KEYBOARD, PROMPT_DATE, PROMPT_TIME, END_ADD_TASK, END_DELETE_TASK, RETURN_INITIAL= range(6)
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

    text = "Use these functions to get your life together :)"
    
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

    global user_date
    user_date = user_input

    context.bot.send_message(
        chat_id=chat_id,
        text="What time of the day do you need to complete this by? (e.g. 0930)"
    )

    return END_ADD_TASK

def end_add_task(update, context):
    chat_id=update.message.chat.id
    user_input=update.message.text.replace(" ", "")
    global username
    username = update.message.from_user.username
    
    if not (user_input.isdigit() and len(user_input) == 4):
        context.bot.edit_message_text(
            chat_id=chat_id,
            text="What are you doing dummy? Input in this format: 0930"
        )

        return END_ADD_TASK

    user_time = user_input

    global task_id
    task_id = task_id + 1

    user = User(task_id = task_id, username = username, date = user_date, time = user_time, event_name = user_event_name)
    session.add(user)
    session.commit()
 
    context.bot.send_message(
        chat_id=chat_id,
        text="Your event has been added."
    )

    text="What are you waiting for? Complete these tasks! \n\n"

    user = session.query(User).get(username)
    connection = MySQLdb.connect (host = "localhost", user = "root", passwd = "Biryani158*", db = "todolist")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Losers;')
    data = cursor.fetchall()
    for row in data:
        if (username == row[1]):
            text += "Task No: " + str(row[0]) + "  Date: " + row[2] + "  Time: " + row[3] + "  Task: " + row[4] + "\n\n"

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=main_options_keyboard()
    )

    return ConversationHandler.END

# Delete Task function
def prompt_task_id(update, context):
    query=update.callback_query

    text = ""
    connection = MySQLdb.connect (host = "localhost", user = "root", passwd = "Biryani158*", db = "todolist")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Losers;')
    data = cursor.fetchall()
    for row in data:
        if (username == row[1]):
            text += "Task No: " + str(row[0]) + "  Date: " + row[2] + "  Time: " + row[3] + "  Task: " + row[4] + "\n\n"

    text += "Enter the task number you want to delete lazy ass."

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text
    )

    return END_DELETE_TASK

def end_delete_task(update, context):
    chat_id=update.message.chat.id
    username=update.message.from_user.username
    user_input=update.message.text

    connection = MySQLdb.connect (host = "localhost", user = "root", passwd = "Biryani158*", db = "todolist")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Losers;')
    data = cursor.fetchall()
    for row in data:
        if (str(row[0]) == user_input):
            if (username != str(row[1])):
                context.bot.send_message(
                    chat_id=chat_id,
                    text='What are you doing dummy? Delete your own tasks!'
                )
                return_initial(update, context)
                return

            else:
                # cursor.execute('DELETE FROM Losers WHERE task_id=' + user_input + '&& username=' + username +';')
                x = session.query(User).get(row[0])
                session.delete(x)
                session.commit()
                context.bot.send_message(
                    chat_id=chat_id,
                    text='Task no ' + user_input + ' has been deleted.'
                )

                text="What are you waiting for? Complete these tasks! \n\n"
                connection = MySQLdb.connect (host = "localhost", user = "root", passwd = "Biryani158*", db = "todolist")
                cursor = connection.cursor()
                cursor.execute('SELECT * FROM Losers;')
                data = cursor.fetchall()
                for row in data:
                    if (username == row[1]):
                        text += "Task No: " + str(row[0]) + "  Date: " + row[2] + "  Time: " + row[3] + "  Task: " + row[4] + "\n\n"

                context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=main_options_keyboard()
                )
                return ConversationHandler.END

    context.bot.send_message(
        chat_id=chat_id,
        text='What are you doing dummy? Delete your own tasks!'
        )
    return_initial(update, context)

def return_initial(update, context):
    chat_id=update.message.chat.id

    text="What are you waiting for? Complete these tasks! \n\n"

    connection = MySQLdb.connect (host = "localhost", user = "root", passwd = "Biryani158*", db = "todolist")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Losers;')
    data = cursor.fetchall()
    for row in data:
        if (username == row[1]):
            text += "Task No: " + str(row[0]) + "  Date: " + row[2] + "  Time: " + row[3] + "  Task: " + row[4] + "\n\n"

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

    dp.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(prompt_task_id, pattern='delete_task')],
            states={
                END_DELETE_TASK: [MessageHandler(Filters.text, end_delete_task)],
                RETURN_INITIAL: [MessageHandler(Filters.text, return_initial)]
            },
            fallbacks=[],
            per_user=False
        )
    )

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()


