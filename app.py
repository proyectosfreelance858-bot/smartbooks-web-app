from flask import Flask, render_template

app = Flask(__name__)

# Simulación de la información de la base de datos (DB)
# *** ASEGÚRATE DE USAR TUS PROPIAS URLS AQUÍ ***
db_data = {
    # BANNERS
    "url_banner1": "/static/images/banner1.jpg", 
    "url_banner2": "/static/images/banner2.jpg",
    "url_banner3": "/static/images/banner_lateral.jpg",
    "url_banner4": "/static/images/banner_inferior.jpg",

    # PRODUCTOS
    "url_productosmasvendidos1": "/static/images/prod1.jpg",
    "txt_productosmasvendidos1": "PAQUETE DE INGLÉS COSMO (SUPERIOR)",
    "url_productosmasvendidos2": "/static/images/prod2.jpg",
    "txt_productosmasvendidos2": "PAQUETE DE INGLÉS COSMO (INFERIOR)",
    "url_productosmasvendidos3": "/static/images/prod3.jpg",
    "txt_productosmasvendidos3": "NOVELA JUVENIL CLÁSICA",
    "url_productosmasvendidos4": "/static/images/prod4.jpg",
    "txt_productosmasvendidos4": "CRÓNICA HISTÓRICA",

    # EDITORIALES
    "url_editorial1": "/static/images/edit1.png",
    "url_editorial2": "/static/images/edit2.png",
    "url_editorial3": "/static/images/edit3.png",
    "url_editorial4": "/static/images/edit4.png",
    "url_editorial5": "/static/images/edit5.png",
}

@app.route("/")
def index():
    # Renderiza directamente index.html, que ya no extiende ningún layout.
    return render_template("index.html", **db_data)

if __name__ == "__main__":
    app.run(debug=True)