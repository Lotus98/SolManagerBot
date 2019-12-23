#!/usr/bin/env python3
## -*- coding: utf-8 -*-
"""
UnipgSolBot
Author: Lotus
"""
import logging
from colorama import Fore, Style

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence)
from settings import LOGIN_URL, MAIN_URL, TOKEN
import sol_framework as sol
import requests
from bs4 import BeautifulSoup

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Create PicklePersistence object
pp = PicklePersistence(filename='u_data.pickle', on_flush=True)

def start(update, context):
	start_msg = "*Benvenuto a* @Sol_pg_Bot.\n"\
		"Questo bot ti permetterà di visualizzare, iscriverti gli appelli disponibili e quelli a cui ti sei già iscritto sulla piattaforma SOL Unipg.\n\n"\
		"NOTA: _Questo bot non è reallizzato ufficialmente, pertanto né Unipg né Cineca sono da considerarsi responsabili di questo bot in alcun modo._"

	update.message.reply_text(start_msg)
	pp.flush()

def login(update, context):
	send_user_pwd = 'Inserisci il tuo *username* e la tua *password* nel seguente formato (con un solo spazio in mezzo):\n\n'\
                    'username password\n\n'\
                    '_Si ricorda che il bot cancellerà immediatamente il messaggio inviato non appena sarà stato effettuato il login, per questioni di Privacy._'

	update.message.reply_markdown(send_user_pwd)
	return 1

def login_1(update, context):
	# Save credentials
	context.user_data['credentials'] = {}
	print(context.user_data)

    # Getting username and password from message's text
	user_pass = update.message.text.split(' ')
	print(user_pass)

    # Delete user message
	context.bot.delete_message(chat_id=update.effective_message.chat_id, message_id=update.message.message_id)

	if len(user_pass) == 2:
		context.user_data['credentials']['username'], context.user_data['credentials']['password'] = user_pass
	else:
		update.message.reply_markdown("Non hai *formattato correttamente* le tue credenziali, riprova.", reply_markup=ReplyKeyboardRemove())
		return 1

    # Send a message to the user to let him wait
	update.message.reply_text("Tentativo di connessione in corso, attendere...")
	context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)

	# Try login
	response = sol.connect(context.user_data)
	if response != "OK":
		update.message.reply_markdown(response, reply_markup=ReplyKeyboardRemove())
		return 1

	# Getting Name and Surname of the user just to show that login was performed correctly
	main_page = context.user_data['session'].get(MAIN_URL)
	soup= BeautifulSoup(main_page.text)
	name = soup.body.find('div', attrs={'class':'masthead_usermenu_user_name'}).text
	update.message.reply_markdown("Sono riuscito a collegarmi, benvenuto *%s*!" %name )

	# Update pickle file
	pp.flush()

	return ConversationHandler.END

def help(update, context):
	help_msg = "Questa è una lista degli attuali *comandi* presenti nel bot:\n\n"\
		"- /help: Visualizza questo messaggio\n"\
		"- /login: Effettua il Login sul portale SOL chiedendo le credenziali\n"\
		"- /logout: Cancella ogni dato personale raccolto dal Bot, compresa la sessione corrente ed effettuando quindi il Logout dal portale\n"\

	update.message.reply_markdown(help_msg)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def cancel(update, context):
    # Undo any command which is going on
    update.message.reply_text('Ok, comando annullato.', reply_markup=ReplyKeyboardRemove())


def main():
	# Create EventHandler with bot's token
	updater = Updater(TOKEN, persistence=pp, use_context=True)
	dp = updater.dispatcher

	# Adding all the Handlers for the commands
	cmd_login = ConversationHandler(
        entry_points=[CommandHandler('login', login)],

        states={
            1: [MessageHandler(Filters.text, login_1)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(CommandHandler('help', help))
	dp.add_handler(CommandHandler('cancel', cancel))
	dp.add_handler(cmd_login)

	# Log all errors
	dp.add_error_handler(error)

	# Starts the bot.
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
	updater.idle()


if __name__=='__main__':
	main()
