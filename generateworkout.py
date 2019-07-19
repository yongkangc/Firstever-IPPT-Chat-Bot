from telegram import CallbackQuery

from application import *

CHOICE,TARGET,IPPTWORKOUT,PUSHUP_SCORE,SITUP_SCORE,NONTARGET = range(6)
logger = logging.getLogger(__name__)

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func

# @send_typing_action
def workout(update,context):
    """function for user to choose if they want their workout to be ippt or overall"""

    user = update.message.from_user
    keyboard = [[InlineKeyboardButton("IPPT Workout", callback_data='targeted'),
                 InlineKeyboardButton("General Workout", callback_data='non-targeted')],
                ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Do you want a IPPT targeted workout or a general workout?',reply_markup=reply_markup)
    choice = update.message.text

    logger.info("choice of %s,%s", user.first_name,choice)


    return TARGET




def target(update,context):
    """function for user to choose choices for their ippt workout"""
    keyboard = [[InlineKeyboardButton("Pushup", callback_data='pushup'),
                 InlineKeyboardButton("Situp", callback_data='situp'),
                 InlineKeyboardButton("Running", callback_data='run'),
                 InlineKeyboardButton("Overall", callback_data='all in one')
                 ],
                ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Which area do you want the workout to target?',reply_markup=reply_markup)

    return IPPTWORKOUT


def pushup_score_workout(update,context):
    keyboard = [[InlineKeyboardButton("Less than 40", callback_data='<40'),
                 InlineKeyboardButton("More than 40", callback_data='>40')]
                ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('How many Pushups can you do?', reply_markup=reply_markup)

    return PUSHUP_SCORE

def pushup_workout(update,context):

    number = update.message.text
    user = update.message.from_user
    logger.info("choice of %s,%s : Pushup workout", user.first_name,number)

    if number == "Less than 40":
        update.message.reply_text('<b>14 day Pushup Boost</b>\n'
                                  'This workout plan would boost your pushup numbers per minute by 50 - 75 %\n\n'
                                  '<b>On Odd Days:</b>\n'
                                  'Do 100 pushups in as few sets as possible, hitting maximum repetiton in each sets.'
                                  'You can still do upper body workouts or in addition to your cardio.\n\n'
                                '<b>On Even Days</b>\n'
                                  'Do 100 pushups throughout the day. This can be little sets of ten done every half hour or fifty pushups done four times throughout the day.\n\n'
                                  'Repeat the ODD/EVEN routine for a total of 10 days. Then take three days off and do NO upper body pushing exercises that work the chest, triceps, and shoulders. Then on day 14, give yourself the pushup test. I would not recommend this workout more than once every six months, since it rather challenging on the same muscle groups repeatedly.'
                                  ,
                                parse_mode=telegram.ParseMode.HTML)

        update.message.reply_text(
            'There are three main types of pushups you can do to break up the monotony: "regular" pushups, "wide" pushups, and triceps pushups.\n\n'
            'Read more at <a href = "https://www.military.com/military-fitness/fitness-test-prep/pullup-push-workout"> 14 day Pushup Plan </a>',
            parse_mode=telegram.ParseMode.HTML)

        end = update.message.reply_text('If you wanna talk to me again:\n\n'
                                        'Send /calculate - calculate your IPPT Score\n'
                                        'Send /workout - generates your workout\n'
                                        'or Send /start to choose!👍')

        job = context.job_queue.run_once(end, 10, context=update.message.chat_id)

        return ConversationHandler.END

    if number == "More than 40":
        update.message.reply_text('<b>14 day Pushup Boost</b>\n'
                                  'This workout plan would boost your pushup numbers per minute by 50 - 75 %\n\n'
                                  '<b>On Odd Days:</b>\n'
                                  'Do 100 pushups in as few sets as possible, hitting maximum repetiton in each sets.'
                                  'You can still do upper body workouts or in addition to your cardio.\n\n'
                                '<b>On Even Days</b>\n'
                                  'Do 100 pushups throughout the day. This can be little sets of ten done every half hour or fifty pushups done four times throughout the day.\n\n'
                                  'Repeat the ODD/EVEN routine for a total of 10 days. Then take three days off and do NO upper body pushing exercises that work the chest, triceps, and shoulders. Then on day 14, give yourself the pushup test. I would not recommend this workout more than once every six months, since it rather challenging on the same muscle groups repeatedly.'
                                  ,
                 parse_mode=telegram.ParseMode.HTML)

        update.message.reply_text('There are three main types of pushups you can do to break up the monotony: "regular" pushups, "wide" pushups, and triceps pushups.\n\n'
                                  'Read more at <a href = "https://www.military.com/military-fitness/fitness-test-prep/pullup-push-workout"> 14 day Pushup Plan </a>', parse_mode=telegram.ParseMode.HTML)

        end = update.message.reply_text('If you wanna talk to me again:\n\n'
                                  'Send /calculate - calculate your IPPT Score\n'
                                  'Send /workout - generates your workout\n'
                                  'or Send /start to choose!👍')

        job = context.job_queue.run_once(end, 10, context=update.message.chat_id)

        return ConversationHandler.END


@send_typing_action
def situp_workout_score(update,context):
    """Function to take user input for situps"""
    update.message.reply_text('What is the maximum number of Situps you can do in 1 minute?')

    return SITUP_SCORE

@send_typing_action
def situp_workout(update,context):
    """Function for situp workout"""

    user = update.message.from_user
    sitUp = update.message.text
    logger.info("Name : %s. sitUp: %s. Situp IPPT Workout", user.first_name, sitUp)

    if not re.match('^[0-9]{1,3}$', sitUp):
        update.message.reply_text('Sorry Please try again. Only input your Situps in number format. e.g 60')
        return SITUP_SCORE

    three_times_situp = int(sitUp)*3

    update.message.reply_text(
                              '<b>Situp 14 day Boost Plan</b>\n\n'
                              'In a nutshell, you will get better at situp tests by taking more situp tests and increasing your endurance by increasing your situp volume BUT at your goal pace for situps.\n\n'
                              '<b>Day 1–4</b>: \n\n'
                              '- Do {} situps in thirty second paced sets.\n'.format(three_times_situp) +
                              '- Aim for 20–25 situps in 30 seconds.So you will do roughly 8–9 sets of 20–25 situps in 30 seconds.\n'
                              '- After that, end it with 3 sets of 30 sec planks.\n\n'
                              '<b>Day 5–8</b>:\n\n '
                              '- Do {} situps in one minute paced sets.\n'.format(three_times_situp) +
                              '- But aim for 40–50 situps in 1 minute sets. This should take you 4–5 sets done through your workout for four days straight.\n'
                              '- After that, end it with 3 sets of 1 min plank.\n\n'.format(three_times_situp)+
                              '<b>Days 11–13</b>:\n\n'
                              'Time to recover – Take 3 days off from any abdominal exercises. You can exercise,but skip the ab exercises for this 3 days.\n\n'
                              '<b>Day 14: TEST Day</b>:\n\n'
                              '- Give yourself a mock test and focus on the goal pace you mastered.\n'
                              '- When you do your situps, practice exerting on the UP movement of the situp and letting gravity take you back to the ground. Just fall back – relaxing the abs for a second.\n\n\n'
                              '<b>Final Words</b>:\n\n'
                              'Spread these 30s/1min abs sets throughout your existing workout however you desire.\n'
                              'I personally like to put this abs workout in between sets of pullups or weighted exercises or even running intervals.\n\n'
                              '*<i>Note</i>  if you are having trouble keeping the goal pace for 30 seconds, try it for 15 seconds and shoot for quick timed sets of 10–12 repetitions for 15 seconds.  The first 15–20 seconds of a 2 minute situp test is where people start off too fast, so it is a good idea to practice the start of the test regularly.\n\n'
                              'Find out more at <a href="https://www.military.com/military-fitness/workouts/situp-test-help-improve-fast">Situp 14 day Boost Plan</a>'
                            ,parse_mode=telegram.ParseMode.HTML)

    update.message.reply_text('If you wanna talk to me again:\n\n'
                                    'Send /calculate - calculate your IPPT Score\n'
                                    'Send /workout - generates your workout\n'
                                    'or Send /start to choose!👍')

    return ConversationHandler.END



@send_typing_action
def running_workout(update,context):
    """Programme for ippt 2.4 run"""

    update.message.reply_text('<b>Interval Workout #1</b>\n\n'
                              'Warm up with 800 m easy jog\n\n'
                              'Run 400m x 6 sets\n'
                              '- Run each round at your 2.4 km goal pace(example 1:30 = 9 min, 2.4 km goal pace)\n'
                              '- Rest ratio is 1 to 1 (e.g if you take 1 min 30 s to run, rest for 1 min 30 s)')

    update.message.reply_text('<b>Interval Workout #2</b>\n\n'
                              'Warm up with 800 m easy jog\n\n'
                              'Run 800m x 3-4 sets\n'
                              '- Run each round at your 2.4 km goal pace(example 1:30 = 9 min, 2.4 km goal pace)\n'
                              '- Rest 3 min per set\n\n'
                              '<i>Note</i>: you could mix in 1 minute calistenics (squats, lunges, pushups, sit-ups -- your choice, depending on upper body or lower body days')

    end = update.message.reply_text('If you wanna talk to me again:\n\n'
                                    'Send /calculate - calculate your IPPT Score\n'
                                    'Send /workout - generates your workout\n'
                                    'or Send /start to choose!👍')

    job = context.job_queue.run_once(cancel, 10, context=update.message.chat_id)

    return ConversationHandler.END


@send_typing_action
def overall_workout(update,context):
    update.message.reply_text('<b>Circuit IPPT Training</b>'
                              '<b>4-6 Sets</b>\n\n'
                              'You only have 10 min to complete each set.\n'
                              'The longer you take to complete the circuit, the shorter your rest time.\n\n'
                              'Run 400m at your goal pace (e.g 1:30 = 9 min, 2.4 km goal pace)\n\n'
                              'Pull ups : 1 - 10 reps\n\n'
                              'Situps : 15 - 50 reps\n\n'
                              'Pushups : \n\n'
                              'Flutter Kicks : 20 counts of 4\n\n'
                              'Diamond Pushups : 5 - 15 reps\n\n'
                              '<i>Rest the remaining of your 10 min before going for the next set</i>'
                              )


    context.job_queue.run_once(cancel, 10, context=update.message.chat_id)

    return ConversationHandler.END


@send_typing_action
def nontarget(update,context):
    keyboard = [[InlineKeyboardButton("Weight Circuit Training", callback_data='Weight Circuit Training'),
                 InlineKeyboardButton("Calistenics Circuit Training", callback_data='Calistenics Circuit Training '),
                 InlineKeyboardButton("Core", callback_data='core'),
                 InlineKeyboardButton("Swimming", callback_data='all in one'),
                 InlineKeyboardButton("Random", callback_data='random')

                 ],
                ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('What type of training do you want to do?', reply_markup=reply_markup)

    return NONTARGET

@send_typing_action
def weight_circuit(update,context):
    update.message.reply_text('<b>Weight Circuit training programme</b>\n\n'
                              'Target: Push, Pull, Leg, Full, Core, Cardio\n\n'
                              '<b>3 - 4 Sets</b>'
                              '- Bench Press x 10\n'
                              '- Lat Pulldown x 10 or One Arm Dumbell Row\n'
                              '- Barbell Squats or Leg Press x 10\n'
                              '- Dumbell Shoulder Press x 10\n'
                              '- Plank for 1 min\n'
                              '- Tabata intervals - 20 sec sprint / 10 sec easy. To work heart rate and challenge the fast paced energy system.\n'
                              '- Rest 5 min')

    context.job_queue.run_once(cancel, 10, context=update.message.chat_id)

    return ConversationHandler.END

def swimming(update,context):
    update.message.reply_text('[Military Swimming Programme](https://www.military.com/military-fitness/military-workouts/military-pft-prep/ask-stew-how-pace-ace-your-fitness-test)\n\n'
                              'Warm up 3 laps\n'
                              '<b>10 sets</b>: \n'
                              '- 50m Swim freestyle FAST (6-8 strokes per breath)\n'
                              '- 50m NO REST go into Swim CSS -- at your goal pace*\n'
                              '- Rest 10 seconds before starting again\n'
                              '- Do this swim workout 5-6 days a week. Minimum standard daily is 1,000-1,500m if you want to get in shape to swim 500m fast.\n')

    context.job_queue.run_once(cancel, 40, context=update.message.chat_id)

    return ConversationHandler.END


def cali_circuit(update,context):
    update.message.reply_text('<b>Calistenics Circuit Training Programme</b>:\n\n'
                              '<b>3-4 Sets</b>\n'
                              '- Run 400 m\n'
                              '- Dips / Push up 5-10 / 20-30 \n'
                              '- Pull up / assisted pullups max rep\n'
                              '- Lunges 20 per leg\n'
                              '- 8 Count Body Builder / Burpees 10-20\n'
                              '- Rest 3 min\n')

    context.job_queue.run_once(cancel, 40, context=update.message.chat_id)

    return ConversationHandler.END

def core(update,context):
    update.message.reply_text('## <b>Core</b>The idea of this workout is to train the core as a whole using various exercises at a high intensity.'
                              '## <b>3 Sets</b>\n'
                              '### Insert planks in between each core exercise\n'
                              '### Change exercise every 30 secs.\n'
                              '- <a href="https://www.popsugar.com/fitness/How-Do-Butterfly-Crunch-40322354">Butterfly Crunches</a>\n'
                              '- <a href="https://www.wikihow.fitness/Do-Spiderman-Planks">Spider Plank</a>\n'
                              '- <a href="https://squatwolf.com/blog/how-to-do-flutter-kicks-correctly/">Flutter Kick</a>\n'
                              '- <a href="https://www.bodybuilding.com/exercises/russian-twist">Russian Twist</a>\n'
                              '- <a href= "https://www.verywellfit.com/mountain-climbers-exercise-3966947">Mountain Climber</a>\n\n'
                              '<i>Therefore you would be doing butterfly crunches, followed by planks,followed by spider planks and then planks again and so on.</i>')



def random_workout(update,context):
    """generates a random workout from the document"""

    update.message.reply_text('<b>Calistenics Circuit Training Programme</b>:\n\n'
                              '<b>3-4 Sets</b>\n'
                              '- Run 400 m\n'
                              '- Dips / Push up 5-10 / 20-30 \n'
                              '- Pull up / assisted pullups max rep\n'
                              '- Lunges 20 per leg\n'
                              '- 8 Count Body Builder / Burpees 10-20\n'
                              '- Rest 3 min\n')

    context.job_queue.run_once(cancel, 40, context=update.message.chat_id)

    return ConversationHandler.END