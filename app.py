import os
from flask import Flask, render_template, jsonify, request
# Se recomienda usar un ORM o al menos una capa de abstracción para la DB, 
# pero mantendremos psycopg2 ya que estaba en el código original.
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
        print("ADVERTENCIA: Faltan variables de entorno de DB. Usando configuración por defecto.")
        # Simular fallo de conexión si no están definidas las variables
        return None

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            # CRUCIAL para hosting en plataformas como Render:
            sslmode='require' if DB_HOST != 'localhost' else 'allow' 
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        return None

# =================================================================
# 2. SIMULACIÓN DE DATOS (PARA FUNCIONALIDAD SIN DB ACTIVA)
# =================================================================

# Datos de colegios simulados para uso si la DB falla
SIMULATED_SCHOOLS = [
    {"ID_COLEGIO": 1, "COLEGIO": "Colegio Mayor del Sol", "GRADES": ["6º Grado", "7º Grado", "8º Grado"]},
    {"ID_COLEGIO": 2, "COLEGIO": "Instituto Británico", "GRADES": ["9º Grado", "10º Grado", "11º Grado"]},
    {"ID_COLEGIO": 3, "COLEGIO": "Liceo Moderno Artesano", "GRADES": ["Preescolar", "1º Grado", "2º Grado"]},
    {"ID_COLEGIO": 4, "COLEGIO": "Gimnasio Los Robles", "GRADES": ["6º Grado", "7º Grado", "8º Grado", "9º Grado", "10º Grado", "11º Grado"]},
]

# Simulación de datos de paquetes de libros
def simulate_package_data(school_id, grade_name):
    """Genera datos de paquete de libros simulados basados en el colegio y el curso."""
    base_price = 150000 
    
    # Ajustar precio base ligeramente
    if school_id == 2: base_price *= 1.2
    if grade_name.startswith("Pre"): base_price *= 0.7
    
    # Generar un ID basado en el hash de los inputs
    package_id = f"PK-{school_id}-{grade_name.replace(' ', '-').lower()}"
    
    # Generar lista de libros
    books = [
        {"name": f"Matemáticas para {grade_name}", "author": "Dr. Álgebra", "isbn": "978-1234567890"},
        {"name": f"Lengua y Literatura de {grade_name}", "author": "A. Machado", "isbn": "978-0987654321"},
        {"name": f"Ciencias Naturales - Volumen I", "author": "B. Franklin", "isbn": "978-5555555555"},
    ]
    
    return {
        "package_id": package_id,
        "school_id": school_id,
        "grade": grade_name,
        "price_total": base_price + (len(books) * 5000), # Precio final simulado
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
    Ruta para obtener la lista de todos los colegios y sus cursos.
    Intenta conectar a la DB real; si falla, usa datos simulados.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            # Fallback a datos simulados si la conexión a la DB falla
            print("INFO: Usando datos simulados de colegios (Fallo de conexión a DB).")
            return jsonify(SIMULATED_SCHOOLS), 200

        with conn.cursor() as cur:
            # Consulta SQL optimizada que asume una estructura de tabla COLEGIO_CURSO
            # Adaptar esto a la estructura real de tu DB si es necesario.
            # Aquí se simula la obtención de colegios y la agrupación de sus cursos.
            sql_query = """
            SELECT 
                c.id_colegio, 
                c.colegio, 
                ARRAY_AGG(DISTINCT cr.curso ORDER BY cr.curso) AS grados
            FROM 
                colegios c
            JOIN 
                cursos_colegios cc ON c.id_colegio = cc.colegio_id
            JOIN 
                cursos cr ON cc.curso_id = cr.id_curso
            GROUP BY 
                c.id_colegio, c.colegio
            ORDER BY 
                c.colegio;
            """
            cur.execute(sql_query)
            
            # Mapear los resultados a un formato JSON
            colegios_data = []
            for id_colegio, nombre_colegio, grados in cur.fetchall():
                 # Los grados ya están como un array de strings gracias a ARRAY_AGG
                colegios_data.append({
                    "ID_COLEGIO": id_colegio,
                    "COLEGIO": nombre_colegio,
                    "GRADES": grados  
                })
        
        conn.close()
        
        # Si la consulta SQL no devuelve nada, se puede volver al fallback simulado
        if not colegios_data:
            print("INFO: DB conectada pero la consulta SQL de colegios no devolvió resultados. Usando datos simulados.")
            return jsonify(SIMULATED_SCHOOLS), 200

        return jsonify(colegios_data), 200

    except Exception as e:
        # Esto captura errores de conexión o errores en la consulta SQL
        print(f"Error FATAL al obtener la lista de colegios: {e}") 
        # Fallback a datos simulados en caso de error grave
        return jsonify(SIMULATED_SCHOOLS), 200 # Devuelve 200 OK con datos simulados

@app.route('/api/paquete', methods=['GET'])
def get_course_package():
    """
    Ruta para obtener el paquete de libros específico para un colegio y curso.
    Requiere 'school_id' y 'grade_name' como parámetros de consulta.
    """
    school_id_str = request.args.get('school_id')
    grade_name = request.args.get('grade_name')

    if not school_id_str or not grade_name:
        return jsonify({"error": "Parámetros 'school_id' y 'grade_name' son requeridos."}), 400

    try:
        school_id = int(school_id_str)
    except ValueError:
        return jsonify({"error": "El 'school_id' debe ser un número entero válido."}), 400

    # 1. Intentar buscar en la base de datos real (SIMULACIÓN DE DB)
    # En un entorno real, harías una consulta a la DB aquí.
    # Por ahora, usamos la simulación.

    # 2. Usar simulación de datos
    package_data = simulate_package_data(school_id, grade_name)

    if package_data:
        return jsonify(package_data), 200
    else:
        # Este caso es improbable con la función simulate_package_data, pero es buena práctica.
        return jsonify({"error": "No se encontró un paquete de libros para la selección."}), 404

# =================================================================
# 4. RUTAS PARA PÁGINAS ESTÁTICAS
# =================================================================

@app.route('/')
def index():
    # Asume que tienes un template 'index.html'
    return render_template('index.html') 

@app.route('/quienes-somos')
def quienes_somos():
    # Asume que tienes un template 'QuienesSomos.html'
    return render_template('QuienesSomos.html') 

@app.route('/terminos-y-condiciones')
def terminos_y_condiciones():
    # Asume que tienes un template 'TerminosYCondiciones.html'
    return render_template('TerminosYCondiciones.html')

@app.route('/preguntas-frecuentes')
def preguntas_frecuentes():
    # Asume que tienes un template 'PreguntasFrecuentes.html'
    return render_template('PreguntasFrecuentes.html')

@app.route('/colegios')
def colegios():
    # Esta ruta sirve la página con la lógica principal
    return render_template('Colegios.html')

@app.route('/contactanos')
def contactanos():
    # Asume que tienes un template 'Contactanos.html'
    return render_template('Contactanos.html')

@app.route('/blog')
def blog():
    # Asume que tienes un template 'Blog.html'
    return render_template('Blog.html')

@app.errorhandler(404)
def page_not_found(e):
    # Asume que tienes un template '404.html'
    return render_template('404.html'), 404

# =================================================================
# 5. INICIALIZACIÓN
# =================================================================

if __name__ == '__main__':
    # Usar el puerto configurado y el host 0.0.0.0 para ser accesible en contenedores/hosting
    print(f"Flask corriendo en http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)
