import os
from flask import Flask, render_template
import psycopg2
from datetime import datetime

# =================================================================
# ATENCIÓN: CONFIGURACIÓN DE BASE DE DATOS
# >>> DEBES REEMPLAZAR ESTOS VALORES CON TUS CREDENCIALES REALES DE POSTGRESQL <<<
# =================================================================
# Si usas Render, considera usar Variables de Entorno y `os.environ.get()` aquí 
# para mayor seguridad y flexibilidad en producción.
DB_HOST = "localhost" 
DB_NAME = "nombre_de_tu_base_de_datos" 
DB_USER = "tu_usuario_postgres" 
DB_PASS = "tu_contraseña_postgres" 

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
    """
    Ruta principal: 
    1. Conecta a la DB y obtiene los 7 blogs.
    2. Define todas las variables requeridas por index.html (banners y blogs).
    3. Renderiza la plantilla.
    """
    blogs = []
    conn = None
    
    # --- 1. CONEXIÓN Y CONSULTA A LA BASE DE DATOS ---
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
                'descripcion_corta': descripcion_corta,
                'url_imagen_principal': url_imagen_principal,
                'fecha': fecha_formateada,
                'autor': 'Smart Books Team',     # Variable fija para el diseño
                'categoria': 'Educación',        # Variable fija para el diseño
                'url_articulo': f'/blog/{slug}'  # Enlace dinámico
            })

        cur.close()

    except psycopg2.Error as e:
        print(f"Error de base de datos PostgreSQL: {e}")
        # En caso de error, 'blogs' será una lista vacía, pero la web cargará.
    except Exception as e:
        print(f"Error inesperado: {e}")
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

    # --- 3. RENDERIZACIÓN DE LA PLANTILLA ---
    # Renderiza index.html (debe estar en la carpeta 'templates')
    return render_template('index.html', **context)

if __name__ == '__main__':
    # =================================================================
    # SOLUCIÓN CRÍTICA AL ERROR DE PUERTOS (PARA RENDER/HOSTING)
    # Se asegura que Flask escuche en 0.0.0.0 y use el puerto asignado
    # =================================================================
    PORT = int(os.environ.get('PORT', 5000))
    HOST = '0.0.0.0' 
    
    app.run(host=HOST, port=PORT, debug=True)