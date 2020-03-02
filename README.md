# sitoGad
Come caricare i file nel sito curve Gad


Nel file routes.py vanno aggiunti nelle seguenti righe le info richieste

    MYSQL_USER = 'your_user'
    MYSQL_PASSWORD = 'your_pass'
    MYSQL_HOST_IP = 'your_host'
    MYSQL_PORT = 'port'
    database = 'db_name'
    
presenti nel file routes.py nella funzione connesione_db.


Inoltre andranno creati i due file .env e .flaskenv: nel primo andrà inserita la chiave segreta, nel secondo il FLASK_ENV


