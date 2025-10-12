import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv 

# Cargar variables de entorno del archivo .env para desarrollo local
load_dotenv() 

app = Flask(__name__)

# OBTENER LA URL DE CONEXIÓN
# En Render, esto leerá la variable configurada en la Interfaz.
# Localmente, leerá del .env
DATABASE_URL = os.environ.get("DATABASE_URL") 


# =========================================================
# FUNCIÓN DE CONEXIÓN Y OBTENCIÓN DE DATOS
# =========================================================
def get_db_data():
    """Conecta a la DB, obtiene los datos clave-valor y los devuelve como un diccionario."""
    conn = None
    data = {}
    
    # Datos de respaldo si la conexión falla (opcional, pero útil)
    # Aquí podrías poner valores por defecto para evitar errores si la DB está caída
    default_data = {
        "url_banner1": "URL_NO_CARGADA",
        "url_editorial1": "URL_NO_CARGADA",
        "txt_productosmasvendidos1": "PRODUCTO NO DISPONIBLE"
    }

    try:
        if not DATABASE_URL:
            print("ERROR: DATABASE_URL no está configurada.")
            return default_data
            
        # Conexión a PostgreSQL (Render requiere sslmode='require')
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        
        # Consulta para obtener todas las claves y valores
        cur.execute("SELECT clave, valor FROM configuracion_web;")
        
        # Convierte los resultados en un diccionario {clave: valor}
        results = cur.fetchall()
        data = {row[0]: row[1] for row in results}
        
        cur.close()
    except Exception as e:
        print(f"Error al conectar o consultar la base de datos: {e}")
        # Si la conexión falla, devuelve los datos de respaldo
        data = default_data
    finally:
        if conn is not None:
            conn.close()
    return data


# =========================================================
# RUTAS DE FLASK
# =========================================================

@app.route('/')
def index():
    # Obtiene todos los datos de la DB
    context = get_db_data()
    
    # Renderiza la plantilla hija 'home.html'
    return render_template('home.html', **context)

# Puedes añadir más rutas aquí
# @app.route('/productos')
# def productos():
#     context = get_db_data()
#     # Aquí podrías usar una plantilla llamada 'productos.html'
#     return render_template('productos.html', **context)


if __name__ == '__main__':
    # Configuración para que funcione en el puerto dinámico de Render
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)