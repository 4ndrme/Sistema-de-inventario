from flask import Flask, render_template, request, redirect, url_for
from config import Config
# Importamos los NUEVOS modelos de nuestro WMS
from models import db, Usuario, Producto, Movimiento 

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route("/")
def inicio():
    # Consultamos todos los productos del almacén
    productos = Producto.query.all()
    return render_template("index.html", productos=productos)


# --- NUEVA RUTA: PARA  CREAR MATERIAL ---
@app.route("/nuevo_material", methods=["GET", "POST"])
def nuevo_material():
    if request.method == "POST":
        # Extraemos los datos del formulario HTML
        codigo = request.form.get("codigo")
        nombre = request.form.get("nombre")
        tipo = request.form.get("tipo")
        stock = request.form.get("stock")
        fecha_caducidad = request.form.get("fecha_caducidad")
        
        # Si la fecha viene vacía, la convertimos a None (NULL en base de datos)
        if not fecha_caducidad:
            fecha_caducidad = None

        # Creamos el nuevo objeto Producto
        nuevo_prod = Producto(
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            stock=int(stock) if stock else 0,
            fecha_caducidad=fecha_caducidad
        )
        
        # Guardamos en SQL Server
        db.session.add(nuevo_prod)
        db.session.commit()
        
        # Redirigimos a la tabla principal
        return redirect(url_for('inicio'))
        
    return render_template("nuevo_material.html")
if __name__ == "__main__":
    app.run(debug=True)