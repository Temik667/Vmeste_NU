import logging
import keys

# Add the necessary modules
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

key = keys.API_KEY

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
"""The stuff we need for the bot to operate it, above. Sorry IDK"""


# First we add the functions that we want to have in our program

"""this is start function. 
Update module retrieves the data from telegram, such as messages
and other. As you see, we can access to different type of information 
using different attriburtes such as effective_user.first_name

CallbackContext is responsible for attaching functions to the commands
user inputs in the telegram"""
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello, {}!'.format(update.effective_user.first_name))


def get_userID(update: Update, context: CallbackContext) -> None: 
    user = update.message.from_user
    update.message.reply_text('Your Name: {}\nID: {}'.format(user['username'], user['id']))

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main() -> None:
  # Start of the bot
  
  # Here goes the TOKEN of our Bot
    updater = Updater(key)

    # This allow to call functions we wrote above
    dispatcher = updater.dispatcher

    # methods call different functions we wrote above. First goes the command line, 
    # and then the function.
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("getID", get_userID))

    # this handler takes any message and repeats it, doesn't read commands
    # Filters used to select particular types of data (such as, text, video, photo, commands)
    # Here `~` sign means does not read
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # checks for the incoming messages
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()