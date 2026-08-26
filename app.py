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

@app.route("/procesar_movimiento/<int:id_producto>", methods=["GET", "POST"])
def procesar_movimiento(id_producto):
    # 1. Buscamos el material exacto en la base de datos
    producto = Producto.query.get_or_404(id_producto)
    
    # 2. Capturamos los datos que nos enviará el HTML
    tipo_movimiento = request.form.get("tipo_movimiento") # 'INGRESO' o 'DESPACHO'
    cantidad = int(request.form.get("cantidad", 0))
    observacion = request.form.get("observacion", "")
    
    # 3. REGLA DE SEGURIDAD: Evitar stock negativo
    if tipo_movimiento == "DESPACHO" and cantidad > producto.stock:
        flash("Error: No hay suficiente stock en el almacén para este despacho.", "error")
        return redirect(url_for('inicio'))
        
    # 4. Lógica Matemática
    if tipo_movimiento == "INGRESO":
        producto.stock += cantidad
    elif tipo_movimiento == "DESPACHO":
        producto.stock -= cantidad
        
    # 5. Registro Inmutable de Auditoría
    nuevo_movimiento = Movimiento(
        tipo_movimiento=tipo_movimiento,
        cantidad=cantidad,
        observacion=observacion,
        producto_id=producto.id,
        # Usamos el ID por defecto (1) temporalmente hasta que tengamos el sistema de Login listo
        usuario_id=1 
    )
    
    # 6. Transacción Segura (Se guarda el stock y el historial al mismo tiempo)
    db.session.add(nuevo_movimiento)
    db.session.commit()
    
    # 7. Mensaje de éxito y redirección
    flash(f"{tipo_movimiento} de {cantidad} unidades procesado con éxito.", "success")
    return redirect(url_for('inicio'))

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
        
    # Si la petición es GET, mostramos la pantalla del formulario
    return render_template("movimiento.html", producto=producto)

# --- NUEVA RUTA: HISTORIAL DE MOVIMIENTOS ---
@app.route("/movimientos")
def movimientos():
    # Obtenemos todos los movimientos ordenados por fecha (más recientes primero)
    movimientos_lista = Movimiento.query.order_by(Movimiento.fecha_movimiento.desc()).all()
    return render_template("movimientos.html", movimientos=movimientos_lista)

if __name__ == "__main__":
    app.run(debug=True)



if __name__ == "__main__":
    app.run(debug=True)