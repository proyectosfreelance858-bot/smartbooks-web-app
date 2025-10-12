import os
from flask import Flask, render_template
import psycopg2
from datetime import datetime

# =================================================================
# ATENCIÓN: CONFIGURACIÓN DE BASE DE DATOS
# >>> DEBES REEMPLAZAR ESTOS VALORES CON TUS CREDENCIALES REALES DE POSTGRESQL <<<
# =================================================================
DB_HOST = "localhost" 
DB_NAME = "nombre_de_tu_base_de_datos" 
DB_USER = "tu_usuario_postgres" 
DB_PASS = "tu_contraseña_postgres" 

app = Flask(__name__)

def get_db_connection():
    """Establece la conexión a la base de datos PostgreSQL."""
    # Nota: psycopg2 usará las credenciales definidas arriba
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
    1. Conecta a la DB.
    2. Obtiene los datos de los 7 blogs (blogs).
    3. Define las variables de carrusel (url_banner1, url_banner2).
    4. Renderiza el index.html con todos los datos.
    """
    blogs = []
    conn = None
    
    # --- 1. CONEXIÓN Y CONSULTA A LA BASE DE DATOS ---
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Consulta para obtener los 7 artículos del blog más recientes
        # La tabla se llama articulos_blog según el script SQL anterior
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
        
        # Formatear los datos obtenidos de la base de datos
        for blog_data in db_blogs:
            (id, titulo, descripcion_corta, url_imagen_principal, fecha_creacion, slug) = blog_data
            
            # Formateo de Fecha: '01 Oct, 2025'
            # Se convierte la fecha del objeto datetime a un string y se traducen los meses
            fecha_formateada = fecha_creacion.strftime("%d %b, %Y")
            meses_espanol = {'Jan': 'Ene', 'Apr': 'Abr', 'Aug': 'Ago', 'Dec': 'Dic'}
            for en, es in meses_espanol.items():
                fecha_formateada = fecha_formateada.replace(en, es)
            
            # Construcción del diccionario 'blog' para Jinja2
            blogs.append({
                'id': id,
                'titulo': titulo,
                'descripcion_corta': descripcion_corta,
                'url_imagen_principal': url_imagen_principal,
                'fecha': fecha_formateada,
                'autor': 'Smart Books Team',     # Valor fijo para el diseño (Se podría obtener de otra tabla)
                'categoria': 'Educación',        # Valor fijo para el diseño (Se podría obtener de otra columna)
                'url_articulo': f'/blog/{slug}'  # Enlace de ejemplo al detalle del artículo
            })

        cur.close()

    except psycopg2.Error as e:
        print(f"Error de base de datos PostgreSQL: {e}")
        # En caso de error, 'blogs' será una lista vacía, y la web cargará sin los artículos.
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        if conn:
            conn.close()

    # --- 2. CONTEXTO DE VARIABLES PARA LA PLANTILLA (Incluye las variables anteriores) ---
    context = {
        # Variables anteriores para el Carrusel
        'url_banner1': 'https://images.unsplash.com/photo-1543269664-56b93a02a768?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 
        'url_banner2': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 
        
        # Nueva variable que alimenta la sección del Blog
        'blogs': blogs
    }

    # --- 3. RENDERIZACIÓN DE LA PLANTILLA ---
    # Renderiza index.html (debe estar en la carpeta 'templates')
    return render_template('index.html', **context)

if __name__ == '__main__':
    # Ejecuta la aplicación Flask en modo de depuración
    # (Para producción, se debe usar un servidor WSGI como Gunicorn)
    app.run(debug=True)