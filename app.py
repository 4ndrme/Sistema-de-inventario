from flask import Flask, render_template
from config import Config
from models import db, Producto, Categoria

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route("/")
def inicio():
    productos = Producto.query.all()
    return render_template("index.html", productos=productos)

# --- NUEVA RUTA PARA CATEGORÍAS ---
@app.route("/categorias")
def categorias():
    # Consultamos todas las categorías
    lista_categorias = Categoria.query.all()
    return render_template("categorias.html", categorias=lista_categorias)

if __name__ == "__main__":
    app.run(debug=True)