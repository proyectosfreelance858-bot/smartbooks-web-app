import os
from flask import Flask, render_template
import psycopg2
from datetime import datetime
from dotenv import load_dotenv # <-- Importar dotenv

# Cargar las variables de entorno desde el archivo .env
# Esto hace que DB_HOST, DB_NAME, DB_USER, DB_PASS estén disponibles
load_dotenv()

# =================================================================
# 1. CONFIGURACIÓN DE BASE DE DATOS Y HOSTING
# Obtiene las credenciales de las variables de entorno (Render/Hosting/.env)
# =================================================================
# Ahora lee directamente de las variables de entorno (cargadas por load_dotenv() o por el hosting)
DB_HOST = os.environ.get("DB_HOST") 
DB_NAME = os.environ.get("DB_NAME") 
DB_USER = os.environ.get("DB_USER") 
DB_PASS = os.environ.get("DB_PASS") 
# DB_PORT no es necesario por defecto, psycopg2 lo maneja

# Configuración de puerto y host para Render
PORT = int(os.environ.get('PORT', 5000))
HOST = '0.0.0.0' 

app = Flask(__name__)

def get_db_connection():
    """Intenta establecer la conexión a la base de datos PostgreSQL."""
    # Se añade un chequeo simple para no fallar en psycopg2 con None
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS]):
         raise psycopg2.OperationalError("Faltan variables de conexión a la base de datos (DB_HOST, DB_NAME, DB_USER, DB_PASS).")
         
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
    
    # --- 2. INTENTO DE CONEXIÓN Y CONSULTA DE LA DB ---
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Consulta para obtener los 7 artículos del blog más recientes
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
        
        # Formatear los datos para Jinja2
        for blog_data in db_blogs:
            (id, titulo, descripcion_corta, url_imagen_principal, fecha_creacion, slug) = blog_data
            
            # Formateo de Fecha
            fecha_formateada = fecha_creacion.strftime("%d %b, %Y")
            meses_espanol = {'Jan': 'Ene', 'Apr': 'Abr', 'Aug': 'Ago', 'Dec': 'Dic'}
            for en, es in meses_espanol.items():
                fecha_formateada = fecha_formateada.replace(en, es)
            
            # Lógica de las Imágenes de Blog: usa la URL de la DB o un placeholder si está vacía
            imagen_url = url_imagen_principal
            if not imagen_url or not imagen_url.strip():
                # Esta es la URL de placeholder (imagen ya destinada si falla la DB)
                imagen_url = 'https://via.placeholder.com/600x400.png?text=Smart+Books+Blog'

            blogs.append({
                'id': id,
                'titulo': titulo,
                'url_imagen_principal': imagen_url,
                'descripcion_corta': descripcion_corta,
                'fecha': fecha_formateada,
                'autor': 'Smart Books Team',     
                'categoria': 'Educación',        
                'url_articulo': f'/blog/{slug}'  
            })

        cur.close()

    except psycopg2.OperationalError as e:
        # Este error es el indicador CLAVE: Falla de credenciales o conectividad.
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS.")
        print(f"HOST: {DB_HOST}, USER: {DB_USER}, DB: {DB_NAME}")
        print(f"Mensaje: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        if conn:
            conn.close()

    # --- 3. CONTEXTO DE VARIABLES PARA LA PLANTILLA ---
    context = {
        # BANNERS: Usan URLs fijas de Unsplash, como siempre
        'url_banner1': 'https://images.unsplash.com/photo-1543269664-56b93a02a768?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 
        'url_banner2': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 
        
        # BLOGS: Lista vacía si la conexión falla, o llena con datos de la DB si es exitosa
        'blogs': blogs
    }

    return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)