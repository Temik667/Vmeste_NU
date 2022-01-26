import telebot
from telebot import types

API_KEY = '5073950568:AAHaViAz4s_2b-UcuY7jB2t9KcdWgUkIEoE'
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands = ['start'])
# def start(message):
#   bot.reply_to(message, 'How it is going?')

def start(message):
  markup = types.ReplyKeyboardMarkup()
  buttonA = types.KeyboardButton('Cоздать')
  buttonB = types.KeyboardButton('B')
  buttonC = types.KeyboardButton('C')

  markup.row(buttonA, buttonB)
  markup.row(buttonC)

  bot.send_message(message.chat.id, 'It works!', reply_markup=markup)
  
bot.polling()