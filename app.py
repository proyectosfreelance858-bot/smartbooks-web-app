import os
from flask import Flask, render_template
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env (útil para desarrollo local)
load_dotenv()

# =================================================================
# ATENCIÓN: CONFIGURACIÓN DE BASE DE DATOS
# ESTO DEBE SER REEMPLAZADO CON TUS CREDENCIALES REALES O VARIABLES DE ENTORNO
# =================================================================
# La mejor práctica es usar variables de entorno (Render/Heroku/etc. las usan).
# Si no las encuentra en el entorno, usa los valores por defecto (ej. "localhost").

DB_HOST = os.environ.get("DB_HOST", "localhost") 
DB_NAME = os.environ.get("DB_NAME", "nombre_de_tu_base_de_datos") 
DB_USER = os.environ.get("DB_USER", "tu_usuario_postgres") 
DB_PASS = os.environ.get("DB_PASS", "tu_contraseña_postgres") 

# El puerto de Render/hosting se obtiene de la variable 'PORT'
PORT = int(os.environ.get('PORT', 5000))
HOST = '0.0.0.0' 

app = Flask(__name__)

def get_db_connection():
    """Establece la conexión a la base de datos PostgreSQL."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

@app.route('/')
def index():
    blogs = []
    conn = None
    
    # --- 1. CONEXIÓN Y CONSULTA A LA BASE DE DATOS (CON MANEJO DE ERRORES) ---
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Consulta para obtener los 7 artículos del blog más recientes por fecha
        sql_query = """
            SELECT 
                id, 
                titulo, 
                descripcion_corta, 
                url_imagen_principal, 
                fecha_creacion, 
                slug 
            FROM 
                articulos_blog 
            ORDER BY 
                fecha_creacion DESC 
            LIMIT 7;
        """
        cur.execute(sql_query)
        db_blogs = cur.fetchall()
        
        # Formatear los datos obtenidos para la plantilla Jinja2
        for blog_data in db_blogs:
            (id, titulo, descripcion_corta, url_imagen_principal, fecha_creacion, slug) = blog_data
            
            # Formateo de Fecha: '01 Oct, 2025' y traducción de meses
            fecha_formateada = fecha_creacion.strftime("%d %b, %Y")
            meses_espanol = {'Jan': 'Ene', 'Apr': 'Abr', 'Aug': 'Ago', 'Dec': 'Dic'}
            for en, es in meses_espanol.items():
                fecha_formateada = fecha_formateada.replace(en, es)
            
            # Construcción del diccionario 'blog' 
            blogs.append({
                'id': id,
                'titulo': titulo,
                # IMPORTANTE: Los blogs que no tienen URL de imagen fallarán. 
                # Aquí verificamos si la URL es nula y usamos una por defecto.
                'url_imagen_principal': url_imagen_principal if url_imagen_principal else 'https://via.placeholder.com/600x400.png?text=Smart+Books+Blog',
                'descripcion_corta': descripcion_corta,
                'fecha': fecha_formateada,
                'autor': 'Smart Books Team',     
                'categoria': 'Educación',        
                'url_articulo': f'/blog/{slug}'  
            })

        cur.close()

    except psycopg2.Error as e:
        # Si la conexión falla, imprimimos un mensaje claro y dejamos 'blogs' vacío
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR CRÍTICO DE CONEXIÓN A LA BASE DE DATOS: {e}")
        print(f"Revisa las credenciales (DB_HOST, DB_NAME, DB_USER, DB_PASS).")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    except Exception as e:
        print(f"Error inesperado durante la consulta: {e}")
    finally:
        if conn:
            conn.close()

    # --- 2. CONTEXTO DE VARIABLES PARA LA PLANTILLA ---
    context = {
        # Variables anteriores para el Carrusel (compatibilidad con index.html)
        'url_banner1': 'https://images.unsplash.com/photo-1543269664-56b93a02a768?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 
        'url_banner2': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 
        
        # Variable que alimenta la sección del Blog
        'blogs': blogs
    }

    return render_template('index.html', **context)

if __name__ == '__main__':
    # Ejecuta el servidor escuchando en 0.0.0.0 y usando la variable PORT
    app.run(host=HOST, port=PORT, debug=True)