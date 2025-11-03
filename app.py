import os
from flask import Flask, render_template, jsonify, request
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# =================================================================
# 1. CONFIGURACIÓN DE BASE DE DATOS Y HOSTING
# =================================================================
# Las variables se leen del archivo .env o se usan valores por defecto
DB_HOST = os.environ.get("DB_HOST", "localhost") 
DB_NAME = os.environ.get("DB_NAME", "nombre_de_tu_base_de_datos") 
DB_USER = os.environ.get("DB_USER", "tu_usuario_postgres") 
DB_PASS = os.environ.get("DB_PASS", "tu_contraseña_postgres") 
DB_PORT = os.environ.get("DB_PORT", "5432") # PUERTO (Importante para Render)

PORT = int(os.environ.get('PORT', 5000))
HOST = '0.0.0.0' 

app = Flask(__name__)

def get_db_connection():
    """
    Intenta establecer la conexión a la base de datos PostgreSQL.
    Añade sslmode='require' para conexiones remotas (CRUCIAL para Render).
    """
    # Verificamos que todas las variables estén presentes
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT]):
          raise psycopg2.OperationalError("Faltan variables de conexión a la base de datos.")
          
    # La función connect devuelve un objeto de conexión, el cual es un context manager
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        sslmode='require' # SOLUCIÓN PARA EL ERROR DE CONEXIÓN REMOTA (500)
    )
    return conn

# Columnas esperadas para la tabla de productos
PRODUCT_COLUMNS = [
    'id', 'nombre_producto', 'sku', 'descripcion', 'precio', 'editorial', 
    'tipo_texto', 'imagen_url', 'stock', 'fecha_creacion', 'es_kit'
]

def format_product(row):
    """Mapea una fila de producto a un diccionario usando las claves de PRODUCT_COLUMNS."""
    return dict(zip(PRODUCT_COLUMNS, row))

# Función para obtener todas las editoriales para filtros de la tienda
def get_editoriales():
    editoriales = []
    try:
        # **USO DE 'WITH' para asegurar el cierre de la conexión y cursor**
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT editorial FROM productos WHERE editorial IS NOT NULL ORDER BY editorial;")
                editoriales = [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error al obtener editoriales: {e}")
    return editoriales

# Función para obtener todas las categorías/tipos_texto para filtros de la tienda
def get_tipos_texto():
    categorias = []
    try:
        # **USO DE 'WITH' para asegurar el cierre de la conexión y cursor**
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT tipo_texto FROM productos WHERE tipo_texto IS NOT NULL ORDER BY tipo_texto;")
                categorias = [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
    return categorias


# =================================================================
# 2. RUTAS DE TIENDA Y PRODUCTOS
# =================================================================

@app.route('/tienda')
def tienda():
    productos = []
    editoriales = get_editoriales()
    categorias = get_tipos_texto()

    # Base de la consulta, asegurando que las columnas estén en minúsculas para PostgreSQL
    sql_product_columns = [col.lower() for col in PRODUCT_COLUMNS]
    base_query = f"SELECT {', '.join(sql_product_columns)} FROM productos"
    where_clauses = []
    params = []

    # Ejemplo de lógica de filtrado por URL (si la necesitas)
    # editorial_filter = request.args.get('editorial')
    # if editorial_filter:
    #     where_clauses.append("editorial = %s")
    #     params.append(editorial_filter)
        
    query = base_query
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += " ORDER BY nombre_producto ASC;"

    try:
        # **USO DE 'WITH' para asegurar el cierre de la conexión y cursor**
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                
                # Mapear los resultados
                productos = [format_product(row) for row in cur.fetchall()]

    except Exception as e:
        print(f"Error inesperado al cargar la tienda: {e}")

    context = {
        'titulo_pagina': 'Tienda de Textos Escolares',
        'productos': productos,
        'total_productos': len(productos),
        'editoriales': editoriales,
        'tipos_texto': categorias
    }
    
    return render_template('tienda_productos.html', **context)


# =================================================================
# 3. RUTAS API PARA COLEGIOS (CORREGIDA CON 'WITH')
# =================================================================
@app.route('/api/colegios', methods=['GET'])
def get_colegios_data():
    colegios_data = []
    
    # 1. Lista de KEYS que el JavaScript del cliente ESPERA (Mayúsculas)
    JSON_KEYS = [
        'id', 'COLEGIO', 'CIUDAD', 'IMAGEN', 'UBICACION', 
        'PREJARDIN', 'JARDIN', 'TRANSICION', 'PRIMERO', 'SEGUNDO', 
        'TERCERO', 'CUARTO', 'QUINTO', 'SEXTO', 'SEPTIMO', 
        'OCTAVO', 'NOVENO', 'DECIMO', 'ONCE'
    ]
    
    # 2. Lista de COLUMNAS SQL (Minúsculas para PostgreSQL por defecto)
    SQL_COLUMNS = [k.lower() for k in JSON_KEYS] 
    
    try:
        # **USO DE 'WITH' para asegurar el cierre de la conexión y cursor**
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                
                # Consulta: Usamos las columnas en minúscula para la consulta SQL
                query = f"SELECT {', '.join(SQL_COLUMNS)} FROM colegios ORDER BY colegio ASC;"
                cur.execute(query)
                
                # Mapea los resultados: Usamos JSON_KEYS (mayúsculas) como claves
                colegios_data = [dict(zip(JSON_KEYS, row)) for row in cur.fetchall()]
        
        return jsonify(colegios_data), 200

    except Exception as e:
        # Esto captura errores de conexión o errores en la consulta SQL
        print(f"Error FATAL al obtener la lista de colegios: {e}") 
        # Devolvemos el error 500 al cliente con más detalle
        return jsonify({"error": "Error interno del servidor al obtener datos de colegios", "detail": str(e)}), 500

# =================================================================
# 4. RUTAS PARA PÁGINAS ESTÁTICAS
# =================================================================

@app.route('/')
def index():
    return render_template('index.html')

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


if __name__ == '__main__':
    # Usar debug=True solo para desarrollo local
    app.run(host=HOST, port=PORT, debug=True)