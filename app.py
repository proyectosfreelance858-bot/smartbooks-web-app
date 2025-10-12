import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv 

# Cargar variables de entorno del archivo .env (solo local)
load_dotenv() 

app = Flask(__name__)

# OBTENER LA URL DE CONEXIÓN
DATABASE_URL = os.environ.get("DATABASE_URL") 

# =========================================================
#  AQUÍ DEBE ESTAR DEFINIDA LA FUNCIÓN get_db_data()
# =========================================================
def get_db_data():
    """Conecta a la DB, obtiene los datos clave-valor y los devuelve como un diccionario."""
    conn = None
    data = {}
    try:
        # Usa sslmode='require' para conexiones a Render
        # Asegúrate de que DATABASE_URL NO esté vacía
        if not DATABASE_URL:
            print("ERROR: DATABASE_URL no está configurada.")
            return {}
            
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        
        # Consulta para obtener todas las claves y valores
        cur.execute("SELECT clave, valor FROM configuracion_web;")
        
        # Convierte los resultados en un diccionario {clave: valor}
        results = cur.fetchall()
        data = {row[0]: row[1] for row in results}
        
        cur.close()
    except Exception as e:
        # Esto capturará errores de conexión o de sintaxis SQL
        print(f"Error al conectar o consultar la base de datos: {e}")
    finally:
        if conn is not None:
            conn.close()
    return data

# =========================================================
#  La ruta 'index' llama a la función de arriba
# =========================================================
@app.route('/')
def index():
    # Línea 23, donde ocurre el error si la función no está arriba
    context = get_db_data() 
    return render_template('index.html', **context)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)