# il file segue la convenzione della PEP8 di Python:
# - le costanti sono tutte in maiuscolo
# - scrivo in ordine: librerie esterne, librerie mie, costanti e funzioni globali, il resto

# importo le librerie
import os
import math
import datetime as dt
from collections import Counter

import pandas as pd

from flask import render_template, request, flash, redirect, url_for
from flask_optimize import FlaskOptimize

from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import NumeralTickFormatter, ColumnDataSource, Span, Range1d
from bokeh.models.tools import HoverTool

import mysql.connector
from sqlalchemy import create_engine

# carico l'app
from app import app

# ottimizzo alcuni processi di flask
flask_optimize = FlaskOptimize()

# dizionario filtro-colore
COLORE_FILTRO = {'Cl': 'black', 'Clear': 'black', 'Rc': 'red',
                 'V': 'green', 'B': 'blue', 'Ha': 'purple',
                 'Halfa': 'purple', 'R': 'red',
                 'unfiltered': 'black', 'Ir': 'coral'}

def connessione_db(stringa):
    MYSQL_USER = 'your_user'
    MYSQL_PASSWORD = 'your_pass'
    MYSQL_HOST_IP = 'your_host'
    MYSQL_PORT = 'port'
    database = 'db_name'

    # ====== Connection ====== #
    # Connecting to mysql by providing a sqlachemy engine
    engine = create_engine('mysql+mysqlconnector://'+MYSQL_USER+':'+MYSQL_PASSWORD+'@'+MYSQL_HOST_IP+':'+MYSQL_PORT+'/' + database, echo=False).connect()

    data = pd.read_sql(stringa, engine)

    data.header=None

    data = data.reset_index()

    return data


# creo la home del sito
@app.route("/")
@flask_optimize.optimize()
def homepage():

    return render_template("home.html")


# pagina elenco per grafico: la riga state = ... serve per poter leggere dall'html
# il nome della stella scelta
@app.route("/elenco", methods=['GET', 'POST'])
def elenco():
    df_obs = connessione_db('SELECT rilevazioni.filtro,rilevazioni.jd, \
                            rilevazioni.magnitudine,rilevazioni.osservatore, \
                            rilevazioni.stella FROM rilevazioni')
    df_eff = connessione_db('SELECT effemeridi.stella, effemeridi.periodo,\
                            effemeridi.epoca FROM effemeridi')

    LISTA = df_obs['stella'].to_list()

    STAR = sorted(set(LISTA))

    state = {'choice': "selected"}

    if request.method == "POST":
        choice = request.form["star"]

        if choice == '0':

            flash('Oggetto non selezionato')
            return redirect(url_for('elenco'))

        else:
            if request.form['btn'] == 'Grafica osservazioni':

                df_int = df_obs[df_obs.loc[:,'stella']==choice]
                dati = df_int[['filtro','jd','magnitudine','osservatore']]

                script, div = grafico(dati,df_eff, choice)

                return render_template('grafico.html', script=script, div=div)

    return render_template("elenco.html", state=state, star=STAR)


# pagina grafico: genero gli script per l'html
@app.route("/grafico")
def grafico(lista_dati,df_eff,choice):

    lista_dati['jd'] = pd.to_numeric(lista_dati['jd'],errors='coerce')
    lista_dati['magnitudine'] = pd.to_numeric(lista_dati['magnitudine'],errors='coerce')

    p = figure(plot_width=1920, plot_height=1080, sizing_mode='scale_both',
               tools=['box_zoom,save,hover,reset,wheel_zoom'],
               output_backend="webgl")

    elenco_filtro=lista_dati['filtro'].to_list()


    set_filtro = set(elenco_filtro)

    p.xaxis.formatter = NumeralTickFormatter(format="0.00")

    #source = ColumnDataSource(lista_dati)
    i=0

    while i < len(set_filtro):

        filtro_sel = list(set_filtro)[i]

        dati = lista_dati[lista_dati['filtro']==filtro_sel]
        source = ColumnDataSource(dati)

        p.asterisk(x='jd', y='magnitudine', size=4, source=source,
                       color=COLORE_FILTRO.get(filtro_sel, 'black'),
                       legend_label=list(set_filtro)[i])

        intest = list(dati.columns.values)

        t = pd.to_numeric(lista_dati[intest[1]])

        for item in range(len(df_eff)):
                # se la stella ha effemeridi

                if (df_eff.loc[item]['stella'] == choice):

                    epocaP = float(df_eff.loc[item]['epoca'])
                    periodo = float(df_eff.loc[item]['periodo'])
                    numoss = 1

                    # cerca il giorno in cui c'è l'osservazione
                    for i in range(len(t)):
                        while ((numoss*periodo)+epocaP) < (t.iloc[i]):
                            numoss = numoss + 1
                            # nel giorno in cui c'è l'osservazione
                            if int(t.iloc[i]) == int(epocaP + numoss*periodo) or \
                                int(t.iloc[i]) == (int(epocaP + numoss*periodo)+1):
                                # disegna la riga del minimo
                                eff_primario = (epocaP + (numoss*periodo))
                                eff_secondario = 1+(epocaP + (numoss * periodo))

                                line = Span(location=eff_primario,
                                            dimension='height',
                                            line_dash='dashed',
                                            line_color='red',
                                            line_width=1)

                                line2 = Span(location=eff_secondario,
                                             dimension='height',
                                             line_dash='dashed',
                                            line_color='green',
                                             line_width=0.8)

                                p.add_layout(line)
                                p.add_layout(line2)

        i+=1

    p.y_range.flipped = True

    ColumnDataSource(lista_dati)
    # genero i dati da visualizzare quando passo col mouse
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [("Data [JD]", "@jd{0.00000}"),
                              ("Magnitudine", "@magnitudine{0.0000}"),
                              ("Osservatore", "@osservatore"), ]
    hover.mode = 'mouse'

    titolo = choice
    p.title.text = titolo
    p.title.align = "center"
    p.title.text_font_size = "21px"

    p.xaxis.axis_label = 'Data [JD]'
    p.yaxis.axis_label = 'Magnitudine'

    p.legend.location = "top_left"
    p.legend.orientation = 'horizontal'
    p.legend.click_policy = "hide"

    script, div = components(p)

    return script, div


# pagina about
@app.route("/about_project")
@flask_optimize.optimize()
def about_project():
    return render_template("about_project.html")


# pagina tabella: genera un dataframe che passo all'html
@app.route("/tabella")
@flask_optimize.optimize()
def tabella():

    df = connessione_db('SELECT rilevazioni.file FROM rilevazioni')

    LISTA = [file.split('_')[0] for file in list(set(df['file'].to_list()))]

    d = Counter(LISTA)
    tab = pd.DataFrame(d.items(), columns=['obj', '#'])

    LISTA_BLAZAR=['BL Lac','2344+514','2230+114','3C 454']

    date = [str(dt.datetime.strptime(file.split('_')[1],'%Y%m%d').date()) for file in df['file']]

    tipo = ["Blazar" if nome in LISTA_BLAZAR else "Variabile" for nome in tab['obj']]

    tab['tipo'] = tipo

    tab.sort_values(by=['#','obj'], inplace=True, ascending=[False,True])

    lista_dati = tab.values.tolist()

    tot_obj = len(tab)
    tot_obs = len(LISTA)
    last_obs = max(date)

    return render_template('tabella.html', lista = lista_dati,
                            tot_obj = tot_obj,tot_obs = tot_obs, last_obs=last_obs)
