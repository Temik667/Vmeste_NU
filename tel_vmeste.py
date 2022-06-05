import logging
import telegram
import keys
import Class_user
import Class_ride
from parse import *
import os

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

key = keys.API_KEY
bot = telegram.Bot(token = key)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

NAME, SEX, PHOTO = range(3)
POINT_A, POINT_B, ADD_PERSON, MATCH, RESULT= range(5)
YES = range(1)

user_db = Class_user.sql_class
new_user = {}

"""INITIATE REGISTRATION"""


# def register(update: Update, context: CallbackContext) -> int:
#     user_id = update.message.from_user.id
#     if user_db.is_new(user_id) == False:
#         update.message.reply_text('You are not a new user!\n')
#         ConversationHandler.END
#         return
        
#     update.message.reply_text('!!!REGISTER!!!\n(/cancel to cancel)')
#     new_user['id'] = int(update.message.from_user.id)
#     return NAME

def register(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    if user_db.is_new(user_id) == False:
        update.message.reply_text('You are not a new user!\n')
        return ConversationHandler.END
    reply_keyboard = [['Male', 'Female']]

    logger.info("Name of %s: %s", update.message.from_user.name, update.message.text)
    new_user['name'] = update.message.from_user.name
    new_user['id'] = int(update.message.from_user.id)

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
    user_db.add_user(int(new_user['id']), str(new_user['name']), str(new_user['sex']), int(new_user['photo']))
    new_user.clear()
    
    update.message.reply_text(
        'I bet you look great!\nNow you can travel with others!\n/ride to find a partner.')
    return ConversationHandler.END

def photo(update: Update, context: CallbackContext) -> int:
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('{}_photo.jpg'.format(update.message.from_user.id))

    logger.info("Photo of %s: %s", update.message.from_user.name, 'user_photo.jpg')
    new_user['photo'] = 1
    user_db.add_user(int(new_user['id']), str(new_user['name']), str(new_user['sex']), int(new_user['photo']))
    new_user.clear()

    update.message.reply_text(
        'Done!\nNow you can travel with others!\nType /ride to find a partner.')
    return ConversationHandler.END    

def registration_cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Registration calceled', reply_markup=ReplyKeyboardRemove()
    )
    new_user.clear()

    return ConversationHandler.END

"""RIDE LIST"""
def ride_list(user_id):
    near = Class_ride.Requests.showNearest(user_id)
    ride_list = ""
    counter = 1
    for item in near:
        if item == list(near)[-1]:
            ride_list += "{}. Name: {}\nSex: {}\nPassengers: {}\nPrice: {}".format(counter, item['name'], item['sex'], item['num'] + 1 , item['price'])
            break
        ride_list += "{}. Name: {}\nSex: {}\nPassengers: {}\nPrice: {}\n".format(counter, item['name'], item['sex'], item['num'] + 1 , item['price'])
        counter += 1
    
    return ride_list


"""INITIATE RIDE"""

def ride(update: Update, context: CallbackContext) -> int:
    if user_db.is_new(update.message.from_user.id) == True:
        update.message.reply_text("You are not registered yet!\nPlease /register")
        return ConversationHandler.END
    update.message.reply_text('!!!Ride initiated!!!\nTo cancel the ride type /cancel\nSend your location:\nUse Location in Telegram')
    Class_ride.Requests.add_request(update.message.from_user.id)
    return POINT_A

def point_a(update: Update, context: CallbackContext) -> int:
    user_location = update.message.location
    logger.info(
        "Departure is %s: %f / %f", update.message.from_user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Send location of the destination:\nUse Location in Telegram'
    )
    Class_ride.Requests.add_a_point(update.message.from_user.id, user_location.latitude, user_location.longitude)
    return POINT_B

def point_b(update: Update, context: CallbackContext) -> int:
    reply_buttons = [['1', '2', '3']]
    user_location = update.message.location
    logger.info(
        "Destination is %s: %f / %f", update.message.from_user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text('How many passangers?', 
    reply_markup=ReplyKeyboardMarkup(reply_buttons, one_time_keyboard=True, input_field_placeholder='1, 2, 3?'))
    Class_ride.Requests.add_b_point(update.message.from_user.id, user_location.latitude, user_location.longitude)
    return ADD_PERSON

def add_person(update: Update, context: CallbackContext):
    update.message.reply_text('Done!\nWe seek your pair!', reply_markup=ReplyKeyboardRemove())
    Class_ride.Requests.add_others(update.message.from_user.id, int(update.message.text), update.effective_chat.first_name, user_db.find_sex(update.message.from_user.id))
    text = ride_list(update.message.from_user.id)
    return MATCH

def match(update: Update, context: CallbackContext) -> int:
    
    return RESULT

def result(update: Update, context: CallbackContext) -> None:
    if update.message.text == 'Wait for more':
        update.message.reply_text('Seeking further')
        return MATCH
    update.message.reply_text('Match Found!')
    Class_ride.Requests.remove_request(update.message.from_user.id)
    return ConversationHandler.END

def ride_cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Ride calceled', reply_markup=ReplyKeyboardRemove()
    )
    Class_ride.Requests.remove_request(update.message.from_user.id)
    return ConversationHandler.END

"""GET BIO"""
def get_bio(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_db.is_new(user_id) == True:
        update.message.reply_text('You are not registered yet!\nPlease /register')
        return 

    name = user_db.find_name(user_id)
    sex =  user_db.find_sex(user_id)
    has_photo = user_db.has_photo(user_id)
    if has_photo == True:
        file = '{}_photo.jpg'.format(user_id)
        bot.send_photo(update.effective_chat.id, photo = open(file, 'rb'), filename = file)
        update.message.reply_text('!!!Your Bio!!!\nName: {}\nSex: {}\nPhoto: Present'.format(name, sex))
    else:
        update.message.reply_text('!!!Your Bio!!!\nName: {}\nSex: {}\nPhoto: None'.format(name, sex))

"""START"""
def start(update: Update, context: CallbackContext) -> None:
    if user_db.is_new(update.message.from_user.id) == True:
        update.message.reply_text('Hello! I see that you are a new rider!\nVmeste bot is dedicated for cooperative ride on taxis.\nPlease /register')
    else:
        update.message.reply_text('Hello, {}!\n/ride - to get a ride!\n/help - to get list of commands'.format(update.effective_user.first_name))


"""UPDATE"""
        
# def update_name(update: Update, context: CallbackContext) -> int:
#     get_bio(update, context)
#     update.message.reply_text('Your new name(or old one):\n/cancel for cancel')
#     return NAME

# def update_name_func(update: Update, context: CallbackContext) -> int:
#     logger.info("Updated name of %s: %s", update.message.from_user.name, update.message.text)
#     name = update.message.text
#     user_db.update_name(update.message.from_user.id, name)
#     update.message.reply_text('Updated name! Now you are more yourself than you were ever before!')
#     return ConversationHandler.END

def update_sex(update:Update, context: CallbackContext) -> int:
    get_bio(update, context)
    reply_keyboard = [['Male', 'Female']]

    update.message.reply_text(
        'Your new sex(or old one):\n/cancel for cancel',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Male/Female?'
        ),
    )
    return SEX

def update_sex_func(update: Update, context: CallbackContext) -> int:
    logger.info("Updated sex of %s: %s", update.message.from_user.name, update.message.text)
    sex = update.message.text
    user_db.update_sex(update.message.from_user.id, sex)
    update.message.reply_text('Updated sex! Now you are more yourself than you were ever before!', 
    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def update_photo(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Upload a photo(or to delete current one /delete_photo\n/cancel for cancel')
    return PHOTO

def update_photo_func(update:Update, contex: CallbackContext) -> int:
    text = 'Updated Photo!\nIndeed, you are a human, not a robot!'
    if user_db.has_photo(update.message.from_user.id) == True:
        os.remove('{}_photo.jpg'.format(update.message.from_user.id))
        text = 'Updated Photo! You are nicer on this one!'
    
    user_db.update_photo(update.message.from_user.id, 1)
    logger.info("Removed photo of %s: %s", update.message.from_user.name, 'user_photo.jpg')
    
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('{}_photo.jpg'.format(update.message.from_user.id))

    logger.info("Updated photo of %s: %s", update.message.from_user.name, 'user_photo.jpg')
    
    
    update.message.reply_text(text)
    return ConversationHandler.END 

def delete_photo(update: Update, context: CallbackContext) -> int:
    if user_db.has_photo(update.message.from_user.id) == False:
        update.message.reply_text('You do not have photo to delete.')
        return ConversationHandler.END
    logger.info("User %s deleted photo", update.message.from_user.name)
    os.remove('{}_photo.jpg'.format(update.message.from_user.id))
    
    user_db.update_photo(update.message.from_user.id, 0)
    update.message.reply_text('Photo deleted!')
    return ConversationHandler.END

def update_cancel(update:Update, context: CallbackContext) -> int:
    update.message.reply_text('Update canceled')
    return ConversationHandler.END

"""DELETE USER"""
def delete_me(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Yes', 'No']]

    update.message.reply_text(
        'WANT TO BE DELETED!?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='No Please GOD PLEASE NOOOO!'
        ),
    )

    return YES

def delete_me_func(update: Update, context: CallbackContext) -> None:
    if update.message.text == 'Yes':
        update.message.reply_text('Goodbye my friend ;(')
        user_db.delete_user(update.message.from_user.id)
        if user_db.has_photo(update.message.from_user.id):
            os.remove('{}_photo.jpg'.format(update.message.from_user.id))
    
    else:
        update.message.reply_text('Ops! That was close!')
    
    return ConversationHandler.END

"""HELP"""
def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Commands:\n/register - registration\n/get_bio - biography\n/ride - initiate ride\n\nUpdate bio:\n/update_sex\n/update_photo\n/delete_me - delete user from the database')




def main() -> None:
    updater = Updater(key)
    
    dispatcher = updater.dispatcher

    register_conv = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            SEX: [MessageHandler(Filters.regex('^(Male|Female)$'), sex)],
            PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler("skip", skip_photo)]
            },
        fallbacks=[CommandHandler('cancel', registration_cancel)],
        conversation_timeout=60
    )

    ride_conv = ConversationHandler(
        entry_points=[CommandHandler("ride", ride)],
        states={
            POINT_A: [MessageHandler(Filters.location, point_a)],
            POINT_B: [MessageHandler(Filters.location, point_b)],
            ADD_PERSON: [MessageHandler(Filters.regex('[1-3]'), add_person)],
            MATCH: [MessageHandler(Filters.text, match)],
            RESULT: [MessageHandler(Filters.regex('^(Yes|No)$'), result)]
        },
        fallbacks=[CommandHandler('cancel', ride_cancel)],
    )

    # update_name_conv=ConversationHandler(
    #     entry_points=[CommandHandler("update_name", update_name)],
    #     states={
    #         NAME: [MessageHandler(Filters.text, update_name_func)]
    #     },
    #     fallbacks=[CommandHandler('cancel', update_cancel)],
    #     conversation_timeout=60
    # )

    update_sex_conv=ConversationHandler(
        entry_points=[CommandHandler("update_sex", update_sex)],
        states={
            SEX: [MessageHandler(Filters.regex('^(Male|Female)$'), update_sex_func)]
        },
        fallbacks=[CommandHandler('cancel', update_cancel)],
        conversation_timeout=60
    )

    update_photo_conv=ConversationHandler(
        entry_points=[CommandHandler("update_photo", update_photo)],
        states={
            PHOTO: [MessageHandler((Filters.photo), update_photo_func), CommandHandler("delete_photo", delete_photo)]
        },
        fallbacks=[CommandHandler('cancel', update_cancel)],
        conversation_timeout=60
    )

    delete_user_conv=ConversationHandler(
        entry_points=[CommandHandler("delete_me", delete_me)],
        states={
            YES: [MessageHandler(Filters.regex('^(Yes|No)$'), delete_me_func)]
        },
        fallbacks=[CommandHandler('cancel', delete_me_func)],
        conversation_timeout=60
    )
   
   
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("get_bio", get_bio))
    dispatcher.add_handler(CommandHandler("help", help))
    
    # dispatcher.add_handler(update_name_conv)
    dispatcher.add_handler(update_sex_conv)
    dispatcher.add_handler(update_photo_conv)
    dispatcher.add_handler(register_conv)
    dispatcher.add_handler(ride_conv)
    dispatcher.add_handler(delete_user_conv)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()