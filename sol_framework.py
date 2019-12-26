"""
Functions to communicate with SOL platform
"""
import requests
from bs4 import BeautifulSoup
from settings import *

def connect(user_data):
    if 'session' not in user_data:
        user_data['session'] = requests.Session()

    # Getting credentials if available
    try:
        user_data['session'].auth = (user_data['credentials']['username'], user_data['credentials']['password'])
    except KeyError:
        return "Non hai effettuato ancora il login, effettualo tramite il comando /login."

    # Check if server is alive
    status_code = requests.head(HOME_URL).status_code
    if status_code != 200:
        print("[CONNECTION] Server irraggiungibile. Status code: " + str(status_code))
        return "Non riesco a contattare il server (CODE: %d), riprova più tardi..." % status_code

    # Check if the login is still valid (without performing a login)
    if user_data['session'].head(MAIN_URL).status_code == 200:
        return "OK"

    # Perform the login
    if user_data['session'].get(LOGIN_URL).url != MAIN_URL:
        return "Le credenziali fornite non sono valide. Riprova."
    return "OK"

def getEnrolledExams(user_data):
    # Gets the hmtl page with the data
    response = user_data['session'].get(ENROLLED_EXAMS_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    booked = soup.body.find_all('table', class_='detail_table')

    # Parsing data, creating a list with final output
    out = []
    for i in range(len(booked)):
        temp=[]
        for j in booked[i].get_text().split('\n'):
            if j!='':
                temp.append(j+'\n')
        out.extend((temp[0], temp[-1]))

    for i in range(len(out)):
        if i%2:
            out[i]='Data: ' + ' '.join([out[i][:10], 'Ora:', out[i][10:15]]) + '\n\n'
        else:
            out[i]=type_to_sym['Prenotazione']+out[i]

    result = ''
    for i in out:
        result += i
    return result

def getExams(user_data):
    # Gets the hmtl page with the data
    response = user_data['session'].get(EXAMS_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    exams = soup.body.table('td')

    # Parsing data and creating an element in a list for each exam
    exams = [exams[6*i:6*(i+1)]  for i in range(int(len(exams)/6))]

    result=''
    linksList=[]
    count=0
    for i in exams:
        if(i[0].div):
            count+=1
            linksList.append(i[0].div.a['href'])
            result+=str(count)+' '+type_to_sym['Prenotazione']
        else:
            result+=type_to_sym['Vietato']
        for j in range(1,5):
            result+=('', i[j].get_text()+' ')[j==1]
            result+=('', 'Data: '+i[j].get_text())[j==2]
            result+=('', 'Iscrizioni dal: '+i[j].get_text()[0:10]+' al: '+i[j].get_text()[10:20])[j==3]
            result+=('', '\nDescrizione: '+ i[j].get_text())[j==4]
        result+='\n\n'

    return result, linksList

def enrollToExam(user_data, link):
    # Funzione per realizzare la registrazione ad un appello
    response = user_data['session'].get(BASE_URL+link)
    soup = BeautifulSoup(response.text, features='lxml')
    params = soup.body.form('input')
    en_link = soup.body.form['action']
    payload = {i['name']:i['value'] for i in params}
    enroll = user_data['session'].post(BASE_URL+en_link, data=payload)
    soup2 = BeautifulSoup(enroll.text)
    res = soup2.body('p', class_="app-text_esito_pren_msg-esito_pren")
    if res == 'PRENOTAZIONE EFFETTUATA\n':
        return 'OK'
    else:
        return 'ERROR - La prenotazione *non* è stata effettuata con successo, riprova più tardi'
