import os
from flask import Flask, render_template, abort
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

# Función auxiliar para formatear productos (evita repetir código)
def format_products(db_productos):
    """Convierte los resultados de la consulta de productos en un formato de lista de diccionarios."""
    productos = []
    for producto_data in db_productos:
        (sku, titulo, categoria, precio, url_imagen, descripcion) = producto_data
        
        precio_formateado = f"${precio:,.0f}".replace(",", ".")
        
        imagen_url = url_imagen
        if not imagen_url or not imagen_url.strip():
            imagen_url = 'https://via.placeholder.com/400x500.png?text=Producto'
        
        productos.append({
            'sku': sku,
            'titulo': titulo,
            'categoria': categoria,
            'precio': precio,
            'precio_formateado': precio_formateado,
            'url_imagen': imagen_url,
            'rating': 5,
            'descripcion_corta': descripcion.split('.')[0] if descripcion else "Descripción no disponible."
        })
    return productos


@app.route('/')
def index():
    blogs = []
    productos_destacados = [] 
    config_data = {}
    conn = None
    
    # --- 2. INTENTO DE CONEXIÓN Y CONSULTA DE LA DB ---
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # --- CONSULTA 1: OBTENER URLs DE BANNERS, RECUADROS Y EDITORIALES ---
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

        for clave, valor in db_config:
            config_data[clave] = valor
            
        # Asignar valores a variables de contexto (con un fallback de seguridad si no están en la DB)
        url_banner1 = config_data.get('url_banner1', 'https://via.placeholder.com/1920x600.png?text=Falta+Banner+1')
        url_banner2 = config_data.get('url_banner2', 'https://via.placeholder.com/1920x600.png?text=Falta+Banner+2')
        url_recuadro1 = config_data.get('url_recuadro1', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+1')
        url_recuadro2 = config_data.get('url_recuadro2', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+2')
        url_recuadro3 = config_data.get('url_recuadro3', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+3')
        url_editorial1 = config_data.get('url_editorial1', 'https://via.placeholder.com/150x80.png?text=Editorial+1')
        url_editorial2 = config_data.get('url_editorial2', 'https://via.placeholder.com/150x80.png?text=Editorial+2')
        url_editorial3 = config_data.get('url_editorial3', 'https://via.placeholder.com/150x80.png?text=Editorial+3')
        url_editorial4 = config_data.get('url_editorial4', 'https://via.placeholder.com/150x80.png?text=Editorial+4')
        url_editorial5 = config_data.get('url_editorial5', 'https://via.placeholder.com/150x80.png?text=Editorial+5')


        # --- CONSULTA 2: OBTENER LOS ARTÍCULOS DEL BLOG ---
        sql_blog_query = """
            SELECT 
                id, titulo, descripcion_corta, url_imagen_principal, fecha_creacion, slug 
            FROM 
                articulos_blog 
            ORDER BY 
                fecha_creacion DESC 
            LIMIT 8; 
        """
        cur.execute(sql_blog_query)
        db_blogs = cur.fetchall()
        
        # Formatear los datos del blog
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
            
        # --- CONSULTA 3: OBTENER PRODUCTOS MÁS VENDIDOS (Para index.html) ---
        sql_productos_query = """
            SELECT 
                sku, titulo, categoria, precio, url_imagen, descripcion 
            FROM 
                productos_escolares 
            -- Los ordenamos por SKU para consistencia, limitando a 4
            ORDER BY sku 
            LIMIT 4; 
        """
        cur.execute(sql_productos_query)
        db_productos = cur.fetchall()
        productos_destacados = format_products(db_productos) # Usamos la función auxiliar
            
        cur.close()

    except psycopg2.OperationalError as e:
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS. Mensaje: {e}")
        # Manejo de fallbacks simplificado
        url_banner1, url_banner2 = 'https://via.placeholder.com/1920x600.png?text=Error+DB', 'https://via.placeholder.com/1920x600.png?text=Error+DB'
        url_recuadro1, url_recuadro2, url_recuadro3 = 'https://via.placeholder.com/600x400.png?text=Error+DB', 'https://via.placeholder.com/600x400.png?text=Error+DB', 'https://via.placeholder.com/600x400.png?text=Error+DB'
        url_editorial1, url_editorial2, url_editorial3, url_editorial4, url_editorial5 = ['https://via.placeholder.com/150x80.png?text=Error+DB'] * 5
        
    except Exception as e:
        print(f"Error inesperado durante la consulta de datos: {e}")
        # Manejo de fallbacks simplificado
        url_banner1, url_banner2 = 'https://via.placeholder.com/1920x600.png?text=Error+Inesperado', 'https://via.placeholder.com/1920x600.png?text=Error+Inesperado'
        url_recuadro1, url_recuadro2, url_recuadro3 = 'https://via.placeholder.com/600x400.png?text=Error+Inesperado', 'https://via.placeholder.com/600x400.png?text=Error+Inesperado', 'https://via.placeholder.com/600x400.png?text=Error+Inesperado'
        url_editorial1, url_editorial2, url_editorial3, url_editorial4, url_editorial5 = ['https://via.placeholder.com/150x80.png?text=Error+E'] * 5
        
    finally:
        if conn:
            conn.close()

    # --- 3. CONTEXTO DE VARIABLES PARA LA PLANTILLA ---
    context = {
        'url_banner1': url_banner1, 'url_banner2': url_banner2, 
        'url_recuadro1': url_recuadro1, 'url_recuadro2': url_recuadro2, 'url_recuadro3': url_recuadro3,
        'url_editorial1': url_editorial1, 'url_editorial2': url_editorial2, 'url_editorial3': url_editorial3, 
        'url_editorial4': url_editorial4, 'url_editorial5': url_editorial5,
        'blogs': blogs,
        'productos_destacados': productos_destacados
    }

    return render_template('index.html', **context)


# =================================================================
# RUTA PARA LA PÁGINA DE EDICIONES CASTILLO
# =================================================================

@app.route('/aliados/castillo')
def aliados_castillo():
    productos = []
    conn = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Usamos LIKE para obtener todas las subcategorías que empiezan por 'Ediciones Castillo'
        sql_castillo_query = """
            SELECT 
                sku, titulo, categoria, precio, url_imagen, descripcion
            FROM 
                productos_escolares 
            WHERE 
                categoria LIKE 'Ediciones Castillo%%' 
            ORDER BY 
                titulo ASC; 
        """
        cur.execute(sql_castillo_query)
        db_productos = cur.fetchall()
        
        productos = format_products(db_productos)
            
        cur.close()

    except psycopg2.OperationalError as e:
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS. Mensaje: {e}")
        pass 
    except Exception as e:
        print(f"Error inesperado al cargar productos de Castillo: {e}")
        pass
    finally:
        if conn:
            conn.close()

    context = {
        'titulo_pagina': 'Ediciones Castillo',
        'productos': productos,
        # URL del logo de Ediciones Castillo
        'url_logo_editorial': 'https://sbooks.com.co/wp-content/uploads/2023/09/Ediciones-Color-2.png', 
        'texto_presentacion': 'Explora la colección completa de textos escolares, guías y plan lector de Ediciones Castillo, líder en innovación educativa.',
        'total_productos': len(productos)
    }
    
    # Se espera que el nombre de la plantilla sea 'Castillo.html'
    return render_template('Castillo.html', **context)


# =================================================================
# NUEVA RUTA PARA LA PÁGINA DE MACMILLAN EDUCATION
# =================================================================

@app.route('/aliados/macmillan')
def aliados_macmillan():
    productos = []
    conn = None
    
    # Lista de categorías exactas proporcionadas por el usuario para MacMillan
    macmillan_categories = [
        'MacMillan',
        'Give Me Five, MacMillan',
        'Insta English, MacMillan',
        'Doodle Town, MacMillan',
        'Ferris Wheel, MacMillan'
    ]
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Usamos IN para obtener los productos de las categorías exactas de MacMillan
        # Nota: La sintaxis de psycopg2 para IN requiere pasar una tupla de valores
        sql_macmillan_query = """
            SELECT 
                sku, titulo, categoria, precio, url_imagen, descripcion
            FROM 
                productos_escolares 
            WHERE 
                categoria IN %s
            ORDER BY 
                titulo ASC; 
        """
        # Ejecutamos la consulta. La tupla se pasa como una sola variable de consulta
        cur.execute(sql_macmillan_query, (tuple(macmillan_categories),))
        db_productos = cur.fetchall()
        
        productos = format_products(db_productos)
            
        cur.close()

    except psycopg2.OperationalError as e:
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS. Mensaje: {e}")
        pass 
    except Exception as e:
        print(f"Error inesperado al cargar productos de MacMillan: {e}")
        pass
    finally:
        if conn:
            conn.close()

    context = {
        'titulo_pagina': 'MacMillan Education',
        'productos_macmillan': productos, # Variable usada en la plantilla aliados_macmillan.html
        # URL del logo de MacMillan proporcionada por el usuario
        'url_logo_editorial': 'https://sbooks.com.co/wp-content/uploads/2022/11/logo_MacMillanresized.webp', 
        'texto_presentacion': 'Explora la colección completa de textos, plataformas y soluciones bilingües de MacMillan Education.',
        'total_productos': len(productos)
    }
    
    # Renderizamos la nueva plantilla 'aliados_macmillan.html'
    return render_template('aliados_macmillan.html', **context)


if __name__ == '__main__':
    # Usar debug=True solo en entorno de desarrollo
    app.run(host=HOST, port=PORT, debug=True)