import os
import sys
from flask import Flask, render_template, jsonify, request
import psycopg2 
from psycopg2 import extras
from datetime import datetime
from dotenv import load_dotenv

# =================================================================
# 0. CONFIGURACIÓN INICIAL Y AMBIENTE
# =================================================================

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la base de datos y el servidor
DB_HOST = os.environ.get("DB_HOST", "localhost") 
DB_NAME = os.environ.get("DB_NAME", "smartbooks_db_duns") 
DB_USER = os.environ.get("DB_USER", "tu_usuario_postgres") 
DB_PASS = os.environ.get("DB_PASS", "tu_contraseña_postgres") 
DB_PORT = os.environ.get("DB_PORT", "5432") 

# Configuración del hosting (necesario para Render/Heroku)
PORT = int(os.environ.get('PORT', 5000))
HOST = '0.0.0.0' 

# Inicialización de la aplicación Flask
app = Flask(__name__)

# =================================================================
# 1. UTILIDADES Y CONEXIÓN A LA BASE DE DATOS
# =================================================================

def get_db_connection():
    """
    Intenta establecer la conexión a la base de datos PostgreSQL.
    Configura el modo SSL para conexiones remotas (ej. Render).
    """
    conn = None
    try:
        # Configuración SSL para Render u otros servicios en la nube
        sslmode = 'require' if 'RENDER' in os.environ else 'disable'

        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            sslmode=sslmode
        )
        return conn
    except psycopg2.Error as e:
        print(f"ERROR: No se pudo conectar a la base de datos: {e}", file=sys.stderr)
        # Esto puede ser un error fatal en la inicialización
        # En un entorno real, se debería manejar mejor.
        return None

# =================================================================
# 2. RUTAS PRINCIPALES (VISTAS)
# =================================================================

@app.route('/')
def home():
    """Ruta para la página de inicio."""
    return render_template('index.html')

@app.route('/quienes-somos')
def about():
    """Ruta para la página 'Quiénes Somos'."""
    return render_template('Quienes_somos.html')

@app.route('/terminos-y-condiciones')
def terms():
    """Ruta para la página de términos y condiciones."""
    return render_template('Terminos_y_condiciones.html')

@app.route('/preguntas-frecuentes')
def faq():
    """Ruta para la página de preguntas frecuentes."""
    return render_template('Preguntas_frecuentes.html')

@app.route('/aliados/<aliado_slug>')
def allied(aliado_slug):
    """Ruta para las páginas de aliados."""
    # En un entorno real, esto se usaría para cargar contenido específico
    return render_template('Aliado.html', aliado=aliado_slug)

@app.route('/tienda')
def store():
    """Ruta para la página de la tienda (catálogo principal)."""
    return render_template('Tienda.html')

@app.route('/colegios')
def schools():
    """Ruta para la página de búsqueda de colegios."""
    return render_template('Colegios.html')

@app.route('/contactanos')
def contact():
    """Ruta para la página de contacto."""
    return render_template('Contactanos.html')

@app.route('/intranet')
def intranet():
    """Ruta para la Intranet."""
    return render_template('Intranet.html')

@app.route('/blog')
def blog():
    """Ruta para la página del blog."""
    # En un entorno real, esta ruta cargaría la lista de articulos_blog
    return render_template('Blog.html')

# =================================================================
# 3. RUTAS DE API: COLEGIOS (GET)
# =================================================================

@app.route('/api/colegios', methods=['GET'])
def get_colegios():
    """
    API para obtener la lista completa de colegios.
    Se requiere el campo 'IMAGEN' para el front-end de colegios.
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Se asume una tabla 'colegios' con los campos necesarios
        query = """
        SELECT 
            id_colegio, 
            colegio, 
            ciudad, 
            ubicacion,
            -- Asumimos que la URL de la imagen del colegio está aquí
            url_imagen AS imagen, 
            prejardin, jardin, transicion,
            primero, segundo, tercero, cuarto, quinto, 
            sexto, septimo, octavo, noveno, decimo, once
        FROM colegios
        ORDER BY colegio;
        """
        cur.execute(query)
        colegios = cur.fetchall()
        cur.close()
        conn.close()

        # Conversión a lista de diccionarios JSON serializables
        colegios_list = [dict(colegio) for colegio in colegios]
        
        # Corrección: asegurar que los valores NULL se muestren como "0" o cadena vacía en el JSON
        # para que el frontend (Colegios.html) los maneje correctamente.
        clean_colegios_list = []
        for colegio in colegios_list:
            clean_colegio = {}
            for key, value in colegio.items():
                # Reemplazar None/NULL en campos de grados por '0' para el frontend
                if key.upper() in ['PREJARDIN', 'JARDIN', 'TRANSICION', 'PRIMERO', 'SEGUNDO', 'TERCERO', 'CUARTO', 
                                   'QUINTO', 'SEXTO', 'SEPTIMO', 'OCTAVO', 'NOVENO', 'DECIMO', 'ONCE'] and value is None:
                    clean_colegio[key] = '0'
                elif value is None:
                    clean_colegio[key] = ''
                else:
                    clean_colegio[key] = value
            clean_colegios_list.append(clean_colegio)

        return jsonify(clean_colegios_list), 200

    except psycopg2.Error as e:
        print(f"ERROR DB en /api/colegios: {e}", file=sys.stderr)
        return jsonify({"error": "Error al consultar la base de datos de colegios"}), 500
    except Exception as e:
        print(f"ERROR inesperado en /api/colegios: {e}", file=sys.stderr)
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route('/api/paquete', methods=['GET'])
def get_paquete_educativo():
    """
    API para obtener el kit educativo específico para un colegio y grado.
    El frontend (Colegios.html) normalmente llamaría a esta ruta.
    """
    colegio_id = request.args.get('id_colegio')
    grado_key = request.args.get('grado') # Ejemplo: 'PRIMERO', 'TRANSICION'

    if not colegio_id or not grado_key:
        return jsonify({"error": "Faltan parámetros: id_colegio y grado"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Validar que el grado_key sea una columna válida para prevenir SQL Injection
        valid_grades = ['prejardin', 'jardin', 'transicion', 'primero', 'segundo', 'tercero', 
                        'cuarto', 'quinto', 'sexto', 'septimo', 'octavo', 'noveno', 'decimo', 'once']
        if grado_key.lower() not in valid_grades:
            return jsonify({"error": "Grado no válido"}), 400

        # Query parametrizada para seleccionar el campo de grado específico
        query = f"""
        SELECT 
            colegio, 
            ciudad, 
            ubicacion, 
            url_imagen AS imagen,
            {grado_key.lower()} AS paquete_info
        FROM colegios
        WHERE id_colegio = %s;
        """
        cur.execute(query, (colegio_id,))
        paquete = cur.fetchone()
        cur.close()
        conn.close()

        if paquete:
            paquete_dict = dict(paquete)
            paquete_info = paquete_dict.get('paquete_info')
            
            # Si no hay paquete específico (valor es '0' o None), devuelve error
            if paquete_info is None or str(paquete_info).strip() in ['0', 'NULL', '']:
                return jsonify({"error": f"No hay kit educativo registrado para el grado {grado_key} en el colegio {paquete_dict.get('colegio')}"}), 404

            # Generar una cantidad de libros random entre 4 y 7 para el front-end
            import random
            random_book_count = random.randint(4, 7)

            response = {
                "colegio": paquete_dict.get('colegio'),
                "ciudad": paquete_dict.get('ciudad'),
                "ubicacion": paquete_dict.get('ubicacion'),
                "imagen": paquete_dict.get('imagen'),
                "grado": grado_key,
                "paquete_info": paquete_info,
                "cantidad_libros": random_book_count
            }

            return jsonify(response), 200
        else:
            return jsonify({"error": f"Colegio con ID {colegio_id} no encontrado"}), 404

    except psycopg2.Error as e:
        print(f"ERROR DB en /api/paquete: {e}", file=sys.stderr)
        return jsonify({"error": "Error al consultar la base de datos"}), 500
    except Exception as e:
        print(f"ERROR inesperado en /api/paquete: {e}", file=sys.stderr)
        return jsonify({"error": "Error interno del servidor"}), 500

# =================================================================
# 4. RUTAS DE API: TIENDA (ARTÍCULOS) (GET)
# =================================================================

@app.route('/api/articulos', methods=['GET'])
def get_articulos():
    """
    API para obtener los artículos de la tienda (catálogo principal).
    Incluye la CORRECCIÓN para la 'url_imagen_principal'.
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Se asume una tabla 'articulos_tienda' con los campos que necesitas
        query = """
        SELECT 
            id_articulo, 
            titulo, 
            descripcion_corta, 
            precio, 
            categoria,
            -- CORRECCIÓN: Seleccionar el campo de la imagen
            url_imagen_principal
        FROM articulos_tienda
        WHERE activo = TRUE
        ORDER BY id_articulo DESC;
        """
        cur.execute(query)
        articulos = cur.fetchall()
        cur.close()
        conn.close()

        articulos_list = []
        for articulo in articulos:
            articulo_dict = dict(articulo)
            # Asegurar que el campo se incluye
            articulo_dict['url_imagen_principal'] = articulo_dict.get('url_imagen_principal') or 'https://sbooks.com.co/wp-content/uploads/2024/12/no-image.png'
            
            # Convertir precio a float si es necesario
            try:
                articulo_dict['precio'] = float(articulo_dict['precio'])
            except (ValueError, TypeError):
                articulo_dict['precio'] = 0.0
                
            articulos_list.append(articulo_dict)

        return jsonify(articulos_list), 200

    except psycopg2.Error as e:
        print(f"ERROR DB en /api/articulos: {e}", file=sys.stderr)
        return jsonify({"error": "Error al consultar la base de datos de artículos"}), 500
    except Exception as e:
        print(f"ERROR inesperado en /api/articulos: {e}", file=sys.stderr)
        return jsonify({"error": "Error interno del servidor"}), 500


# =================================================================
# 5. RUTAS DE API: CONTACTO (POST)
# =================================================================

@app.route('/api/contacto', methods=['POST'])
def handle_contacto():
    """
    API para manejar el envío del formulario de contacto.
    Inserta los datos en la tabla 'contactos'.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos JSON no proporcionados"}), 400

    # Campos esperados
    nombre = data.get('nombre')
    email = data.get('email')
    telefono = data.get('telefono')
    asunto = data.get('asunto')
    mensaje = data.get('mensaje')
    
    if not all([nombre, email, asunto, mensaje]):
        return jsonify({"error": "Faltan campos obligatorios (nombre, email, asunto, mensaje)"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        cur = conn.cursor()
        query = """
        INSERT INTO contactos (nombre, email, telefono, asunto, mensaje, fecha_contacto)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        fecha_contacto = datetime.now()
        cur.execute(query, (nombre, email, telefono, asunto, mensaje, fecha_contacto))
        conn.commit()
        cur.close()
        conn.close()
        
        # En un entorno real, aquí se enviaría un email de notificación
        print(f"Contacto recibido: {nombre} - {email}", file=sys.stderr)

        return jsonify({"message": "Mensaje enviado con éxito. Pronto te contactaremos.", "status": "success"}), 201

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR DB al insertar contacto: {e}", file=sys.stderr)
        return jsonify({"error": "Error al guardar el mensaje. Intenta de nuevo más tarde."}), 500
    except Exception as e:
        print(f"ERROR inesperado en /api/contacto: {e}", file=sys.stderr)
        return jsonify({"error": "Error interno del servidor al procesar tu solicitud."}), 500


# =================================================================
# 6. MANEJO DE ERRORES GLOBAL
# =================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Manejo de la página no encontrada (404)."""
    print(f"ERROR: Ruta no encontrada: {request.url}", file=sys.stderr)
    # Asume que existe un template 404.html
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Manejo de errores internos del servidor (500)."""
    print(f"ERROR: Error interno del servidor: {e}", file=sys.stderr)
    # Asume que existe un template 500.html
    return render_template('500.html'), 500

# =================================================================
# 7. INICIALIZACIÓN DEL SERVIDOR
# =================================================================

if __name__ == '__main__':
    # Mensaje de inicio para el entorno local
    print("=====================================================")
    print("  Smart Books Flask Server Inicializando")
    print("=====================================================")
    print(f"  HOST: {HOST}, PORT: {PORT}")
    print(f"  DB: {DB_NAME}@{DB_HOST}:{DB_PORT} (User: {DB_USER})")
    
    # Intento de conexión inicial (opcional, pero ayuda a detectar fallos tempranos)
    if get_db_connection() is not None:
         print("  Conexión a DB: Exitosa.")
    else:
         print("  Conexión a DB: FALLÓ. Revisar variables de entorno.")
    
    print("=====================================================")

    # Iniciar la aplicación Flask
    # Nota: use_reloader=False es útil si tienes problemas de doble inicio en algunos entornos
    app.run(host=HOST, port=PORT, debug=True)