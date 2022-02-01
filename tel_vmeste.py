from dis import dis
import logging

import telegram
import keys
import Class_user
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

key = keys.API_KEY

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

NAME, SEX, PHOTO = range(3)
POINT_A, POINT_B, ADD_PERSON, PERSON_COUNT= range(4)

user_db = Class_user
new_user = {}

new_variable = 230
"""INITIATE REGISTRATION"""


def register(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('!!!REGISTER!!!\nYour name:')
    new_user['id'] = int(update.message.from_user.id)
    return NAME

def name(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Male', 'Female']]

    logger.info("Name of %s: %s", update.message.from_user.name, update.message.text)
    new_user['name'] = update.message.text

    update.message.reply_text(
        'Your sex:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Male/Female?'
        ),
    )
    return SEX

def sex(update: Update, context: CallbackContext) -> int:
    logger.info("Sex of %s: %s", update.message.from_user.name, update.message.text)
    new_user['sex'] = update.message.text

    update.message.reply_text('Your photo(/skip for skip):\nNote: photo increases the chance for matching',
    reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO

def skip_photo(update: Update, context: CallbackContext) -> int:
    logger.info("User %s did not send a photo.", update.message.from_user.name)
    new_user['photo'] = 0
    
    update.message.reply_text(
        'I bet you look great!\nDone! Now you can travel with others!\nType /ride to find a partner.')

def photo(update: Update, context: CallbackContext) -> int:
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('{}_photo.jpg'.format(update.message.from_user.id))

    logger.info("Photo of %s: %s", update.message.from_user.name, 'user_photo.jpg')
    new_user['photo'] = 1
    user_db.add_user(new_user['id'], new_user['name'], new_user['sex'], new_user['photo'])

    update.message.reply_text(
        'Done! Now you can travel with others!\nType /ride to find a partner.')

def registration_cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Registration calceled', reply_markup=ReplyKeyboardRemove()
    )
    new_user.clear()

    return ConversationHandler.END

"""INITIATE RIDE"""

def ride(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('!!!Ride initiated!!!\nTo cancel the ride type /cancel\nSend your location:\nUse Location in Telegram')
    return POINT_A

def point_a(update: Update, context: CallbackContext) -> int:
    user_location = update.message.location
    logger.info(
        "Departure is %s: %f / %f", update.message.from_user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Send location of the destination:\nUse Location in Telegram'
    )
    
    return POINT_B

def point_b(update: Update, context: CallbackContext) -> int:
    reply_buttons = [['Yes', 'No']]
    user_location = update.message.location
    logger.info(
        "Destination is %s: %f / %f", update.message.from_user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text('Want to add person?', 
    reply_markup=ReplyKeyboardMarkup(reply_buttons, one_time_keyboard=True, input_field_placeholder='Yes/No?'))

    return ADD_PERSON

def add_person(update: Update, context: CallbackContext) -> int:
    reply_buttons = [['1', '2', '3']]

    if update.message.text == 'Yes':
        update.message.reply_text('How many persons (up to 3):', 
        reply_markup=ReplyKeyboardMarkup(reply_buttons, one_time_keyboard=True, input_field_placeholder='1/2/3?'))
        return PERSON_COUNT
    else:
        update.message.reply_text('Done! We seek your pair!', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def person_count(update: Update, context: CallbackContext) -> int:
    logger.info("Add %s persons to the ride", update.message.text)

    update.message.reply_text('Done! We seek your pair!', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_db.is_new(user_id) == True:
        update.message.reply_text('Hello! I see that you are a new rider!\nPlease /register !')
    else:
        update.message.reply_text('Hello, {}!\nVmeste bot is dedicated for cooperative ride on taxis.\nPlease use the following commands:\n/help - to get info about commands\n/register - to register\n/ride - to get a ride!'.format(update.effective_user.first_name))


def ride_cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Ride calceled', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

"""GET BIO"""
def get_bio(update: Update, context: CallbackContext) -> None:
    name, sex, photo = user_db.name, user_db.sex, user_db.has_photo

    if photo == True:
        file = '{}_photo.jpg'.format(name)
        telegram.Bot.send_photo(update.effective_chat.id, filename = file)
    else:
        update.message.reply_text('!!!Your Bio!!!\nName: {}\nSex: {}\nPhoto: None'.format(name, sex))
    update.message.reply_text('!!!Your Bio!!!\nName: {}\nSex: {}\n'.format(name, sex))


def main() -> None:
    updater = Updater(key)
    
    dispatcher = updater.dispatcher

    register_conv = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            NAME: [MessageHandler(Filters.text, name)],
            SEX: [MessageHandler(Filters.regex('^(Male|Female)$'), sex)],
            PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler("skip", skip_photo)]
            },
        fallbacks=[CommandHandler('cancel', registration_cancel)],
    )

    ride_conv = ConversationHandler(
        entry_points=[CommandHandler("ride", ride)],
        states={
            POINT_A: [MessageHandler(Filters.location, point_a)],
            POINT_B: [MessageHandler(Filters.location, point_b)],
            ADD_PERSON: [MessageHandler(Filters.regex('^(Yes|No)$'), add_person)],
            PERSON_COUNT: [MessageHandler(Filters.regex('[1-3]'), person_count)],
        },
        fallbacks=[CommandHandler('cancel', ride_cancel)]
    )

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("bio", get_bio))
    dispatcher.add_handler(register_conv)
    dispatcher.add_handler(ride_conv)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()