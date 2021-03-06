#!/usr/bin/env python3
## -*- coding: utf-8 -*-
"""
UnipgSolBot
Author: Lotus
"""
import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ChatAction,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence, CallbackQueryHandler)
from settings import *
import sol_framework as sol
import requests
from bs4 import BeautifulSoup

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Create PicklePersistence object
pp = PicklePersistence(filename='u_data.pickle', on_flush=True)

def start(update, context):
	start_msg = "*Benvenuto a* @UnipgSolBot.\n"\
		"Questo bot ti permetterà di visualizzare gli appelli disponibili e quelli a cui ti sei già iscritto sulla piattaforma SOL Unipg.\n"\
        "Ti permetterà inoltre di iscriverti a nuovi appelli se disponibili\n\n"\
        "Per visualizzare i comandi disponibili utilizza /help\n\n"\
		"NOTA: _Questo bot non è reallizzato ufficialmente, pertanto né Unipg né Cineca sono da considerarsi responsabili di questo bot in alcun modo._"

	update.message.reply_markdown(start_msg, reply_markup=ReplyKeyboardRemove())
	pp.flush()

def help(update, context):
	help_msg = "Ecco una lista dei *comandi* attualmente disponibili su questo bot:\n\n"\
        "- /help: Visualizza questo messaggio\n"\
        "- /cancel: Interrompe il comando attualmente in esecuzione\n"\
        "- /login: Effettua il Login sul portale SOL chiedendo le credenziali\n"\
        "- /logout: Cancella ogni dato personale raccolto dal Bot, compresa la sessione corrente ed effettuando quindi il Logout dal portale\n"\
        "- /booked: Visualizza gli esami a cui sei iscritto\n"\
        "- /exams: Visualizza gli esami disponibili e ti permette eventualmente di iscriverti\n"

	update.message.reply_markdown(help_msg)

def login(update, context):
	send_user_pwd = 'Inserisci il tuo *username* e la tua *password* nel seguente formato:\n\n'\
                    'username:password\n\n'\
                    '_Si ricorda che il bot cancellerà immediatamente il messaggio inviato non appena sarà stato effettuato il login, per questioni di Privacy._'

	update.message.reply_markdown(send_user_pwd)
	return 1

def login_handler(update, context):
	# Save credentials
	context.user_data['credentials'] = {}

    # Getting username and password from message's text
	user_pass = update.message.text.split(':')

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
	soup = BeautifulSoup(main_page.text, features='lxml')
	name = soup.body.find('div', attrs={'class':'masthead_usermenu_user_name'}).text
	update.message.reply_markdown("Sono riuscito a collegarmi, benvenuto *%s*!" % name)

	# Update pickle file
	pp.flush()

	return ConversationHandler.END

def view_enrolled_exams(update, context):
    # Verifica che l'utente abbia effettuato l'accesso
    response = sol.connect(context.user_data)
    if response != "OK":
        update.message.reply_markdown(response, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # Prende una stringa e una lista utilizzando una funzione di sol_framework
    booked, id = sol.getEnrolledExams(context.user_data)
    update.message.reply_markdown('Ecco gli appelli a cui sei iscritto:\n\n%s' %sol.escape(booked))

    # Crea la tastiera per l'utente
    keyboard = [['No']]
    for i in range(1,id+1):
        keyboard.append([str(i)])

    update.message.reply_markdown(
        'Vuoi rimuovere una prenotazione?\n'\
        'Seleziona l\'ID della prenotazione da eliminare',
        reply_markup=ReplyKeyboardMarkup(keyboard))
    return 1

def remove_booking(update, context):
    context.user_data['choice'] = update.message.text
    if context.user_data['choice'] == 'No':
        update.message.reply_markdown('Nessuna prenotazione rimossa', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        response = sol.unbookExam(context.user_data)
        if response != 'OK':
            update.message.reply_markdown(response, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        update.message.reply_markdown('Operazione teriminata con successo', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

def view_exams(update, context):
    # Verifica che l'utente abbia effettuato l'accesso
    response = sol.connect(context.user_data)
    if response != "OK":
        update.message.reply_markdown(response, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    # Inizializza Inline Keyboard
    keyboard = [[ "Visualizza", "Iscriviti" ]]
    view_msg = "Vuoi solo visualizzare gli appelli disponibili o vuoi anche iscriverti?\n"#\
        #"_Puoi interrompere qualunque comando in esecuzione con il comando /cancel_\n"
    update.message.reply_text(view_msg, reply_markup=ReplyKeyboardMarkup(keyboard))
    return 1

def choice_handler(update, context):
    answer = update.message.text
    if answer == 'Iscriviti':
        # Esegue la funzione di sol_framework
        exams, linksDict = sol.getExams(context.user_data)
        # Inizializza la tastiera per la selezione degli appelli
        keyboard = [['%s' %i] for i in linksDict.keys()]
        text = 'Ecco gli appelli disponibili:\n'\
            'Quelli a cui puoi iscriverti sono segnati con %s, quelli a cui non puoi con %s \n\n%s\n'\
            'Gli appelli disponibili sono segnati con un numero.\n'\
            'Seleziona il numero dell\'appello a cui vuoi iscriverti \n' %(type_to_sym['Prenotazione'], type_to_sym['Vietato'], sol.escape(exams))
        update.message.reply_markdown(text, reply_markup=ReplyKeyboardMarkup(keyboard))
        return 2
    else:
        exams, linksDict = sol.getExams(context.user_data)
        update.message.reply_markdown(f'Ecco gli appelli disponbili:\n\n{sol.escape(exams)}', reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

def enroll_exam_handler(update, context):
        exam_id = update.message.text
        # Effettua l'iscrizione all'esame
        exams, linksDict = sol.getExams(context.user_data)
        result = sol.enrollToExam(context.user_data, linksDict[exam_id])
        if result != "OK":
            update.message.reply_markdown(result, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        else:
            update.message.reply_markdown('Prenotazione effettuata con successo', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

def logout(update, context):
    # Delete all
    for key in list(context.user_data):  # Using a list to prevent RuntimeError, since user_data could change during iterations
        del context.user_data[key]

    # Update pickle file
    pp.flush()

    # Notification message
    update.message.reply_markdown("Tutti i dati che erano presenti sono stati rimossi con successo.\n\n")
    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def cancel(update, context):
    # Undo any command which is going on
    update.message.reply_text('Ok, comando annullato.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    # Create EventHandler with bot's token
    updater = Updater(TOKEN, persistence=pp, use_context=True)
    dp = updater.dispatcher

	# Adding all the Handlers for the commands
    cmd_login = ConversationHandler(
        entry_points=[CommandHandler('login', login)],

        states={
            1: [MessageHandler(Filters.text, login_handler)]
        },

        fallbacks=[CommandHandler('cancel', cancel)])

    cmd_view_exams = ConversationHandler(
        entry_points=[CommandHandler('exams', view_exams)],

        states={
            1: [MessageHandler(Filters.text, choice_handler)],

            2: [MessageHandler(Filters.text, enroll_exam_handler)]
        },

        fallbacks=[CommandHandler('cancel', cancel)])

    cmd_booked_exams = ConversationHandler(
        entry_points=[CommandHandler('booked', view_enrolled_exams)],

        states={
            1: [MessageHandler(Filters.text, remove_booking)]
        },

        fallbacks=[CommandHandler('cancel', cancel)])

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('logout', logout))
    dp.add_handler(CommandHandler('cancel', cancel))
    dp.add_handler(cmd_booked_exams)
    dp.add_handler(cmd_login)
    dp.add_handler(cmd_view_exams)

    # Log all errors
    dp.add_error_handler(error)
    # Starts the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()

if __name__=='__main__':
	main()
