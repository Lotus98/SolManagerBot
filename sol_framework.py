"""
Functions to communicate with SOL platform
"""
import requests
from bs4 import BeautifulSoup
from settings import *

def escape(s):
    s = s.replace('_','\_')
    s = s.replace('*','\*')
    return s

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
    booked = soup.body('table', class_='detail_table')

    # Parsing data, creating a list with final output
    out = []
    count = 0
    for i in booked:
        count += 1
        temp=['ID: %s ' %str(count)]
        for j in i.get_text().split('\n'):
            if j!='':
                temp.append(j+'\n')
        out.extend((temp[0], temp[1], temp[-1]))
    cnt = 1
    for i in range(len(out)):
        if cnt == 3 :
            out[i]='Data: ' + ' '.join([out[i][:10], 'Ora:', out[i][10:15]]) + '\n\n'
            cnt = 0
        elif cnt == 2 :
            out[i]=type_to_sym['Prenotazione']+out[i]
        cnt += 1
    result = ''
    for i in out:
        result += i
    return result, count

def getExams(user_data):
    # Gets the hmtl page with the data
    response = user_data['session'].get(EXAMS_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    exams = soup.body.table('td')

    # Parsing data and creating an element in a list for each exam
    exams = [exams[6*i:6*(i+1)]  for i in range(int(len(exams)/6))]

    result=''
    linksDict={}
    count=0
    for i in exams:
        if(i[0].div):
            count+=1
            linksDict[str(count)] = i[0].div.a['href']
            result+='ID: '+str(count)+' '+type_to_sym['Prenotazione']
        else:
            result+=type_to_sym['Vietato']
        for j in range(1,5):
            result+=('', i[j].get_text()+' ')[j==1]
            result+=('', 'Data: '+i[j].get_text())[j==2]
            result+=('', 'Iscrizioni dal: '+i[j].get_text()[0:10]+' al: '+i[j].get_text()[10:20])[j==3]
            result+=('', '\nDescrizione: '+ i[j].get_text())[j==4]
        result+='\n\n'
    return result, linksDict

def enrollToExam(user_data, link):
    # Funzione per realizzare la registrazione ad un appello
    response = user_data['session'].get(BASE_URL+link)
    soup = BeautifulSoup(response.text, features='lxml')
    # Recupera il link al quale effettuare la richiesta POST
    en_link = soup.body.form['action']
    # Crea il payload da passare per la richiesta POST
    params = soup.body.form('input')
    payload = {i['name']:i['value'] for i in params}
    # Effettua l'iscrizione all'appello
    enroll = user_data['session'].post(BASE_URL+en_link, data=payload)
    # Verifica se l'operazione è andata a buon fine --> DA RICONTROLLARE
    soup2 = BeautifulSoup(enroll.text, features='lxml')
    res = soup2.body('p', class_="app-text_esito_pren_msg-esito_pren")
    if res[0].get_text() == 'PRENOTAZIONE EFFETTUATA\n':
        return 'OK'
    else:
        return 'ERROR - La prenotazione *non* è stata effettuata con successo. Riprova più tardi'

def unbookExam(user_data):
    # Gets the hmtl page with the data
    response = user_data['session'].get(ENROLLED_EXAMS_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    booked = soup.body('table', class_='detail_table')

    choice = user_data['choice']
    # Collects link and payload to forge the POST request
    linksDict={}
    count = 0
    for i in booked:
        count += 1
        tmp = i('td', attrs={'title':'cancella la prenotazione'})
        if tmp != []:
            linksDict[str(count)] = { 'link':tmp[0].form['action'], 'payload':{i['name']:i['value'] for i in tmp[0]('input', attrs={'type':'hidden'})} }
        else:
            linksDict[str(count)] = ''
    if linksDict[choice]== '':
        return 'Non è possibile rimuovere questa prenotazione'
    unbook = user_data['session'].post(BASE_URL+linksDict[choice]['link'], data=linksDict[choice]['payload'])
    soup2 = BeautifulSoup(unbook.text, features='lxml')

    link = soup2.table.form['action']
    payload = {}
    for i in soup2.table.form.table('input'):
        if i['name'] != '':
            payload.update({i['name']:i['value']})

    if user_data['session'].post(BASE_URL+link, data=payload).url != ENROLLED_EXAMS_URL :
        return 'L\'operazione non è andata a buon fine. Riprova più tardi'
    req = user_data['session'].post(BASE_URL+link, data=payload)

    return 'OK'
