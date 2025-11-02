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
            'categoria': categoria, 
            'precio': precio,
            'precio_formateado': precio_formateado,
            'url_imagen': imagen_url,
            'rating': 5, # Valor fijo de ejemplo
            'descripcion_corta': descripcion.split('.')[0] if descripcion else "Descripción no disponible."
        })
    return productos

# =================================================================
# RUTA PRINCIPAL (PÁGINA DE INICIO)
# =================================================================
@app.route('/')
def index():
    conn = None
    
    # Se definen valores por defecto para mostrar en caso de un error de base de datos.
    context = {
        'blogs': [],
        'productos_destacados': []
    }
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Consulta 1: Configuración (Ahora busca los 6 banners y demás claves)
        claves_config = [
            'url_banner1', 'url_banner2', 'url_banner3', 'url_banner4', 'url_banner5', 'url_banner6',
            'url_recuadro1', 'url_recuadro2', 'url_recuadro3',
            'url_editorial1', 'url_editorial2', 'url_editorial3', 'url_editorial4', 'url_editorial5'
        ]
        
        sql_config = "SELECT clave, valor FROM configuracion_web WHERE clave IN %s;"
        cur.execute(sql_config, (tuple(claves_config),))
        db_config = cur.fetchall()
        config_data = dict(db_config)
            
        # --- INICIO DE LA CORRECCIÓN ---
        # Se agregan las URLs de banners y editoriales al contexto como variables individuales,
        # que es el formato que la plantilla index.html espera.
        
        # Asigna las URLs de los banners individualmente
        for i in range(1, 7):
            context[f'url_banner{i}'] = config_data.get(f'url_banner{i}', f'https://via.placeholder.com/1920x600.png?text=Falta+Banner+{i}')
        
        # Asigna las URLs de las editoriales individualmente
        for i in range(1, 6):
            context[f'url_editorial{i}'] = config_data.get(f'url_editorial{i}', f'https://via.placeholder.com/150x80.png?text=Editorial+{i}')

        # Asigna las URLs de los recuadros (esto ya estaba correcto)
        context['url_recuadro1'] = config_data.get('url_recuadro1', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+1')
        context['url_recuadro2'] = config_data.get('url_recuadro2', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+2')
        context['url_recuadro3'] = config_data.get('url_recuadro3', 'https://via.placeholder.com/600x400.png?text=Falta+Recuadro+3')
        # --- FIN DE LA CORRECCIÓN ---

        # Consulta 2: Artículos del Blog
        sql_blog_query = """
            SELECT id, titulo, descripcion_corta, url_imagen_principal, fecha_creacion, slug FROM articulos_blog 
            ORDER BY fecha_creacion DESC LIMIT 8; 
        """
        cur.execute(sql_blog_query)
        db_blogs = cur.fetchall()
        
        blogs = []
        for blog_data in db_blogs:
            (id, titulo, descripcion_corta, url_imagen_principal, fecha_creacion, slug) = blog_data
            fecha_formateada = fecha_creacion.strftime("%d %b, %Y")
            meses_espanol = {'Jan': 'Ene', 'Apr': 'Abr', 'Aug': 'Ago', 'Dec': 'Dic'}
            for en, es in meses_espanol.items():
                fecha_formateada = fecha_formateada.replace(en, es)
            imagen_url = url_imagen_principal if url_imagen_principal and url_imagen_principal.strip() else 'https://via.placeholder.com/600x400.png?text=Smart+Books+Blog'

            blogs.append({
                'id': id, 'titulo': titulo, 'url_imagen_principal': imagen_url,
                'descripcion_corta': descripcion_corta, 'fecha': fecha_formateada,
                'autor': 'Smart Books Team', 'categoria': 'Educación',        
                'url_articulo': f'/blog/{slug}'  
            })
        context['blogs'] = blogs
            
        # Consulta 3: Productos Destacados
        sql_productos_query = "SELECT sku, titulo, categoria, precio, url_imagen, descripcion FROM productos_escolares ORDER BY sku LIMIT 4;"
        cur.execute(sql_productos_query)
        db_productos = cur.fetchall()
        context['productos_destacados'] = format_products(db_productos)
            
        cur.close()

    except psycopg2.OperationalError as e:
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS. Mensaje: {e}")
        # En caso de error de DB, se asegura de que las variables esperadas por el template existan
        for i in range(1, 7):
            context.setdefault(f'url_banner{i}', f'https://via.placeholder.com/1920x600.png?text=Error+DB+{i}')
        for i in range(1, 6):
            context.setdefault(f'url_editorial{i}', f'https://via.placeholder.com/150x80.png?text=Error+DB')
        context.setdefault('url_recuadro1', 'https://via.placeholder.com/600x400.png?text=Error+DB')
        context.setdefault('url_recuadro2', 'https://via.placeholder.com/600x400.png?text=Error+DB')
        context.setdefault('url_recuadro3', 'https://via.placeholder.com/600x400.png?text=Error+DB')

    except Exception as e:
        print(f"Error inesperado durante la consulta de datos para la página de inicio: {e}")
    finally:
        if conn:
            conn.close()

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
    except Exception as e:
        print(f"Error inesperado al cargar productos de Castillo: {e}")
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

        sql_macmillan_query = "SELECT sku, titulo, categoria, precio, url_imagen, descripcion FROM productos_escolares WHERE categoria IN %s ORDER BY titulo ASC;"
        cur.execute(sql_macmillan_query, (tuple(macmillan_categories),))
        db_productos = cur.fetchall()
        productos = format_products(db_productos)
        cur.close()

    except psycopg2.OperationalError as e:
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS. Mensaje: {e}")
    except Exception as e:
        print(f"Error inesperado al cargar productos de MacMillan: {e}")
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
# RUTA PARA LA TIENDA GENERAL DE PRODUCTOS
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
        sql_productos_query = "SELECT sku, titulo, categoria, precio, url_imagen, descripcion FROM productos_escolares ORDER BY titulo ASC;"
        cur.execute(sql_productos_query)
        db_productos = cur.fetchall()
        productos = format_products(db_productos)
            
        # 2. Consulta para obtener las CATEGORÍAS únicas para los filtros
        sql_categorias_query = "SELECT DISTINCT categoria FROM productos_escolares ORDER BY categoria ASC;"
        cur.execute(sql_categorias_query)
        db_categorias = cur.fetchall()
        
        editoriales = ['MacMillan', 'Ediciones Castillo']
        
        for (cat,) in db_categorias:
            if 'MacMillan' in cat:
                tipo_texto = cat.replace(', MacMillan', '').strip()
            elif 'Ediciones Castillo' in cat:
                tipo_texto = cat.replace('Ediciones Castillo', '').strip()
            else:
                tipo_texto = cat
            
            if tipo_texto and tipo_texto != cat:
                categorias.append(tipo_texto)
            if cat not in categorias:
                 categorias.append(cat)
        
        categorias = sorted(list(set(categorias)))
        
        cur.close()

    except psycopg2.OperationalError as e:
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS. Mensaje: {e}")
    except Exception as e:
        print(f"Error inesperado al cargar la tienda: {e}")
    finally:
        if conn:
            conn.close()

    context = {
        'titulo_pagina': 'Tienda de Textos Escolares',
        'productos': productos,
        'total_productos': len(productos),
        'editoriales': editoriales,
        'tipos_texto': categorias
    }
    
    return render_template('tienda_productos.html', **context)

@app.route('/api/colegios', methods=['GET'])
def get_colegios_data():
    conn = None
    colegios_data = []
    
    # 1. Lista de KEYS que el JavaScript del cliente ESPERA (Mayúsculas)
    JSON_KEYS = [
        'id', 'COLEGIO', 'CIUDAD', 'IMAGEN', 'UBICACION', 
        'PREJARDIN', 'JARDIN', 'TRANSICION', 'PRIMERO', 'SEGUNDO', 
        'TERCERO', 'CUARTO', 'QUINTO', 'SEXTO', 'SEPTIMO', 
        'OCTAVO', 'NOVENO', 'DECIMO', 'ONCE'
    ]
    
    # 2. Lista de COLUMNAS SQL (Minúsculas para PostgreSQL)
    SQL_COLUMNS = [k.lower() for k in JSON_KEYS] # ['id', 'colegio', 'ciudad', ...]
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Consulta: Usamos las columnas en minúscula para la consulta SQL
        query = f"SELECT {', '.join(SQL_COLUMNS)} FROM colegios ORDER BY colegio ASC;"
        cur.execute(query)
        
        # Mapea los resultados: Usamos JSON_KEYS (mayúsculas) como claves
        # para el diccionario, asegurando que el cliente reciba lo que espera.
        colegios_data = [dict(zip(JSON_KEYS, row)) for row in cur.fetchall()]
        
        return jsonify(colegios_data), 200

    except Exception as e:
        # Esto captura errores de conexión o errores en la consulta SQL
        # Se imprime el error para el registro del servidor
        print(f"Error al obtener la lista de colegios (FATAL DB ERROR): {e}") 
        # Devuelve el error 500 al cliente
        return jsonify({"error": "Error interno del servidor al obtener datos de colegios", "detail": str(e)}), 500
    finally:
        if conn:
            conn.close()

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

@app.route('/blog')
def blog():
    return render_template('Blog.html')

@app.route('/intranet')
def intranet():
    return render_template('Intranet.html')


# Esta línea debe quedar al final de tu archivo para ejecutar la app
if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)