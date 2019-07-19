from application import *



""" Functions that perform the /calculate command of the app """


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
    sec = int(runTime[3:5])

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
        (90, "🥇 Commando gold"),
        (85, "🥇 Gold"),
        (75, "🥈 Silver"),
        (61, "🥉 Pass for NSF/Incentive"),
        (51, "Fail for NSF/Pass for NSMEN"),
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
                ('Your Score : {} {}.\n{} more points to {} 💪').format(total_score, grade, point_needed,
                                                                          almost_grade))

            time.sleep(3)

            update.message.reply_text('If you wanna talk to me again:\n\n'
                                      'Send /calculate - calculate your IPPT Score\n'
                                      'Send /workout - generates your workout\n'
                                      'or Send /start to choose!👍')

            return ConversationHandler.END

        else:
            update.message.reply_text('100 Points! Perfect! 💪 ')
            time.sleep(15)
            update.message.reply_text('If you wanna talk to me again:\n\n'
                                      'Send /calculate - calculate your IPPT Score\n'
                                      'Send /workout - generates your workout\n'
                                      'or Send /start to choose!👍')

            return ConversationHandler.END

    except TelegramError:
        logger.info('Your Score : %s %s. %s more points to %s . Type anything to try again.', total_score, grade,
                    point_needed, almost_grade)
        update.message.reply_text('Sorry there was an error.\n /cancel then /calculate to try again')



        return ConversationHandler.END



@send_typing_action
def calculate(update, context):
    """ /calculate command """

    update.message.reply_text('My only purpose is to help you with your IPPT 💪\n'
                              'Send /cancel to stop talking to me.\n'
                              'You have chosen to calculate your IPPT Score.\n\n'
                              'Please send me your age!')
    return AGE

@send_typing_action
def choice(update, context):
    """asking age"""

    user = update.message.from_user
    logger.info("Choice of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('What is your current age? Don\'t worry, no one else will know.',
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
        update.message.reply_text('How many Pushups can you do in 1 minute?')

    return PUSHUPS


@send_typing_action
def pushupcount(update, context):
    """Stores pushup value and ask for situps"""

    user = update.message.from_user
    pushUp = update.message.text

    logger.info("Pushup of %s: %s", user.first_name, pushUp)
    if not re.match('^[0-9]{1,2}$', pushUp):
        update.message.reply_text('Sorry Please try again. Only input your Pushups in number format. e.g 60')
        return PUSHUPS
    else:
        context.user_data['Pushups'] = pushUp
        update.message.reply_text('How many Situps can you do in 1 minute?')

    return SITUPS


@send_typing_action
def situpcounts(update, context):
    """Stores situp value and ask for run"""

    user = update.message.from_user
    sitUp = update.message.text
    logger.info("Name : %s. sitUp: %s", user.first_name, sitUp)

    if not re.match('^[0-9]{1,3}$', sitUp):
        update.message.reply_text('Sorry Please try again. Only input your Situps in number format. e.g 60')
        return SITUPS

    else:
        context.user_data['Situps'] = sitUp
        update.message.reply_text('How long do you take for a 2.4km run? Please enter in mins.secs format (e.g 11.30)')

    return RUNTIME


@send_typing_action
def run_time(update, context):
    """Stores run value"""

    user = update.message.from_user
    runTime = update.message.text

    logger.info("Name: %s. RunTime: %s", user.first_name, runTime)
    if not re.match('^[0-9]{2}[.][0-9]{2}$', runTime):
        update.message.reply_text('Sorry, Please enter again in mins.secs e.g 11.30 for 11:30: ')
        return RUNTIME
    else:
        context.user_data['Run Time'] = runTime

        # key board for the user to edit his information
        user_data = context.user_data
        reply_keyboard = [['Age', 'Pushups'],
                          ['Situps', 'Run Time'],
                          ['Done']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text("Is the Information correct?"
                                  "{}"
                                  "Click Done if it is correct. If Not, Please click on the wrong section to correct the information. ".format(
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

    update.message.reply_text("Is the Information correct?"
                              "{}"
                              "Click Done if it is correct.\nIf not please correct me".format(
                            facts_to_str(user_data)), reply_markup=markup)

    return EDIT


@send_typing_action
def regular_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'Your {}? Please correct me.'.format(text.lower()))

    return RECEIVED_INFORMATION
