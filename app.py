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
# 2. SIMULACIÓN DE DATOS DE FALLBACK
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

# =================================================================
# 3. RUTAS DE API (DATOS DINÁMICOS)
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
# 4. RUTAS PARA PÁGINAS ESTÁTICAS
# =================================================================
# NOTA: Estas rutas requieren que tengas los templates (.html) correspondientes 
# en la carpeta 'templates' de tu aplicación Flask.

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
# 5. INICIALIZACIÓN
# =================================================================

if __name__ == '__main__':
    print(f"Flask corriendo en http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)