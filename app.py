import os
import psycopg2
from flask import Flask, render_template

app = Flask(__name__)

# OBTENER LA URL DE CONEXIÓN
# --------------------------------------------------------------------------------
# Durante el desarrollo local, usa tu URL literal (la que Render te dio).
# Cuando despliegues en Render, Render usará automáticamente la variable de entorno
# 'DATABASE_URL' que ellos configuran.
# ¡REEMPLAZA ESTA URL CON LA TUYA!
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://smartbooks_db_duns_user:K6VQR41ddpegEb1TCRTlXODv407vkU5J@dpg-d3lk7jp5pdvs73aio4eg-a.oregon-postgres.render.com/smartbooks_db_duns"
)
# --------------------------------------------------------------------------------


def get_db_data():
    """Conecta a la DB, obtiene los datos clave-valor y los devuelve como un diccionario."""
    conn = None
    data = {}
    try:
        # Usa sslmode='require' para conexiones a Render
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        
        # Consulta para obtener todas las claves y valores
        cur.execute("SELECT clave, valor FROM configuracion_web;")
        
        # Convierte los resultados en un diccionario {clave: valor}
        # Esto hace que sea fácil usar en la plantilla HTML
        results = cur.fetchall()
        data = {row[0]: row[1] for row in results}
        
        cur.close()
    except Exception as e:
        print(f"Error al conectar o consultar la base de datos: {e}")
        # En producción, podrías retornar una página de error, pero aquí solo imprimimos.
        # Devuelve un diccionario vacío si falla la conexión.
    finally:
        if conn is not None:
            conn.close()
    return data

@app.route('/')
def index():
    # 1. Obtener todos los datos de la base de datos
    context = get_db_data()

    # 2. Renderizar la plantilla HTML, pasando el diccionario 'context'
    return render_template('index.html', **context)

if __name__ == '__main__':
    # Asegúrate de usar un puerto que no esté en uso. 8000 es común para desarrollo.
    app.run(debug=True, port=8000)