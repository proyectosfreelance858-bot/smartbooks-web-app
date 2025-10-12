import os
import psycopg2
from flask import Flask, render_template

# Librería para cargar el archivo .env (necesitarás instalarla localmente)
from dotenv import load_dotenv 

# Cargar variables de entorno del archivo .env
# Esto solo funciona cuando ejecutas 'python app.py' en tu máquina local.
load_dotenv() 

app = Flask(__name__)

# OBTENER LA URL DE CONEXIÓN
# Cuando está en Render, lee el env de Render. Localmente, lee del .env.
DATABASE_URL = os.environ.get("DATABASE_URL") 
# -----------------------------------------------------------------------------

# ... (El resto de la función get_db_data y la ruta index es la misma) ...

@app.route('/')
def index():
    context = get_db_data()
    return render_template('index.html', **context)

if __name__ == '__main__':
    # Usaremos el puerto 10000, el puerto por defecto de Render.
    # No es estrictamente necesario, pero es bueno acostumbrarse.
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
