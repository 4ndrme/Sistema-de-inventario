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

@app.route("/procesar_movimiento/<int:id_producto>", methods=["GET", "POST"])
def procesar_movimiento(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    
    if request.method == "POST":
        tipo_movimiento = request.form.get("tipo_movimiento") 
        cantidad = int(request.form.get("cantidad", 0))
        observacion = request.form.get("observacion", "")
        
        if tipo_movimiento == "DESPACHO" and cantidad > producto.stock:
            flash("Error: No hay suficiente stock en el almacén para este despacho.", "error")
            return redirect(url_for('inicio'))
            
        if tipo_movimiento == "INGRESO":
            producto.stock += cantidad
        elif tipo_movimiento == "DESPACHO":
            producto.stock -= cantidad
            
        nuevo_movimiento = Movimiento(
            tipo_movimiento=tipo_movimiento,
            cantidad=cantidad,
            observacion=observacion,
            producto_id=producto.id,
            usuario_id=1 
        )
        
        db.session.add(nuevo_movimiento)
        db.session.commit()
        
        flash(f"{tipo_movimiento} de {cantidad} unidades procesado con éxito.", "success")
        return redirect(url_for('inicio'))
        
    return render_template("movimiento.html", producto=producto)

@app.route("/movimientos")
def movimientos():
    movimientos_lista = Movimiento.query.order_by(Movimiento.fecha_movimiento.desc()).all()
    return render_template("movimientos.html", movimientos=movimientos_lista)

if __name__ == "__main__":
    app.run(debug=True)