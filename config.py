# il file segue la convenzione della PEP8 di Python:
# - le costanti sono tutte in maiuscolo
# - scrivo in ordine: librerie esterne, librerie mie, costanti e funzioni globali, il resto

# file di configurazione dell'app

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
load_dotenv(os.path.join(basedir, '.flaskenv'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
