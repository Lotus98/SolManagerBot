[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

**Sol Manager** è un bot Telegram che permette agli studenti dell'Università di Perugia di interagire in maniera facile e intuitiva con la piattaforma [SOL](https://unipg.esse3.cineca.it/Home.do)

***

## Funzionalità

Attualmente sono disponbili le seguenti funzionalità:
* Visualizzazione e rimozione degli appelli prenotati
* Visualizzazione e iscrizione agli appelli disponibili

*Ulteriori funzionalità verranno aggiunte in futuro*

---
## Installazione

Il bot viene rilasciato con licenza MIT. Per cui chiunque può contribuire alle modifiche e nuove implementazioni, tramite Github.

Per utilizzare correttamente la repository, dopo averla clonata, eseguire i seguenti comandi per installare le dipendenze di python necessarie:
```bash
sudo pip3 install python-telegram-bot
sudo pip3 install bs4
```

Dopodiché sarà necessario rinominare il file:
* ``settins_git.py`` in ``settings.py``

Infine sarà necessario modificare il file ``settings.py`` inserendo il token del proprio bot nella variabile ``TOKEN``

---

## Utilizzo

L'utilizzo è semplicissimo, basterà eseguire il seguente comando:
```bash
python3 main.py
```

---
Il presente bot è stato realizzato tramite l'utilizzo di [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

È inoltre da considerarsi totalmente **non ufficiale**, né *Cineca* né *Unipg* sono responsabili in alcun modo.

*This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it.*
