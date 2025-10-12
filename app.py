import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv 

# Cargar variables de entorno del archivo .env (SOLO PARA DESARROLLO LOCAL)
# Render ignora esto y usa la configuración de su interfaz.
load_dotenv() 

app = Flask(__name__)

# OBTENER LA URL DE CONEXIÓN
# Obtiene la variable de entorno ya sea de Render (Producción) o de .env (Local)
DATABASE_URL = os.environ.get("DATABASE_URL") 


# =========================================================
# FUNCIÓN DE CONEXIÓN Y OBTENCIÓN DE DATOS
# =========================================================
def get_db_data():
    """Conecta a la DB, obtiene los datos clave-valor y los devuelve como un diccionario."""
    conn = None
    data = {}
    
    # Valores de respaldo para evitar fallos si la DB está inaccesible
    default_data = {
        "url_banner1": "https://via.placeholder.com/800x200?text=Banner+No+Cargado",
        "url_banner2": "https://via.placeholder.com/800x200?text=Banner+No+Cargado",
        "url_editorial1": "https://via.placeholder.com/50x20?text=E1",
        "url_editorial2": "https://via.placeholder.com/50x20?text=E2",
        "txt_productosmasvendidos1": "Producto Default 1",
        "url_productosmasvendidos1": "https://via.placeholder.com/150",
        "txt_productosmasvendidos2": "Producto Default 2",
        "url_productosmasvendidos2": "https://via.placeholder.com/150",
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
    # 1. Obtiene todos los datos de la DB
    context = get_db_data()
    
    # 2. Renderiza la plantilla hija 'home.html' (que extiende 'layout.html')
    return render_template('home.html', **context)


if __name__ == '__main__':
    # Configuración para que funcione en el puerto dinámico de Render
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)