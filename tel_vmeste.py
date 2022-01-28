from http.client import PRECONDITION_FAILED
import logging
import numbers
from pydoc import text
from unicodedata import name
from more_itertools import one

from sqlalchemy import true, update
from sympy import register_handler
from zmq import Message
import keys

# Add the necessary modules
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

key = keys.API_KEY

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

NAME, SEX, PHOTO = range(3)
POINT_A, POINT_B, ADD_PERSON, PERSON_COUNT= range(4)

def register(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('!!!REGISTER!!!\nYour name:')
    return NAME

def name(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Male', 'Female']]

    logger.info("Name of %s: %s", update.message.from_user.name, update.message.text)
    update.message.reply_text(
        'Your sex:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Male/Female?'
        ),
    )
    return SEX

def sex(update: Update, context: CallbackContext) -> int:
    logger.info("Sex of %s: %s", update.message.from_user.name, update.message.text)
    update.message.reply_text('Your photo(/skip for skip):\nNote: photo increases the chance for matching',
    reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO

def skip_photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.name)
    
    update.message.reply_text(
        'I bet you look great!\nDone! Now you can travel with others!\nType /ride to find a partner'
    )

def photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.name, 'user_photo.jpg')
    update.message.reply_text('Done! Now you can travel with others!\nType /ride to find a partner')

def ride(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('!!!Ride initiated!!!\nTo cancel the ride type /cancel\nSend your location:\nUse Location in Telegram')
    return POINT_A

def point_a(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Departure is %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Send location of the destination:\nUse Location in Telegram'
    )
    
    return POINT_B

def point_b(update: Update, context: CallbackContext) -> int:
    reply_buttons = [['Yes', 'No']]
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Destination is %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
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
    update.message.reply_text('Hello, {}!'.format(update.effective_user.first_name))

def registration_cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Registration calceled', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def ride_cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Ride calceled', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


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
    numbers='123'
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
    dispatcher.add_handler(register_conv)
    dispatcher.add_handler(ride_conv)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()