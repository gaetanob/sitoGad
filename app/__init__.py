# il file segue la convenzione della PEP8 di Python:
# - le costanti sono tutte in maiuscolo
# - scrivo in ordine: librerie esterne, librerie mie, costanti e funzioni globali, il resto

# in questa pagina carico l'app e ne cancello la cache ogni volta che viene riavviata
# ottimizzando molti processi

from flask import Flask
from config import Config

app = Flask(__name__)
app.secret_key = '26cf84ceb41c4fe5af8f2a957a03886a'
app.config.from_object(Config)

from app import routes
from jinja2.environment import create_cache
from flask_optimize import FlaskOptimize

app.jinja_env.cache = {}
flask_optimize = FlaskOptimize()