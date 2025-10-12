import os
from flask import Flask, render_template
import psycopg2
from psycopg2 import OperationalError

# Inicialización de la aplicación Flask
app = Flask(__name__)

# ==========================================================
# FUNCIONES DE DATOS Y CONEXIÓN A POSTGRESQL
# ==========================================================

# Datos de respaldo (fallback) en caso de que la conexión a la DB falle
def get_fallback_data():
    """Retorna un diccionario de datos si la base de datos no está disponible."""
    print("--- Usando datos de respaldo (FALLBACK DATA) ---")
    return {
        # BANNERS
        "url_banner1": "https://i.ibb.co/1DN94s7/banner1.jpg",
        "url_banner2": "https://i.ibb.co/pvKfq0p9/banner2.png",
        "url_banner3": "/static/images/banner_lateral.jpg",
        "url_banner4": "/static/images/banner_inferior.jpg",

        # PRODUCTOS
        "txt_productosmasvendidos1": "PAQUETE DE INGLÉS Cosmo – 2°",
        "txt_productosmasvendidos2": "PAQUETE DE INGLÉS Cosmo – 1°",
        "txt_productosmasvendidos3": "EL PAN DE LA GUERRA",
        "txt_productosmasvendidos4": "LA GACETA DE LANDRY", 
        "url_productosmasvendidos1": "https://sbooks.com.co/wp-content/uploads/2022/12/4-300x300.png",
        "url_productosmasvendidos2": "https://sbooks.com.co/wp-content/uploads/2022/12/3-300x300.png",
        "url_productosmasvendidos3": "https://sbooks.com.co/wp-content/uploads/2022/11/EL-PAN-DE-LA-GUERRA-199x300.png",
        "url_productosmasvendidos4": "https://sbooks.com.co/wp-content/uploads/2022/11/LA-GACETA-DE-LANDRY-200x300.png",

        # EDITORIALES
        "url_editorial1": "https://sbooks.com.co/wp-content/uploads/2022/11/logo_MacMillanresized.webp",
        "url_editorial2": "https://sbooks.com.co/wp-content/uploads/2022/11/logo_Alpharesized.webp",
        "url_editorial3": "https://sbooks.com.co/wp-content/uploads/2023/09/Ediciones-Color-2.png",
        "url_editorial4": "https://sbooks.com.co/wp-content/uploads/2024/10/CLE-LOGO.png",
        "url_editorial5": "https://sbooks.com.co/wp-content/uploads/2024/10/SCHOLASTIC-LOGO.png",
        
        # RECUADROS
        'url_recuadro1': 'https://sbooks.com.co/wp-content/uploads/2023/10/feliz-colegiala-adolescente-disfrutando-libro-2048x1365.jpg',
        'txt_trecuadro1': '¡La escuela se transforma y la manera de elegir también!',
        'txt_recuadro1': 'Conoce y decide es el espacio seguro para revisar y decidir por el proyecto didáctico que apoye a tus alumnos. Desde casa, conoce nuestro catálogo de Plan Lector, contáctanos y uno de nuestros representantes estará dispuesto a brindarte toda la asesoría que necesites.',
        'url_recuadro2': 'https://scontent-bog2-2.xx.fbcdn.net/v/t51.75761-15/466804452_18121734811396677_4516505954897104926_n.jpg?_nc_cat=106&ccb=1-7&_nc_sid=127cfc&_nc_ohc=FyEzIAmkdi0Q7kNvwFDLg1_&_nc_oc=AdmdIW-Y04jEh0QmeOLXDW848AdhLmHTawrl1JGQhRSxWkHVPKG6cGhDgkQM-uGgSTE&_nc_zt=23&_nc_ht=scontent-bog2-2.xx&_nc_gid=C0OvuGXiLYQ57rVjgm0Kbg&oh=00_AfckN3_4HyS21GJ_IACyHAVI3IqFZvgbScu_2AwBv5HnaA&oe=68F1B772',
        'txt_trecuadro2': 'Más que libros, soluciones',
        'txt_recuadro2': 'En Smart Books, no solo ofrecemos libros, sino soluciones que abren las puertas al conocimiento y el aprendizaje.',
        'url_recuadro3': 'https://sbooks.com.co/wp-content/uploads/2023/10/Mesa-de-trabajo-1@4x.png', 
        'txt_trecuadro3': '¡Nuevo Programa Académico! para la Educación',
        'txt_recuadro3': 'ADVANCING FUTURES, es un programa integral diseñado para introducir los temas de ciudadanía global, sostenibilidad, diversidad, equidad e inclusión en las aulas de todo el mundo. Involucra a los estudiantes con elementos clave de los Objetivos de Desarrollo Sostenible de las Naciones Unidas y los capacita para trabajar por un futuro más justo y sostenible.'
    }


def get_db_data():
    """Intenta conectar a la DB y retorna los datos de configuracion_web."""
    # En Render, la URL de la base de datos se proporciona típicamente como una variable de entorno.
    # Usamos una URL de ejemplo si no está disponible (para desarrollo local).
    db_url = os.environ.get("DATABASE_URL")
    
    # Si no hay URL de DB configurada, forzamos los datos de respaldo
    if not db_url:
        print("ADVERTENCIA: No se encontró la variable de entorno DATABASE_URL.")
        return get_fallback_data()

    data = {}
    conn = None
    try:
        # Conecta a la base de datos usando la URL de Render/PostgreSQL
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Consulta la tabla de configuración que creamos (clave, valor)
        cur.execute("SELECT clave, valor FROM configuracion_web;")
        
        # Construye el diccionario a partir de los resultados
        for clave, valor in cur.fetchall():
            data[clave] = valor

        cur.close()
        
    except OperationalError as e:
        print(f"ERROR DE CONEXIÓN/CONSULTA: {e}")
        # Si la conexión falla, usa los datos de respaldo.
        return get_fallback_data()
    
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return get_fallback_data()
        
    finally:
        if conn:
            conn.close()

    return data


# ==========================================================
# RUTAS DE LA APLICACIÓN
# ==========================================================

@app.route("/")
def index():
    """Ruta principal que carga los datos de la DB y renderiza la plantilla."""
    
    # Intenta obtener los datos de la DB. Si falla, usa los de respaldo.
    db_data = get_db_data()
    
    # El operador **db_data desempaqueta el diccionario como argumentos
    # de palabra clave para render_template (ej: url_banner1=valor, etc.)
    return render_template("index.html", **db_data)


# ==========================================================
# INICIO DEL SERVIDOR (CRÍTICO PARA RENDER)
# ==========================================================

if __name__ == "__main__":
    # Usa la variable de entorno PORT proporcionada por Render (producción)
    # o 5000 por defecto (desarrollo local)
    port = int(os.environ.get("PORT", 5000))
    
    # Ejecuta el servidor en todas las interfaces ('0.0.0.0')
    # lo cual es un requisito para los hosts de producción como Render.
    app.run(host='0.0.0.0', port=port, debug=True)