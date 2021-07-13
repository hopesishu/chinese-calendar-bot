import constants as keys
from lunardate import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, replymarkup
import logging, datetime, pytz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# global variables
today = datetime.datetime.today()
day = today.day
month = today.month
year = today.year
chinese_date = LunarDate.fromSolarDate(year, month, day)

# date calculation
def date_calculation():
    gregorian_date_str = "today's Gregorian date: " + str(day) + "/" + str(month) + "/" + str(year)
    chinese_date_str = "today's Lunar date: " + str(chinese_date.day) + "/" + str(chinese_date.month) + "/" + str(chinese_date.year)
    date_reply = str(gregorian_date_str + "\n" + chinese_date_str)
    return date_reply

# next_date calculation
def next_date_calculation():
    date_list = [] # [gregorian date, lunar date]
    if (chinese_date.day >= 1 and chinese_date.day < 15):
        next_chinese_date_day = 15
        gregorian_date = LunarDate(chinese_date.year, chinese_date.month, next_chinese_date_day).toSolarDate()
        gregorian_date_datetime = datetime.datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        lunar_date_datetime = datetime.datetime(chinese_date.year, chinese_date.month, next_chinese_date_day)
        # gregorian_date_str = "next Gregorian ShiWu date: " + str(gregorian_date.day) + "/" + str(gregorian_date.month) + "/" + str(gregorian_date.year)
        # chinese_date_str = "next Lunar ShiWu date: " + str(next_chinese_date_day) + "/" + str(chinese_date.month) + "/" + str(chinese_date.year)
        # next_date_reply = str(gregorian_date_str + "\n" + chinese_date_str)
        # return next_date_reply
    else:
        next_chinese_date_day = 1
        next_chinese_date_month = chinese_date.month + 1
        gregorian_date = LunarDate(chinese_date.year, next_chinese_date_month, next_chinese_date_day).toSolarDate()
        gregorian_date_datetime = datetime.datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        lunar_date_datetime = datetime.datetime(chinese_date.year, next_chinese_date_month, next_chinese_date_day)
    date_list.append(gregorian_date_datetime)
    date_list.append(lunar_date_datetime)
    return date_list
        # gregorian_date_str = "next Gregorian ChuYi date: " + str(gregorian_date.day) + "/" + str(gregorian_date.month) + "/" + str(gregorian_date.year)
        # chinese_date_str = "next Lunar ChuYi date: " + str(next_chinese_date_day) + "/" + str(next_chinese_date_month) + "/" + str(chinese_date.year)
        # next_date_reply = str(gregorian_date_str + "\n" + chinese_date_str)
        # return next_date_reply

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="hello! thank you for using this bot")
    context.bot.send_message(chat_id=update.effective_chat.id, text="here are some actions that you can carry out to get started: \n 1. /notify - you can opt for this bot to remind you when the next day is ChuYi/ShiWu \n 2. /options - tells you what is today's Lunar Date or the next ChuYi/ShiWu")

def notify(update, context):
    # on ChuYi/ShiWu, send notification 
    notify_date = next_date_calculation()
    gregorian_notify_date = notify_date[0]

    context.bot.send_message(chat_id=update.effective_chat.id, text="you have successfully enabled notifications! \nyou will now receive notifications on the next ChuYi/ShiWu at 8am to remind you to be vegetarian :-)")
    morning = pytz.timezone('Asia/Singapore').localize(datetime.datetime(year=gregorian_notify_date.year, month=gregorian_notify_date.month, day=gregorian_notify_date.day, hour=8))
    context.job_queue.run_once(msg, when=morning, context=update.message.chat_id)
    # context.job_queue.run_daily(msg,
    #                             datetime.time(hour=16, minute=56, tzinfo=pytz.timezone('Asia/Singapore')),
    #                             days=(0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id)

def msg(context):
    context.bot.send_message(chat_id=context.job.context, text='remember to eat vegetarian today!')

def keyboard_options():
    """Sends a message with two inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("today eat vege?", callback_data='date')
        ],
        [
            InlineKeyboardButton("when eat vege?", callback_data='next_date')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def options(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="what do you wish to find out?", reply_markup=keyboard_options())
    # update.message.reply_text('Please choose:', reply_markup=keyboard_options())

def keyboard_button(update, context):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    choice = query.data
    if (choice == "date"):
        date_list = date_calculation()
        gregorian_date = date_list[0]
        lunar_date = date_list[1]
        gregorian_date_str = "today's Gregorian date: " + str(day) + "/" + str(month) + "/" + str(year)
        lunar_date_str = "today's Lunar date: " + str(chinese_date.day) + "/" + str(chinese_date.month) + "/" + str(chinese_date.year)
        reply = str(gregorian_date_str + "\n" + lunar_date_str)

        context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
    elif (choice == "next_date"):
        date_list = next_date_calculation()
        gregorian_date = date_list[0]
        lunar_date = date_list[1]
        if (lunar_date.day == 1):
            chu = "ChuYi"
        
        elif (lunar_date.day == 15): 
            chu = "ShiWu"

        gregorian_date_str = "next Gregorian " + chu + " date: " + str(gregorian_date.day) + "/" + str(gregorian_date.month) + "/" + str(gregorian_date.year)
        lunar_date_str = "next Lunar " + chu + " date: " + str(lunar_date.day) + "/" + str(lunar_date.month) + "/" + str(lunar_date.year)
        reply = str(gregorian_date_str + "\n" + lunar_date_str)

        context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
    # query.edit_message_text(text=f"Selected option: {query.data}")
    # options(update, context)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("notify", notify, pass_job_queue=True))
    dp.add_handler(CommandHandler("options", options))
    dp.add_handler(CallbackQueryHandler(keyboard_button))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), start))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()