from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Usuario, Producto, Movimiento 

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route("/")
def inicio():
    query = request.args.get("q", "")
    if query:
        productos = Producto.query.filter(
            (Producto.nombre.ilike(f"%{query}%")) | 
            (Producto.codigo.ilike(f"%{query}%"))
        ).all()
    else:
        productos = Producto.query.all()
    return render_template("index.html", productos=productos, query=query)

@app.route("/nuevo_material", methods=["GET", "POST"])
def nuevo_material():
    if request.method == "POST":
        codigo = request.form.get("codigo")
        nombre = request.form.get("nombre")
        tipo = request.form.get("tipo")
        stock = request.form.get("stock")
        fecha_caducidad = request.form.get("fecha_caducidad")
        
        if not fecha_caducidad:
            fecha_caducidad = None

        nuevo_prod = Producto(
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            stock=int(stock) if stock else 0,
            fecha_caducidad=fecha_caducidad
        )
        
        db.session.add(nuevo_prod)
        db.session.commit()
        return redirect(url_for('inicio'))
        
    return render_template("nuevo_material.html")

@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar_producto(id):
    producto = db.session.get(Producto, id)
    if producto:
        db.session.delete(producto)
        db.session.commit()
    return redirect(url_for("inicio"))

@app.route("/movimientos", methods=["GET", "POST"])
def movimientos():
    if request.method == "POST":
        producto_id = request.form.get("producto_id")
        tipo_movimiento = request.form.get("tipo_movimiento")
        cantidad = int(request.form.get("cantidad", 0))

        producto = db.session.get(Producto, int(producto_id)) if producto_id else None

        if producto:
            if tipo_movimiento == "ENTRADA":
                producto.stock += cantidad
            elif tipo_movimiento == "SALIDA" and producto.stock >= cantidad:
                producto.stock -= cantidad

            # Obtener el primer usuario registrado para satisfacer la FK no nula
            usuario_default = Usuario.query.first()
            usuario_id_val = usuario_default.id if usuario_default else 1

            columnas_mov = [col.name for col in Movimiento.__table__.columns]
            kwargs_mov = {
                "producto_id": producto.id,
                "cantidad": cantidad
            }

            if "tipo" in columnas_mov:
                kwargs_mov["tipo"] = tipo_movimiento
            elif "tipo_movimiento" in columnas_mov:
                kwargs_mov["tipo_movimiento"] = tipo_movimiento

            if "usuario_id" in columnas_mov:
                kwargs_mov["usuario_id"] = usuario_id_val

            nuevo_mov = Movimiento(**kwargs_mov)
            db.session.add(nuevo_mov)
            db.session.commit()

        return redirect(url_for("inicio"))

    productos = Producto.query.all()
    movimientos_lista = Movimiento.query.all()
    return render_template("movimientos.html", productos=productos, movimientos=movimientos_lista)

if __name__ == "__main__":
    app.run(debug=True)