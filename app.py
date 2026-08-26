from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from models import db, Usuario, Producto, Movimiento 

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# --- GUARDIÁN DE SEGURIDAD (Protección de Rutas) ---
@app.before_request
def bloquear_accesos_no_autorizados():
    # Permitimos 'login', 'registro' y archivos estáticos sin iniciar sesión
    rutas_libres = ['login', 'registro', 'static']
    
    # Si el usuario no ha iniciado sesión y la ruta es privada, redirigimos a login
    if 'usuario_id' not in session and request.endpoint not in rutas_libres:
        return redirect(url_for('login'))

# --- RUTA DE REGISTRO DE USUARIOS ---
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for("registro"))

        usuario_existente = Usuario.query.filter_by(username=username).first()
        if usuario_existente:
            flash("El nombre de usuario ya está registrado.", "error")
            return redirect(url_for("registro"))

        # Se asigna el nombre de usuario y rol, y se aplica el hash a la contraseña
        nuevo_usuario = Usuario(username=username, rol="Operador")
        nuevo_usuario.set_password(password)
        
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")
# --- RUTA DE AUTENTICACIÓN (LOGIN) ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        # Se utiliza el método check_password de models.py para comparar el hash seguro
        if usuario and usuario.check_password(password):
            session["usuario_id"] = usuario.id
            session["username"] = usuario.username
            session["rol"] = usuario.rol
            flash(f"Bienvenido al sistema, {usuario.username}.", "success")
            return redirect(url_for("inicio"))
        else:
            flash("Usuario o contraseña incorrectos.", "error")
            
    return render_template("login.html")
# --- RUTA DE CIERRE DE SESIÓN ---
@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for("login"))

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
            usuario_id=session["usuario_id"] 
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