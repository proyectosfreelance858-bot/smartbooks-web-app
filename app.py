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
DB_NAME = os.environ.get("DB_NAME", "smartbooks_db_duns") # Nombre de la DB según la imagen
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
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT]):
        print("ADVERTENCIA: Faltan variables de entorno de DB. Usando configuración por defecto.")
        return None

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            sslmode='require' if DB_HOST != 'localhost' else 'allow' 
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        return None

# =================================================================
# 2. SIMULACIÓN DE DATOS DE FALLBACK (Para usar si falla la DB)
# =================================================================

# Datos de colegios simulados (usando la estructura de la tabla colegios para ser coherente con el frontend)
SIMULATED_SCHOOLS = [
    {"ID_COLEGIO": 1, "COLEGIO": "Colegio Mayor del Sol", "CIUDAD": "Bogotá", "IMAGEN": "url_imagen_sol", "UBICACION": "https://maps.google.com/?q=Colegio+Mayor+del+Sol", "PREJARDIN": "Kit Preescolar A", "JARDIN": "Kit Preescolar A", "TRANSICION": "Kit Preescolar B", "PRIMERO": "Kit Primaria 1", "SEGUNDO": "Kit Primaria 2", "TERCERO": "Kit Primaria 3", "CUARTO": "0", "QUINTO": "0", "SEXTO": "Kit Bachillerato", "SEPTIMO": "Kit Bachillerato", "OCTAVO": "0", "NOVENO": "0", "DECIMO": "0", "ONCE": "0"},
    {"ID_COLEGIO": 2, "COLEGIO": "Instituto Británico", "CIUDAD": "Medellín", "IMAGEN": "url_imagen_britanico", "UBICACION": "https://maps.google.com/?q=Instituto+Británico", "PREJARDIN": "0", "JARDIN": "0", "TRANSICION": "Kit Cambridge Pre", "PRIMERO": "Kit Cambridge 1", "SEGUNDO": "Kit Cambridge 2", "TERCERO": "Kit Cambridge 3", "CUARTO": "Kit Cambridge 4", "QUINTO": "Kit Cambridge 5", "SEXTO": "Kit Bachillerato A, Kit Bachillerato B", "SEPTIMO": "Kit Bachillerato A, Kit Bachillerato B", "OCTAVO": "0", "NOVENO": "Kit IGCSE", "DECIMO": "Kit A-Levels", "ONCE": "Kit A-Levels"},
]

def simulate_package_data(school_id, grade_name):
    """Genera datos de paquete de libros simulados basados en el colegio y el curso."""
    base_price = 150000 
    
    if school_id == 2: base_price *= 1.2
    if grade_name.startswith("Pre"): base_price *= 0.7
    
    package_id = f"PK-{school_id}-{grade_name.replace(' ', '-').lower()}"
    
    books = [
        {"name": f"Matemáticas para {grade_name}", "author": "Dr. Álgebra", "isbn": "978-1234567890"},
        {"name": f"Lengua y Literatura de {grade_name}", "author": "A. Machado", "isbn": "978-0987654321"},
        {"name": f"Ciencias Naturales - Volumen I", "author": "B. Franklin", "isbn": "978-5555555555"},
    ]
    
    return {
        "package_id": package_id,
        "school_id": school_id,
        "grade": grade_name,
        "price_total": base_price + (len(books) * 5000), 
        "books_count": len(books),
        "books_list": books,
        "shipping_time": "3-5 días hábiles"
    }

# Datos de configuración (URLs) de fallback, si la DB falla.
FALLBACK_CONFIG_URLS = {
    "url_editorial1": "https://simulada.com/editorial1.png",
    "url_editorial2": "https://simulada.com/editorial2.png",
    "url_editorial3": "https://simulada.com/editorial3.png",
    "url_editorial4": "https://simulada.com/editorial4.png",
    "url_editorial5": "https://simulada.com/editorial5.png",
    "url_banner1": "https://simulada.com/banner1.png",
    "url_banner2": "https://simulada.com/banner2.png",
    "url_banner3": "https://simulada.com/banner3.png",
    "url_banner4": "https://simulada.com/banner4.png",
    "url_banner5": "https://simulada.com/banner5.png",
    "url_banner6": "https://simulada.com/banner6.png",
    "url_recuadro1": "https://simulada.com/recuadro1.png",
    "url_recuadro2": "https://simulada.com/recuadro2.png",
    "url_recuadro3": "https://simulada.com/recuadro3.png",
}

# Datos de productos destacados (basados en articulos_blog para estructura, pero simulando más de 5)
def get_simulated_featured_products(count=8):
    
    # Usando los datos de la tabla 'articulos_blog' de la imagen para simular la estructura
    base_products = [
        {"titulo": "Cómo elegir los mejores textos escolares: Guía para Coordinadores", "descripcion_corta": "Guía para directores y coordinadores que buscan calidad, alineación pedagógica y adaptabilidad.", "url_imagen": "https://simulada.com/libro1.png", "rating": 5, "precio": 149900, "categoria": "Guías Pedagógicas"},
        {"titulo": "Las Tendencias educativas que no puedes ignorar en 2024-2025", "descripcion_corta": "Análisis de nuestra alianza estratégica con una editorial líder para ofrecer programas bilingües.", "url_imagen": "https://simulada.com/libro2.png", "rating": 4, "precio": 99900, "categoria": "Artículos Blog"},
        {"titulo": "Smart Books y MacMillan: El futuro de la educación bilingüe", "descripcion_corta": "Descubre cómo los textos escolares están evolucionando hacia modelos híbridos que combinan papel y digital.", "url_imagen": "https://simulada.com/libro3.png", "rating": 5, "precio": 199900, "categoria": "Plataformas Digitales"},
        {"titulo": "Transformación Digital en el Aula: Plataformas y Libros Híbridos", "descripcion_corta": "Más allá del material, el éxito educativo depende del docente. Capacitación y herramientas de diagnóstico.", "url_imagen": "https://simulada.com/libro4.png", "rating": 4, "precio": 75900, "categoria": "Tecnología Educativa"},
        {"titulo": "El Rol del Docente: Más allá del Libro", "descripcion_corta": "Un debate sobre la importancia del libro y el papel de las asignaturas en el currículo moderno. Incluye recursos digitales.", "url_imagen": "https://simulada.com/libro5.png", "rating": 5, "precio": 125900, "categoria": "Desarrollo Docente"},
    ]

    simulated_products = []
    # Duplicar y modificar para tener al menos 'count' productos
    for i in range(count):
        product = base_products[i % len(base_products)].copy()
        product["titulo"] = f"{product['titulo']} (Edición {i+1})"
        product["precio"] = product["precio"] + (i * 1000)
        product["precio_formateado"] = f"${product['precio']:,}".replace(",", ".") # Formato de precio en español (e.g., $150.000)
        simulated_products.append(product)
        
    return simulated_products


# =================================================================
# 3. FUNCIONES DE BASE DE DATOS
# =================================================================

def get_config_urls_from_db(conn):
    """Obtiene las URLs de configuración de la tabla configuracion_web."""
    config_urls = {}
    try:
        with conn.cursor() as cur:
            sql_query = 'SELECT clave, valor FROM configuracion_web;'
            cur.execute(sql_query)
            for clave, valor in cur.fetchall():
                # El HTML usa nombres con guión bajo (url_banner1, url_editorial1)
                config_urls[clave.replace('-', '_')] = valor 
        return config_urls
    except Exception as e:
        print(f"Error al obtener URLs de configuracion_web: {e}")
        return {}


# =================================================================
# 4. RUTAS DE API (DATOS DINÁMICOS)
# =================================================================

@app.route('/api/colegios', methods=['GET'])
def get_colegios():
    """
    Ruta para obtener la lista de todos los colegios con sus kits de libros por grado.
    Intenta conectar a la DB real; si falla, usa datos simulados.
    """
    conn = get_db_connection()
    if conn is None:
        print("INFO: Usando datos simulados de colegios (Fallo de conexión a DB).")
        return jsonify(SIMULATED_SCHOOLS), 200

    try:
        with conn.cursor() as cur:
            # Selecciona todas las columnas relevantes de la tabla colegios. 
            # Se asume la estructura del HTML y JS (ID_COLEGIO, COLEGIO, CIUDAD, GRADOS...).
            sql_query = """
            SELECT 
                "ID_COLEGIO", "COLEGIO", "CIUDAD", "IMAGEN", "UBICACION",
                "PREJARDIN", "JARDIN", "TRANSICION", "PRIMERO", "SEGUNDO", 
                "TERCERO", "CUARTO", "QUINTO", "SEXTO", "SEPTIMO", 
                "OCTAVO", "NOVENO", "DECIMO", "ONCE"
            FROM 
                colegios
            ORDER BY 
                "COLEGIO";
            """
            cur.execute(sql_query)
            
            # Nombres de las columnas en el orden de la consulta
            column_names = [desc[0] for desc in cur.description]
            
            colegios_data = []
            for row in cur.fetchall():
                # Crear un diccionario mapeando los nombres de columna a los valores de la fila
                school_data = dict(zip(column_names, row))
                # Limpiar valores NULL si los hay (psycopg2 devuelve None, lo que es seguro en JSON)
                for key, value in school_data.items():
                    if value is None:
                        # Asume '0' para grados sin kit y cadena vacía para otros campos NULL
                        school_data[key] = "0" if key in ["PREJARDIN", "JARDIN", "TRANSICION", "PRIMERO", "SEGUNDO", "TERCERO", "CUARTO", "QUINTO", "SEXTO", "SEPTIMO", "OCTAVO", "NOVENO", "DECIMO", "ONCE"] else ""
                
                colegios_data.append(school_data)
        
        conn.close()
        
        if not colegios_data:
            print("INFO: DB conectada pero la consulta SQL de colegios no devolvió resultados. Usando datos simulados.")
            return jsonify(SIMULATED_SCHOOLS), 200

        return jsonify(colegios_data), 200

    except Exception as e:
        print(f"Error FATAL al obtener la lista de colegios: {e}") 
        # Fallback a datos simulados en caso de error grave
        return jsonify(SIMULATED_SCHOOLS), 200 # Devuelve 200 OK con datos simulados

@app.route('/api/paquete', methods=['GET'])
def get_course_package():
    """
    Ruta para obtener el paquete de libros específico para un colegio y curso.
    Solo usa datos simulados por la complejidad de la búsqueda real.
    """
    school_id_str = request.args.get('school_id')
    grade_name = request.args.get('grade_name') # Nombre del grado (ej. '1° (Primero)')

    if not school_id_str or not grade_name:
        return jsonify({"error": "Parámetros 'school_id' y 'grade_name' son requeridos."}), 400

    try:
        school_id = int(school_id_str)
    except ValueError:
        return jsonify({"error": "El 'school_id' debe ser un número entero válido."}), 400

    # Usar simulación de datos (Mock de búsqueda de libros específicos)
    package_data = simulate_package_data(school_id, grade_name)

    if package_data:
        return jsonify(package_data), 200
    else:
        return jsonify({"error": "No se encontró un paquete de libros para la selección."}), 404

# =================================================================
# 5. RUTAS PARA PÁGINAS ESTÁTICAS
# =================================================================
# NOTA: Estas rutas requieren que tengas los templates (.html) correspondientes 
# en la carpeta 'templates' de tu aplicación Flask.

@app.route('/')
def index():
    """
    Ruta principal. Obtiene URLs de configuración y productos destacados.
    """
    config_urls = {}
    
    conn = get_db_connection()
    if conn is not None:
        # 1. Obtener URLs de configuracion_web
        config_urls = get_config_urls_from_db(conn)
        conn.close()
    
    # 2. Fallback si no hay URLs o falla la DB
    if not config_urls:
        print("INFO: Usando URLs simuladas (Fallo en DB o datos vacíos).")
        config_urls = FALLBACK_CONFIG_URLS


    # 3. Obtener productos destacados simulados (para el carrusel de productos)
    productos_destacados = get_simulated_featured_products(count=8)

    # 4. Renderizar el template con todos los datos
    return render_template(
        'index.html', 
        **config_urls, # Pasa todas las URLs como argumentos individuales (url_banner1=..., etc.)
        productos_destacados=productos_destacados
    ) 

@app.route('/quienes-somos')
def quienes_somos():
    return render_template('QuienesSomos.html') 

@app.route('/terminos-y-condiciones')
def terminos_y_condiciones():
    return render_template('TerminosYCondiciones.html')

@app.route('/preguntas-frecuentes')
def preguntas_frecuentes():
    return render_template('PreguntasFrecuentes.html')

@app.route('/aliados/castillo')
def aliados_castillo():
    # Asume que tienes un template 'AliadosCastillo.html'
    return "Página de Aliados: Castillo (Requiere Template)"

@app.route('/aliados/macmillan')
def aliados_macmillan():
    # Asume que tienes un template 'AliadosMacmillan.html'
    return "Página de Aliados: MacMillan (Requiere Template)"

@app.route('/tienda')
def tienda():
    # Asume que tienes un template 'Tienda.html'
    return render_template('Tienda.html')

@app.route('/colegios')
def colegios():
    return render_template('Colegios.html')

@app.route('/contactanos')
def contactanos():
    return render_template('Contactanos.html')

@app.route('/intranet')
def intranet():
    # Asume que tienes un template 'Intranet.html'
    return render_template('Intranet.html')

@app.route('/blog')
def blog():
    return render_template('Blog.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# =================================================================
# 6. INICIALIZACIÓN
# =================================================================

if __name__ == '__main__':
    print(f"Flask corriendo en http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)