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

# Función auxiliar para formatear productos (evita repetir código)
def format_products(db_productos):
    """Convierte los resultados de la consulta de productos en un formato de lista de diccionarios."""
    productos = []
    for producto_data in db_productos:
        # Asegúrate de que el orden de las columnas sea:
        # (sku, titulo, categoria, precio, url_imagen, descripcion)
        (sku, titulo, categoria, precio, url_imagen, descripcion) = producto_data
        
        precio_formateado = f"${precio:,.0f}".replace(",", ".")
        
        imagen_url = url_imagen
        if not imagen_url or not imagen_url.strip():
            imagen_url = 'https://via.placeholder.com/400x500.png?text=Producto'
        
        productos.append({
            'sku': sku,
            'titulo': titulo,
            # NOTA: En la tienda, la categoría se usará como "Tipo de Texto"
            'categoria': categoria, 
            'precio': precio,
            'precio_formateado': precio_formateado,
            'url_imagen': imagen_url,
            'rating': 5, # Valor fijo de ejemplo
            'descripcion_corta': descripcion.split('.')[0] if descripcion else "Descripción no disponible."
        })
    return productos


# =================================================================
# RUTA PRINCIPAL (index, aliadas y otras rutas anteriores...)
# ... (TU CÓDIGO ANTERIOR PARA index, aliados_castillo y aliados_macmillan VA AQUÍ) ...
# Dado que ya te lo proporcioné modificado en el paso anterior, 
# solo añado la nueva función 'tienda()' y el código base anterior.
# =================================================================

# CÓDIGO DE index() VA AQUÍ
# CÓDIGO DE aliados_castillo() VA AQUÍ
# CÓDIGO DE aliados_macmillan() VA AQUÍ
# (Usaremos el app.py modificado del último paso, no el original, para la integridad del código)

# A continuación, el código de app.py modificado completo con la nueva función 'tienda'.

# --- app.py completo (versión final) ---

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
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Consulta 1: Configuración
        sql_config = """
            SELECT clave, valor FROM configuracion_web 
            WHERE clave IN (
                'url_banner1', 'url_banner2', 'url_recuadro1', 'url_recuadro2', 'url_recuadro3',
                'url_editorial1', 'url_editorial2', 'url_editorial3', 'url_editorial4', 'url_editorial5'
            );
        """
        cur.execute(sql_config)
        db_config = cur.fetchall()

        for clave, valor in db_config:
            config_data[clave] = valor
            
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


        # Consulta 2: Artículos del Blog
        sql_blog_query = """
            SELECT id, titulo, descripcion_corta, url_imagen_principal, fecha_creacion, slug FROM articulos_blog 
            ORDER BY fecha_creacion DESC LIMIT 8; 
        """
        cur.execute(sql_blog_query)
        db_blogs = cur.fetchall()
        
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
            
        # Consulta 3: Productos Destacados
        sql_productos_query = """
            SELECT sku, titulo, categoria, precio, url_imagen, descripcion FROM productos_escolares 
            ORDER BY sku LIMIT 4; 
        """
        cur.execute(sql_productos_query)
        db_productos = cur.fetchall()
        productos_destacados = format_products(db_productos)
            
        cur.close()

    except psycopg2.OperationalError as e:
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS. Mensaje: {e}")
        url_banner1, url_banner2 = 'https://via.placeholder.com/1920x600.png?text=Error+DB', 'https://via.placeholder.com/1920x600.png?text=Error+DB'
        url_recuadro1, url_recuadro2, url_recuadro3 = 'https://via.placeholder.com/600x400.png?text=Error+DB', 'https://via.placeholder.com/600x400.png?text=Error+DB', 'https://via.placeholder.com/600x400.png?text=Error+DB'
        url_editorial1, url_editorial2, url_editorial3, url_editorial4, url_editorial5 = ['https://via.placeholder.com/150x80.png?text=Error+DB'] * 5
        
    except Exception as e:
        print(f"Error inesperado durante la consulta de datos: {e}")
        url_banner1, url_banner2 = 'https://via.placeholder.com/1920x600.png?text=Error+Inesperado', 'https://via.placeholder.com/1920x600.png?text=Error+Inesperado'
        url_recuadro1, url_recuadro2, url_recuadro3 = 'https://via.placeholder.com/600x400.png?text=Error+Inesperado', 'https://via.placeholder.com/600x400.png?text=Error+Inesperado', 'https://via.placeholder.com/600x400.png?text=Error+Inesperado'
        url_editorial1, url_editorial2, url_editorial3, url_editorial4, url_editorial5 = ['https://via.placeholder.com/150x80.png?text=Error+E'] * 5
        
    finally:
        if conn:
            conn.close()

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

        sql_castillo_query = """
            SELECT sku, titulo, categoria, precio, url_imagen, descripcion FROM productos_escolares 
            WHERE categoria LIKE 'Ediciones Castillo%%' 
            ORDER BY titulo ASC; 
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
        'url_logo_editorial': 'https://sbooks.com.co/wp-content/uploads/2023/09/Ediciones-Color-2.png', 
        'texto_presentacion': 'Explora la colección completa de textos escolares, guías y plan lector de Ediciones Castillo, líder en innovación educativa.',
        'total_productos': len(productos)
    }
    
    return render_template('Castillo.html', **context)


# =================================================================
# RUTA PARA LA PÁGINA DE MACMILLAN EDUCATION
# =================================================================

@app.route('/aliados/macmillan')
def aliados_macmillan():
    productos = []
    conn = None
    
    macmillan_categories = [
        'MacMillan', 'Give Me Five, MacMillan', 'Insta English, MacMillan', 
        'Doodle Town, MacMillan', 'Ferris Wheel, MacMillan'
    ]
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        sql_macmillan_query = """
            SELECT sku, titulo, categoria, precio, url_imagen, descripcion FROM productos_escolares 
            WHERE categoria IN %s
            ORDER BY titulo ASC; 
        """
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
        'productos_macmillan': productos,
        'url_logo_editorial': 'https://sbooks.com.co/wp-content/uploads/2022/11/logo_MacMillanresized.webp', 
        'texto_presentacion': 'Explora la colección completa de textos, plataformas y soluciones bilingües de MacMillan Education.',
        'total_productos': len(productos)
    }
    
    return render_template('aliados_macmillan.html', **context)


# =================================================================
# NUEVA RUTA PARA LA TIENDA GENERAL DE PRODUCTOS
# =================================================================

@app.route('/tienda')
def tienda():
    productos = []
    categorias = []
    conn = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Consulta para OBTENER TODOS los productos
        sql_productos_query = """
            SELECT sku, titulo, categoria, precio, url_imagen, descripcion
            FROM productos_escolares 
            ORDER BY titulo ASC; 
        """
        cur.execute(sql_productos_query)
        db_productos = cur.fetchall()
        productos = format_products(db_productos)
            
        # 2. Consulta para obtener las CATEGORÍAS únicas (Tipos de Texto) para los filtros
        # Se asume que 'categoria' contiene el "Tipo de Texto" (Ej: 'Ferris Wheel, MacMillan')
        sql_categorias_query = """
            SELECT DISTINCT categoria 
            FROM productos_escolares 
            ORDER BY categoria ASC;
        """
        cur.execute(sql_categorias_query)
        db_categorias = cur.fetchall()
        
        # Formatear categorías: solo necesitamos el nombre
        # También preparamos la lista de editoriales principales para el filtro "Editorial"
        editoriales = ['MacMillan', 'Ediciones Castillo']
        
        # Extraemos el nombre de la subcategoría/tipo de texto para el filtro
        for (cat,) in db_categorias:
            # Quitamos el nombre del aliado para dejar solo el "Tipo de Texto" si es posible
            if 'MacMillan' in cat:
                tipo_texto = cat.replace(', MacMillan', '').strip()
            elif 'Ediciones Castillo' in cat:
                tipo_texto = cat.replace('Ediciones Castillo', '').strip()
            else:
                tipo_texto = cat
            
            # Solo añadimos las categorías que tengan un nombre significativo
            if tipo_texto and tipo_texto != cat:
                 # Añade la subcategoría específica (Ej: 'Ferris Wheel')
                categorias.append(tipo_texto)
            
            # También mantenemos la categoría completa como fallback
            if cat not in categorias:
                 categorias.append(cat)
        
        # Eliminar duplicados si los hubo
        categorias = sorted(list(set(categorias)))
        
        cur.close()

    except psycopg2.OperationalError as e:
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS. Mensaje: {e}")
        pass
    except Exception as e:
        print(f"Error inesperado al cargar la tienda: {e}")
        pass
    finally:
        if conn:
            conn.close()

    context = {
        'titulo_pagina': 'Tienda de Textos Escolares',
        'productos': productos,
        'total_productos': len(productos),
        'editoriales': editoriales, # ['MacMillan', 'Ediciones Castillo']
        'tipos_texto': categorias # Ej: ['Doodle Town', 'Ferris Wheel', 'Insta English', etc.]
    }
    
    return render_template('tienda_productos.html', **context)
# =================================================================
# RUTAS PARA PÁGINAS ESTÁTICAS (Quienes Somos, Contacto, etc.)
# =================================================================

@app.route('/quienes-somos')
def quienes_somos():
    return render_template('QuienesSomos.html')

@app.route('/terminos-y-condiciones')
def terminos_y_condiciones():
    return render_template('TerminosYCondiciones.html')

@app.route('/preguntas-frecuentes')
def preguntas_frecuentes():
    return render_template('PreguntasFrecuentes.html')

@app.route('/colegios')
def colegios():
    return render_template('Colegios.html')

@app.route('/contactanos')
def contactanos():
    return render_template('Contactanos.html')

# Aunque Blog.html esté vacío, es bueno tener la ruta lista
@app.route('/blog')
def blog():
    return render_template('Blog.html')

# La ruta para Intranet debe coincidir con el nombre de tu archivo
@app.route('/intranet')
def intranet():
    return render_template('Intranet.html')


# ESTA LÍNEA DEBE QUEDAR AL FINAL DE TU ARCHIVO
if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)