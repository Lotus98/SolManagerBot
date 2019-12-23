"""
Functions to communicate with SOL platform
"""
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style
from settings import LOGIN_URL, MAIN_URL, HOME_URL

def connect(user_data):
    if 'session' not in user_data:
        user_data['session'] = requests.Session()

    # Getting credentials if available
    try:
        auth = (user_data['credentials']['username'], user_data['credentials']['password'])
    except KeyError:
        return "Non hai effettuato ancora il login, effettualo tramite il comando /login."

    # Check if server is alive
    status_code = requests.head(HOME_URL).status_code
    if status_code != 200:
        print(Fore.RED + "[CONNECTION] Server irraggiungibile. Status code: " + str(status_code))
        return "Non riesco a contattare il server (CODE: %d), riprova più tardi..." % status_code

    # Check if the login is still valid (without performing a login)
    if user_data['session'].head(MAIN_URL).status_code == 200:
        return "OK"

    # Perform the login
    user_data['session'].get(LOGIN_URL)
    if user_data['session'].get(LOGIN_URL, auth=auth).url != MAIN_URL:
        return "Le credenziali fornite non sono valide. Riprova."
    return "OK"
