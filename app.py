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
# Ahora lee directamente de las variables de entorno
DB_HOST = os.environ.get("DB_HOST") 
DB_NAME = os.environ.get("DB_NAME") 
DB_USER = os.environ.get("DB_USER") 
DB_PASS = os.environ.get("DB_PASS") 

# Configuración de puerto y host para Render
PORT = int(os.environ.get('PORT', 5000))
HOST = '0.0.0.0' 

app = Flask(__name__)

def get_db_connection():
    """Intenta establecer la conexión a la base de datos PostgreSQL."""
    # Se añade un chequeo simple para no fallar en psycopg2 con None
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS]):
         # Es una buena práctica lanzar un error si faltan las credenciales críticas
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
    config_data = {}
    conn = None
    
    # --- 2. INTENTO DE CONEXIÓN Y CONSULTA DE LA DB ---
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # --- CONSULTA 1: OBTENER URLs DE BANNERS Y RECUADROS ---
        sql_config = """
            SELECT 
                clave, 
                valor 
            FROM 
                configuracion_web 
            WHERE 
                clave IN ('url_banner1', 'url_banner2', 'url_recuadro1', 'url_recuadro2', 'url_recuadro3');
        """
        cur.execute(sql_config)
        db_config = cur.fetchall()

        # Almacenar las URLs en el diccionario 'config_data'
        for clave, valor in db_config:
            config_data[clave] = valor
            
        # Asignar valores a variables de contexto (con un fallback de seguridad si no están en la DB)
        url_banner1 = config_data.get('url_banner1', 'https://via.placeholder.com/1920x600.png?text=Falta+Banner+1')
        url_banner2 = config_data.get('url_banner2', 'https://via.placeholder.com/1920x600.png?text=Falta+Banner+2')
        url_recuadro1 = config_data.get('url_recuadro1', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+1')
        url_recuadro2 = config_data.get('url_recuadro2', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+2')
        url_recuadro3 = config_data.get('url_recuadro3', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+3')

        # --- CONSULTA 2: OBTENER LOS ARTÍCULOS DEL BLOG ---
        sql_blog_query = """
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
        cur.execute(sql_blog_query)
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
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS.")
        print(f"Mensaje: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # En caso de fallo crítico, usamos fallbacks
        url_banner1 = 'https://via.placeholder.com/1920x600.png?text=Falla+DB+-+Banner+1'
        url_banner2 = 'https://via.placeholder.com/1920x600.png?text=Falla+DB+-+Banner+2'
        url_recuadro1 = 'https://via.placeholder.com/600x400.png?text=Falla+DB+-+Recuadro+1'
        url_recuadro2 = 'https://via.placeholder.com/600x400.png?text=Falla+DB+-+Recuadro+2'
        url_recuadro3 = 'https://via.placeholder.com/600x400.png?text=Falla+DB+-+Recuadro+3'
        
    except Exception as e:
        print(f"Error inesperado durante la consulta de datos: {e}")
        # En caso de fallo inesperado, usamos fallbacks
        url_banner1 = 'https://via.placeholder.com/1920x600.png?text=Error+Inesperado+-+Banner+1'
        url_banner2 = 'https://via.placeholder.com/1920x600.png?text=Error+Inesperado+-+Banner+2'
        url_recuadro1 = 'https://via.placeholder.com/600x400.png?text=Error+Inesperado+-+Recuadro+1'
        url_recuadro2 = 'https://via.placeholder.com/600x400.png?text=Error+Inesperado+-+Recuadro+2'
        url_recuadro3 = 'https://via.placeholder.com/600x400.png?text=Error+Inesperado+-+Recuadro+3'
        
    finally:
        if conn:
            conn.close()

    # --- 3. CONTEXTO DE VARIABLES PARA LA PLANTILLA ---
    context = {
        # BANNERS
        'url_banner1': url_banner1, 
        'url_banner2': url_banner2, 
        
        # RECUADROS (NUEVO)
        'url_recuadro1': url_recuadro1,
        'url_recuadro2': url_recuadro2,
        'url_recuadro3': url_recuadro3,
        
        # BLOGS
        'blogs': blogs
    }

    return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)