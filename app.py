import os
from flask import Flask, render_template
import psycopg2
from datetime import datetime

# =================================================================
# 1. CONFIGURACIÓN DE BASE DE DATOS Y HOSTING
# Obtiene las credenciales de las variables de entorno (Render/Hosting) 
# o usa valores por defecto (localhost) si no las encuentra.
# =================================================================
DB_HOST = os.environ.get("DB_HOST", "localhost") 
DB_NAME = os.environ.get("DB_NAME", "nombre_de_tu_base_de_datos") 
DB_USER = os.environ.get("DB_USER", "tu_usuario_postgres") 
DB_PASS = os.environ.get("DB_PASS", "tu_contraseña_postgres") 

# Configuración de puerto y host para Render
PORT = int(os.environ.get('PORT', 5000))
HOST = '0.0.0.0' 

app = Flask(__name__)

def get_db_connection():
    """Intenta establecer la conexión a la base de datos PostgreSQL."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

@app.route('/')
def index():
    blogs = []
    productos = [] # Nueva lista para productos
    conn = None
    
    # --- 2. INTENTO DE CONEXIÓN Y CONSULTA DE LA DB ---
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Consulta para obtener los 8 artículos del blog más recientes (MODIFICADO a LIMIT 8)
        sql_query_blogs = """
            SELECT 
                id, 
                titulo, 
                descripcion_corta, 
                url_imagen_principal, 
                fecha_creacion, 
                slug 
            FROM 
                articulos_blog 
            ORDER BY 
                fecha_creacion DESC 
            LIMIT 8; 
        """
        cur.execute(sql_query_blogs)
        db_blogs = cur.fetchall()
        
        # Consulta para obtener 4 productos más vendidos (NUEVA CONSULTA)
        sql_query_productos = """
            SELECT 
                titulo, 
                sku, 
                categoria, 
                precio, 
                url_imagen 
            FROM 
                productos_escolares 
            LIMIT 4; 
        """
        cur.execute(sql_query_productos)
        db_productos = cur.fetchall()
        
        # Formatear datos de BLOGS para Jinja2
        for blog_data in db_blogs:
            (id, titulo, descripcion_corta, url_imagen_principal, fecha_creacion, slug) = blog_data
            
            # Formateo de Fecha
            fecha_formateada = fecha_creacion.strftime("%d %b, %Y")
            meses_espanol = {'Jan': 'Ene', 'Apr': 'Abr', 'Aug': 'Ago', 'Dec': 'Dic'}
            for en, es in meses_espanol.items():
                fecha_formateada = fecha_formateada.replace(en, es)
            
            imagen_url = url_imagen_principal
            if not imagen_url or not imagen_url.strip():
                imagen_url = 'https://via.placeholder.com/600x400.png?text=Smart+Books+Blog'

            blogs.append({
                'id': id,
                'titulo': titulo,
                'url_imagen_principal': imagen_url,
                'descripcion_corta': descripcion_corta,
                'fecha': fecha_formateada,
                'autor': 'Smart Books Team',     
                'categoria': 'Educación',        
                'url_articulo': f'/blog/{slug}'  
            })
            
        # Formatear datos de PRODUCTOS para Jinja2
        for prod_data in db_productos:
            (titulo, sku, categoria, precio, url_imagen) = prod_data
            
            # Formato de Precio: $XXX.XXX
            precio_formateado = f'${precio:,.0f}'.replace(',', '.')
            
            productos.append({
                'titulo': titulo,
                'sku': sku,
                'categoria': categoria,
                'precio': precio_formateado,
                'url_imagen': url_imagen
            })

        cur.close()

    except psycopg2.OperationalError as e:
        # Error de conexión a la BD: utiliza placeholders para que la web no falle
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR CRÍTICO: FALLA DE CONEXIÓN A LA BASE DE DATOS.")
        print(f"Mensaje: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        blogs = [
            {'titulo': 'Guía Rápida para Padres: Cómo apoyar el aprendizaje en casa', 'url_imagen_principal': 'https://via.placeholder.com/600x400.png?text=Blog+1', 'descripcion_corta': 'Consejos prácticos para padres...', 'fecha': '12 Oct, 2025', 'autor': 'Smart Books Team', 'categoria': 'EDUCACIÓN', 'url_articulo': '#'},
            {'titulo': 'El Futuro de la Lectura: Integrando E-books y Material Físico', 'url_imagen_principal': 'https://via.placeholder.com/600x400.png?text=Blog+2', 'descripcion_corta': 'Analizamos la educación híbrida...', 'fecha': '12 Oct, 2025', 'autor': 'Smart Books Team', 'categoria': 'EDUCACIÓN', 'url_articulo': '#'},
            {'titulo': '5 Claves para elegir el Texto Escolar ideal para la secundaria', 'url_imagen_principal': 'https://via.placeholder.com/600x400.png?text=Blog+3', 'descripcion_corta': 'Un checklist esencial para directores...', 'fecha': '12 Oct, 2025', 'autor': 'Smart Books Team', 'categoria': 'EDUCACIÓN', 'url_articulo': '#'},
            {'titulo': 'Cómo la Personalización del Aprendizaje impulsa el rendimiento', 'url_imagen_principal': 'https://via.placeholder.com/600x400.png?text=Blog+4', 'descripcion_corta': 'Las plataformas de Smart Books utilizan IA...', 'fecha': '12 Oct, 2025', 'autor': 'Smart Books Team', 'categoria': 'EDUCACIÓN', 'url_articulo': '#'},
            {'titulo': 'Entrevista Exclusiva: El rol del docente en la era digital', 'url_imagen_principal': 'https://via.placeholder.com/600x400.png?text=Blog+5', 'descripcion_corta': 'Una conversación profunda con una experta pedagógica...', 'fecha': '12 Oct, 2025', 'autor': 'Smart Books Team', 'categoria': 'EDUCACIÓN', 'url_articulo': '#'},
            {'titulo': 'Educación Bilingüe: El método que está funcionando en Latinoamérica', 'url_imagen_principal': 'https://via.placeholder.com/600x400.png?text=Blog+6', 'descripcion_corta': 'Presentamos el marco metodológico de nuestros textos...', 'fecha': '12 Oct, 2025', 'autor': 'Smart Books Team', 'categoria': 'EDUCACIÓN', 'url_articulo': '#'},
            {'titulo': 'Los Beneficios de los Recursos Abiertos (OER) y el Ecosistema Smart Books', 'url_imagen_principal': 'https://via.placeholder.com/600x400.png?text=Blog+7', 'descripcion_corta': 'Exploramos cómo los Recursos Educativos Abiertos complementan...', 'fecha': '12 Oct, 2025', 'autor': 'Smart Books Team', 'categoria': 'EDUCACIÓN', 'url_articulo': '#'},
            {'titulo': 'Transformación Institucional: De la tiza y tablero al aula conectada', 'url_imagen_principal': 'https://via.placeholder.com/600x400.png?text=Blog+8', 'descripcion_corta': 'Un plan de acción detallado para que los colegios implementen...', 'fecha': '12 Oct, 2025', 'autor': 'Smart Books Team', 'categoria': 'EDUCACIÓN', 'url_articulo': '#'}
        ]
        productos = [ 
             {'titulo': 'GIVE ME FIVE! 3', 'sku': '978...', 'categoria': 'Inglés', 'precio': '$170.600', 'url_imagen': 'https://sbooks.com.co/wp-content/uploads/2022/10/give-me-3-SB.webp'},
             {'titulo': 'DOODLE TOWN 3', 'sku': '978...', 'categoria': 'Preescolar', 'precio': '$177.900', 'url_imagen': 'https://sbooks.com.co/wp-content/uploads/2022/10/DOODLE-TOWN-STUDENT-3.png'},
             {'titulo': 'FERRIS WHEEL 1', 'sku': '978...', 'categoria': 'Inglés', 'precio': '$87.400', 'url_imagen': 'https://sbooks.com.co/wp-content/uploads/2022/10/FERRIS-WHEEL-ACTIVITY-1.png'},
             {'titulo': 'INSTA ENGLISH 4B', 'sku': '978...', 'categoria': 'Inglés', 'precio': '$88.300', 'url_imagen': 'https://sbooks.com.co/wp-content/uploads/2025/09/INSTA-2ND-EDITION-4B.jpg'}
        ]
        
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        if conn:
            conn.close()

    # --- 3. CONTEXTO DE VARIABLES PARA LA PLANTILLA ---
    context = {
        'url_banner1': 'https://images.unsplash.com/photo-1543269664-56b93a02a768?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 
        'url_banner2': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 
        
        'productos': productos, 
        
        'blogs': blogs
    }

    return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)