import os
from flask import Flask, render_template
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# =================================================================
# 1. CONFIGURACIÓN DE BASE DE DATOS Y HOSTING
# =================================================================
DB_HOST = os.environ.get("DB_HOST", "localhost") 
DB_NAME = os.environ.get("DB_NAME", "nombre_de_tu_base_de_datos") 
DB_USER = os.environ.get("DB_USER", "tu_usuario_postgres") 
DB_PASS = os.environ.get("DB_PASS", "tu_contraseña_postgres") 

PORT = int(os.environ.get('PORT', 5000))
HOST = '0.0.0.0' 

app = Flask(__name__)

def get_db_connection():
    """Intenta establecer la conexión a la base de datos PostgreSQL."""
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS]):
         raise psycopg2.OperationalError("Faltan variables de conexión a la base de datos.")
         
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

        # --- CONSULTA 1: OBTENER URLs DE BANNERS, RECUADROS Y EDITORIALES ---
        # Se añaden las 5 variables de editoriales a la consulta
        sql_config = """
            SELECT 
                clave, 
                valor 
            FROM 
                configuracion_web 
            WHERE 
                clave IN (
                    'url_banner1', 'url_banner2', 
                    'url_recuadro1', 'url_recuadro2', 'url_recuadro3',
                    'url_editorial1', 'url_editorial2', 'url_editorial3', 'url_editorial4', 'url_editorial5'
                );
        """
        cur.execute(sql_config)
        db_config = cur.fetchall()

        # Almacenar las URLs en el diccionario 'config_data'
        for clave, valor in db_config:
            config_data[clave] = valor
            
        # Asignar valores a variables de contexto (con un fallback de seguridad si no están en la DB)
        # Banners
        url_banner1 = config_data.get('url_banner1', 'https://via.placeholder.com/1920x600.png?text=Falta+Banner+1')
        url_banner2 = config_data.get('url_banner2', 'https://via.placeholder.com/1920x600.png?text=Falta+Banner+2')
        # Recuadros
        url_recuadro1 = config_data.get('url_recuadro1', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+1')
        url_recuadro2 = config_data.get('url_recuadro2', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+2')
        url_recuadro3 = config_data.get('url_recuadro3', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+3')
        # Editoriales (NUEVO)
        url_editorial1 = config_data.get('url_editorial1', 'https://via.placeholder.com/150x80.png?text=Editorial+1')
        url_editorial2 = config_data.get('url_editorial2', 'https://via.placeholder.com/150x80.png?text=Editorial+2')
        url_editorial3 = config_data.get('url_editorial3', 'https://via.placeholder.com/150x80.png?text=Editorial+3')
        url_editorial4 = config_data.get('url_editorial4', 'https://via.placeholder.com/150x80.png?text=Editorial+4')
        url_editorial5 = config_data.get('url_editorial5', 'https://via.placeholder.com/150x80.png?text=Editorial+5')


        # --- CONSULTA 2: OBTENER LOS ARTÍCULOS DEL BLOG (igual que antes) ---
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
        
        # Formatear los datos (lógica omitida por ser igual a la anterior)
        for blog_data in db_blogs:
            (id, titulo, descripcion_corta, url_imagen_principal, fecha_creacion, slug) = blog_data
            fecha_formateada = fecha_creacion.strftime("%d %b, %Y")
            meses_espanol = {'Jan': 'Ene', 'Apr': 'Abr', 'Aug': 'Ago', 'Dec': 'Dic'}
            for en, es in meses_espanol.items():
                fecha_formateada = fecha_formateada.replace(en, es)
            imagen_url = url_imagen_principal
            if not imagen_url or not imagen_url.strip():
                imagen_url = 'https://via.placeholder.com/600x400.png?text=Smart+Books+Blog'

            blogs.append({
                'id': id, 'titulo': titulo, 'url_imagen_principal': imagen_url,
                'descripcion_corta': descripcion_corta, 'fecha': fecha_formateada,
                'autor': 'Smart Books Team', 'categoria': 'Educación',        
                'url_articulo': f'/blog/{slug}'  
            })

        cur.close()

    except psycopg2.OperationalError as e:
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS. Mensaje: {e}")
        # En caso de fallo crítico, usamos fallbacks
        url_banner1 = 'https://via.placeholder.com/1920x600.png?text=Falla+DB+-+Banner+1'
        url_banner2 = 'https://via.placeholder.com/1920x600.png?text=Falla+DB+-+Banner+2'
        url_recuadro1 = 'https://via.placeholder.com/600x400.png?text=Falla+DB+-+Recuadro+1'
        url_recuadro2 = 'https://via.placeholder.com/600x400.png?text=Falla+DB+-+Recuadro+2'
        url_recuadro3 = 'https://via.placeholder.com/600x400.png?text=Falla+DB+-+Recuadro+3'
        url_editorial1 = 'https://via.placeholder.com/150x80.png?text=Error+E1'
        url_editorial2 = 'https://via.placeholder.com/150x80.png?text=Error+E2'
        url_editorial3 = 'https://via.placeholder.com/150x80.png?text=Error+E3'
        url_editorial4 = 'https://via.placeholder.com/150x80.png?text=Error+E4'
        url_editorial5 = 'https://via.placeholder.com/150x80.png?text=Error+E5'
        
    except Exception as e:
        print(f"Error inesperado durante la consulta de datos: {e}")
        # En caso de fallo inesperado, usamos fallbacks
        url_banner1 = 'https://via.placeholder.com/1920x600.png?text=Error+Inesperado+-+Banner+1'
        url_banner2 = 'https://via.placeholder.com/1920x600.png?text=Error+Inesperado+-+Banner+2'
        url_recuadro1 = 'https://via.placeholder.com/600x400.png?text=Error+Inesperado+-+Recuadro+1'
        url_recuadro2 = 'https://via.placeholder.com/600x400.png?text=Error+Inesperado+-+Recuadro+2'
        url_recuadro3 = 'https://via.placeholder.com/600x400.png?text=Error+Inesperado+-+Recuadro+3'
        url_editorial1 = 'https://via.placeholder.com/150x80.png?text=Error+E1'
        url_editorial2 = 'https://via.placeholder.com/150x80.png?text=Error+E2'
        url_editorial3 = 'https://via.placeholder.com/150x80.png?text=Error+E3'
        url_editorial4 = 'https://via.placeholder.com/150x80.png?text=Error+E4'
        url_editorial5 = 'https://via.placeholder.com/150x80.png?text=Error+E5'
        
    finally:
        if conn:
            conn.close()

    # --- 3. CONTEXTO DE VARIABLES PARA LA PLANTILLA ---
    context = {
        'url_banner1': url_banner1, 
        'url_banner2': url_banner2, 
        'url_recuadro1': url_recuadro1,
        'url_recuadro2': url_recuadro2,
        'url_recuadro3': url_recuadro3,
        # Variables de Editoriales (NUEVO)
        'url_editorial1': url_editorial1,
        'url_editorial2': url_editorial2,
        'url_editorial3': url_editorial3,
        'url_editorial4': url_editorial4,
        'url_editorial5': url_editorial5,
        'blogs': blogs
    }

    return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)