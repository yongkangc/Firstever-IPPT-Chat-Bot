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

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOICE, AGE, PUSHUPS, SITUPS, RUNTIME, RECEIVED_INFORMATION, EDIT, END = range(8)
TOKEN = os.getenv("TOKEN")
bot = telegram.Bot(TOKEN)


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



def start(update, context):
    """ /start command for the 2 user options """

    keyboard = [[InlineKeyboardButton("Calculate IPPT Score", callback_data='Calculate IPPT Score'),
                 InlineKeyboardButton("Generate Workout", callback_data='Generate Workout')],
                ]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    # bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    update.message.reply_text('Hi! I am the IPPT Bot! My only purpose is to help you with your IPPT 💪.\n'
                              'Send /cancel to stop talking to me.\n\n'
                              'How can i help? 😊', reply_markup=reply_markup)

    return CHOICE


@send_typing_action
def calculate(update, context):
    """ /calculate command """

    update.message.reply_text('My only purpose is to help you with your IPPT 💪.\n'
                              'Send /cancel to stop talking to me.\n'
                              'You have chosen to calculate your IPPT Score.\n\n'
                              'Please send me your age!')
    return AGE


@send_typing_action
def choice(update, context):
    """asking age"""

    user = update.message.from_user
    logger.info("Choice of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('How old are you? Don\'t worry, no one else would know.',
                              reply_markup=ReplyKeyboardRemove())

    return AGE


@send_typing_action
def age(update, context):
    """Stores age value and ask for pushup"""

    user = update.message.from_user
    age = update.message.text

    logger.info("Age of %s: %s", user.first_name, age)
    if not re.match('^[0-9]{1,2}$', age):
        update.message.reply_text('Sorry Please try again. Only input your age in number format. e.g 21')
        return AGE
    else:
        # adds user age into dict 'context.user_data'
        context.user_data['Age'] = age
        update.message.reply_text('How many pushup can you do in 60 seconds?')

    return PUSHUPS


@send_typing_action
def pushupcount(update, context):
    """Stores pushup value and ask for situps"""

    user = update.message.from_user
    pushUp = update.message.text

    logger.info("Pushup of %s: %s", user.first_name, pushUp)
    if not re.match('^[0-9]{1,2}$', pushUp):
        update.message.reply_text('Sorry Please try again. Only input your push-ups in number format. e.g 60')
        return PUSHUPS
    else:
        context.user_data['Pushups'] = pushUp
        update.message.reply_text('How many sit-ups can you do in 60 seconds?')

    return SITUPS


@send_typing_action
def situpcounts(update, context):
    """Stores situp value and ask for run"""

    user = update.message.from_user
    sitUp = update.message.text
    logger.info("Name : %s. sitUp: %s", user.first_name, sitUp)

    if not re.match('^[0-9]{1,2}$', sitUp):
        update.message.reply_text('Sorry Please try again. Only input your sit-ups in number format. e.g 60')
        return SITUPS

    else:
        context.user_data['Situps'] = sitUp
        update.message.reply_text('How long do you take to complete 2.4km run? Please enter in mins secs format (e.g 1130)')

    return RUNTIME


@send_typing_action
def run_time(update, context):
    """Stores run value"""

    user = update.message.from_user
    runTime = update.message.text

    logger.info("Name: %s. RunTime: %s", user.first_name, runTime)
    if not re.match('^[0-9]{4}$', runTime):
        update.message.reply_text('Sorry please enter again in mins secs e.g 1130 for 11:30: ')
        return RUNTIME
    else:
        context.user_data['Run Time'] = runTime

        # key board for the user to edit his information
        user_data = context.user_data
        reply_keyboard = [['Age', 'Pushups'],
                          ['Situps', 'Run Time'],
                          ['Done']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text("Is the Information correct bro?"
                                  "{}"
                                  "Click Done if it is correct.If Not, Please click on the wrong section to correct me. ".format(
            facts_to_str(user_data)), reply_markup=markup)

    return EDIT


@send_typing_action
def received_information(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    reply_keyboard = [['Age', 'Pushups'],
                      ['Situps', 'Run Time'],
                      ['Done']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    update.message.reply_text("Is the Information correct bro?"
                              "{}"
                              "Click Done if it is correct.If not please correct me".format(
        facts_to_str(user_data)), reply_markup=markup)

    return EDIT


@send_typing_action
def regular_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'Your {}? Please correct me.'.format(text.lower()))

    return RECEIVED_INFORMATION


def facts_to_str(user_data):
    """Converts Dict value into Text message"""

    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def find_ageGroup(age):
    """function to find age grp for ippt"""

    agegrp = [[20, 22], [22, 25],
              [25, 28],
              [28, 31],
              [31, 34],
              [34, 37],
              [37, 40],
              [40, 43],
              [43, 46],
              [46, 49],
              [49, 52],
              [52, 55],
              [55, 58],
              [58, 61]]

    for i in range(len(agegrp)):
        for r in agegrp:
            if r[0] <= age < r[1]:
                logger.info(agegrp)
                return agegrp.index(r) + 1


def roundup(x):
    """helper function to round up running time"""
    return int(math.ceil(x / 10.0)) * 10


@send_typing_action
def calculate_score_grade(update, context):
    """Function to calculate the total IPPT Score"""

    userinput = context.user_data
    age = int(userinput['Age'])
    min_age = 20
    max_age = 60

    if age < min_age:
        age = min_age
    elif age > max_age:
        age = max_age

    pushUp = int(userinput['Pushups'])
    if pushUp > 60:
        pushUp = 60

    sitUp = int(userinput['Situps'])
    if sitUp > 60:
        sitUp = 60

    runTime = userinput['Run Time']
    min = int(runTime[0:2])
    sec = int(runTime[2:4])

    runTime = min * 60 + sec
    runTime = roundup(runTime)
    if runTime > 1100:
        runTime = 1100
    elif runTime < 510:
        runTime = 510

    agegrp = find_ageGroup(age)
    logger.info("Runtime:%s", runTime)

    tier_list = [
        (100, "PERFECT FITNESS"),
        (90, "Commando gold"),
        (85, "Gold"),
        (75, "Silver"),
        (61, "Pass for NSF/Incentive"),
        (51, "Pass for NSMEN"),
        (0, "Fail")
    ]

    pushUpScore = (pushUpScores.get(str(pushUp)))[agegrp - 1]
    sitUpScore = (sitUpScores.get(str(sitUp)))[agegrp - 1]
    runScore = (runScores.get(str(runTime)))[agegrp - 1]

    total_score = int(pushUpScore) + int(sitUpScore) + int(runScore)
    grade = "Trainee"
    almost_grade = "Trainee"
    almost_point = 100
    point_needed = 0

    user = update.message.from_user
    logger.info("Name : %s. Score: %s", user.first_name, total_score)

    for tier in tier_list:
        if total_score < tier[0]:
            almost_grade = tier[1]
            almost_point = tier[0]
        else:
            grade = tier[1]
            point_needed = almost_point - total_score
            break
    logger.info("Name : %s. tier: %s", user.first_name, grade)
    try:
        if total_score < 100:
            update.message.reply_text(
                ('Your Score : {} {}.\n {} more points to {}. 💪').format(total_score, grade, point_needed,
                                                                          almost_grade))
            update.message.reply_text('Bro if you wanna talk to me again:\n\n'
                                      'Send /calculate - calculate your IPPT Score\n'
                                      'Send /workout - generates your workout\n'
                                      'or Send /start to choose!👍')
            return ConversationHandler.END
        else:
            update.message.reply_text('100 Points! Perfect! 💪 ')
            update.message.reply_text('Bro if you wanna talk to me again:\n\n'
                                      'Send /calculate - calculate your IPPT Score\n'
                                      'Send /workout - generates your workout\n'
                                      'or Send /start to choose!👍')

            return ConversationHandler.END

    except TelegramError:
        logger.info('Your Score : %s %s. %s more points to %s . Type anything to try again.', total_score, grade,
                    point_needed, almost_grade)
        update.message.reply_text('Sorry there was an error. /cancel then /calculate to try again')



        return ConversationHandler.END


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
    update.message.reply_text('Bye {}! Type anything to talk to me again :)'.format(user.first_name),
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    logger.info("Starting bot")

    #setting config for deployment
    # Port is given by Heroku
    PORT = os.environ.get('PORT')
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('calculate', calculate)],
        states={
            CHOICE: [MessageHandler(Filters.regex('^(Calculate IPPT Score|Generate Workout)$'), choice)],
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
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text, non_command_reply))


    # log all errors
    dp.add_error_handler(error)

    # run the bot with webhook handler
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()


