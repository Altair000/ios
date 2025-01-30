# Bibliotecas de python
import os
# Bibliotecas de terceros
import telebot

TOKEN = os.getenv('bot_token', '8135078630:AAFih0JnMDPumrrFlLPbJnGYDJBuBI2Sk5g')
ADMIN = os.getenv('admin', 1519654469)

bot = telebot.TeleBot(TOKEN, threaded=False)
