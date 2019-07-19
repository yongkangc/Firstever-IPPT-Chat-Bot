import telegram
from telegram import InlineKeyboardButton, ChatAction, InlineKeyboardMarkup, InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, InlineQueryHandler, \
    ConversationHandler, RegexHandler
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)


import logging
import re
from functools import wraps
import math
import os


from ippt_data import *
from calculateippt import *
from generateworkout import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = '898265418:AAFhUSkBIocJ5XDtvpmwy7_TJSbOZWFatCo'
#TOKEN = os.getenv("TOKEN")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func


@send_typing_action
def start(update, context):
    """ /start command for the 2 user options """

    keyboard = [[InlineKeyboardButton("Calculate IPPT Score", callback_data='Calculate IPPT Score'),
                 InlineKeyboardButton("Generate Workout", callback_data='Generate Workout')],
                ]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Hi! I am the IPPT Bot! I am to help you with your IPPT 💪\n'
                              'Send /cancel to stop talking to me.\n\n'
                              'How can i help? 😊', reply_markup=reply_markup)

    return CHOICE


def facts_to_str(user_data):
    """Converts Dict value into Text message"""

    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


@send_typing_action
def non_command_reply(update, context):
    update.message.reply_text('Hey bro, here\'s how i can help :\n\n'
                              'Send /calculate - calculate your IPPT Score\n'
                              'Send /workout - generates your workout\n'
                              'or Send /start to choose!👍')


@send_typing_action
def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye {}! Type anything to chat with me again :)'.format(user.first_name),
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    logger.info("Starting bot")

    #setting config for deployment
    # Port is given by Heroku
    # PORT = os.environ.get('PORT')
    # HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")

    updater = Updater(TOKEN,use_context=True)
    dp = updater.dispatcher

    # conversation handler
    conv_handler_calculate = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('calculate', calculate)],
        states={
            CHOICE: [MessageHandler(Filters.regex('^Calculate IPPT Score$'), choice),
                     MessageHandler(Filters.regex('^Generate Workout$'), workout)],
            AGE: [MessageHandler(Filters.text, age, pass_user_data=True)],
            PUSHUPS: [MessageHandler(Filters.text, pushupcount, pass_user_data=True)],
            SITUPS: [MessageHandler(Filters.text, situpcounts, pass_user_data=True)],
            RUNTIME: [MessageHandler(Filters.text, run_time, pass_user_data=True)],
            EDIT: [MessageHandler(Filters.regex('^(Age|Pushups|Situps|Run Time)$'),
                                  regular_choice,
                                  pass_user_data=True),
                   MessageHandler(Filters.regex('^(Done)$'), calculate_score_grade, pass_user_data=True)],
            RECEIVED_INFORMATION: [MessageHandler(Filters.text, received_information, pass_user_data=True)]
            # LOCATION: [MessageHandler(Filters.location, location),
            #            CommandHandler('skip', skip_location)],
            #
            # BIO: [MessageHandler(Filters.text, bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    #Conv handler for generate workout feature
    conv_handler_workout = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('workout', workout),CommandHandler('pushup',pushup_score_workout)],
        states={
            CHOICE: [MessageHandler(Filters.regex('^Calculate IPPT Score$'), choice),
                     MessageHandler(Filters.regex('^Generate Workout$'), workout)],
            TARGET: [MessageHandler(Filters.regex('^IPPT Workout$'),target),
                     MessageHandler(Filters.regex('^General Workout$'),nontarget)],


            IPPTWORKOUT: [MessageHandler(Filters.regex('^(Pushup)$'),pushup_score_workout)
                        ,MessageHandler(Filters.regex('^Situp$'),situp_workout_score)
                          ,MessageHandler(Filters.regex('^(Running|Overall)$'),running_workout)],

            SITUP_SCORE: [MessageHandler(Filters.text, situp_workout)],

            PUSHUP_SCORE: [MessageHandler(Filters.regex('^(Less than 40|More than 40)$'),pushup_workout)],

            NONTARGET:[MessageHandler(Filters.regex('^Weight Circuit Training$'), weight_circuit),
                     MessageHandler(Filters.regex('^Calistenics Circuit Training$'), cali_circuit),
                       MessageHandler(Filters.regex('^Core$'), core),
                       MessageHandler(Filters.regex('^Swimming$'), swimming),
                       MessageHandler(Filters.regex('^Random$'),random_workout)

                       ]
        },
        fallbacks= [CommandHandler('cancel',cancel)]
    )

    dp.add_handler(conv_handler_workout)
    dp.add_handler(conv_handler_calculate)
    dp.add_handler(MessageHandler(Filters.text, non_command_reply))


    # log all errors
    dp.add_error_handler(error)

    # # run the bot with webhook handler
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=int(PORT),
    #                       url_path=TOKEN)
    # updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))


    updater.start_polling()
    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()


