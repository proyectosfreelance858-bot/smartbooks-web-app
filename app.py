import os
import psycopg2
from flask import Flask, render_template

# --- Inicialización de Flask ---
app = Flask(__name__)

# --- Configuración de la Base de Datos PostgreSQL ---
# ¡IMPORTANTE! Reemplaza estos valores con tus credenciales reales
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "smartbooks_db") # Ejemplo: tu_nombre_db
DB_USER = os.environ.get("DB_USER", "postgres")    # Ejemplo: tu_usuario_db
DB_PASS = os.environ.get("DB_PASS", "tu_password")  # Ejemplo: tu_password_db


def get_db_connection():
    """Establece la conexión con PostgreSQL."""
    # Nota: Se recomienda encarecidamente usar un pool de conexiones en producción.
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

def get_latest_blogs():
    """Obtiene los 3 artículos de blog más recientes."""
    conn = None
    blogs = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Consulta SQL para obtener los 3 más recientes
        cur.execute(
            """
            SELECT titulo, slug, descripcion_corta, url_imagen_principal, fecha_creacion
            FROM articulos_blog
            ORDER BY fecha_creacion DESC 
            LIMIT 3;
            """
        )
        
        # Mapea los resultados del cursor a una lista de diccionarios (útil para Jinja)
        columns = [desc[0] for desc in cur.description]
        blogs = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        cur.close()
    except Exception as e:
        print(f"Error al conectar o consultar la base de datos: {e}")
        # En caso de error, retorna una lista vacía para que la página no falle
        blogs = []
    finally:
        if conn is not None:
            conn.close()
    return blogs

# --- Filtro Jinja para formatear la fecha ---
def format_date(value):
    """Formatea un objeto datetime a 'DD Mes YYYY'"""
    if value:
        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }
        day = value.day
        month = meses[value.month]
        year = value.year
        return f"{day} {month} {year}"
    return ""

app.jinja_env.filters['date_format'] = format_date

# --- Rutas de la Aplicación ---
@app.route('/')
def index():
    # 1. Obtener los 3 blogs
    latest_blogs = get_latest_blogs()
    
    # 2. Renderizar el HTML y pasar la lista de blogs
    return render_template('index.html', latest_blogs=latest_blogs)

# --- Ejecución ---
if __name__ == '__main__':
    # Usar host='0.0.0.0' para desarrollo y pruebas locales
    app.run(debug=True, host='0.0.0.0')