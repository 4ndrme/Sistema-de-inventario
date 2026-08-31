from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from config import Config
from models import db, Usuario, Producto, Movimiento 
import csv
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from models import db, Usuario, Producto, ProductoFisico, ProductoPerecible, Movimiento
from sqlalchemy import text
from permisos import requiere_rol
import smtplib
from email.mime.text import MIMEText
import os

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
        rol_seleccionado = request.form.get("rol") # 1. NUEVA LÍNEA: Captura el rol del HTML
        
        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for("registro"))
            
        usuario_existente = Usuario.query.filter_by(username=username).first()
        if usuario_existente:
            flash("El nombre de usuario ya está registrado.", "error")
            return redirect(url_for("registro"))
            
        # 2. LÍNEA MODIFICADA: Pasa la variable en lugar de "Operador"
        nuevo_usuario = Usuario(username=username, rol=rol_seleccionado)
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
        stock_int = int(stock) if stock else 0
        
        # POLIMORFISMO EN ACCIÓN: Instanciamos la clase hija correspondiente
        if tipo == 'Perecible':
            fecha_caducidad = request.form.get("fecha_caducidad")
            # Si el formulario viene vacío, pasamos None
            fecha_valida = fecha_caducidad if fecha_caducidad else None
            
            nuevo_prod = ProductoPerecible(
                codigo=codigo,
                nombre=nombre,
                tipo=tipo,
                stock=stock_int,
                fecha_caducidad=fecha_valida
            )
        else:
            # Por defecto, si es Físico (o cualquier otro)
            nuevo_prod = ProductoFisico(
                codigo=codigo,
                nombre=nombre,
                tipo=tipo,
                stock=stock_int,
                ruta_documento=None # Se puede implementar carga de PDF después
            )
        
        db.session.add(nuevo_prod)
        db.session.commit()
        flash(f"Material {nombre} registrado correctamente.", "success")
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
        usuario_id = session["usuario_id"]

        try:
            # 1. BASE DE DATOS: Delegamos la transacción al Stored Procedure
            sql = text("""
                EXEC sp_ProcesarMovimiento 
                    @producto_id = :prod_id, 
                    @usuario_id = :usr_id, 
                    @tipo_movimiento = :tipo, 
                    @cantidad = :cant, 
                    @observacion = :obs
            """)
            
            db.session.execute(sql, {
                'prod_id': producto.id,
                'usr_id': usuario_id,
                'tipo': tipo_movimiento,
                'cant': cantidad,
                'obs': observacion
            })
            db.session.commit()
            
            # Refrescamos el objeto en memoria para leer el nuevo stock que calculó SQL
            db.session.refresh(producto)

            # 2. POO AVANZADA (El Plus): El objeto decide si dispara la alerta
            if tipo_movimiento == "DESPACHO" and producto.requiere_atencion():
                enviar_alerta_stock(producto.nombre, producto.stock)

            flash(f"{tipo_movimiento} de {cantidad} unidades procesado con éxito.", "success")
            
        except Exception as e:
            # Si el Stored Procedure aborta (ej. intentan dejar el stock negativo), capturamos el error
            db.session.rollback()
            flash(f"Error de base de datos: La operación fue bloqueada por regla de negocio.", "error")
            
        return redirect(url_for('inicio'))
        
    return render_template("movimiento.html", producto=producto)

@app.route("/movimientos")
def movimientos():
    movimientos_lista = Movimiento.query.order_by(Movimiento.fecha_movimiento.desc()).all()
    return render_template("movimientos.html", movimientos=movimientos_lista)


# --- RUTA DE EXPORTACIÓN A EXCEL (.XLSX FORMATTEADO) ---
@app.route("/exportar_inventario")
def exportar_inventario():
    productos = Producto.query.all()

    # Creamos el libro y la hoja de cálculo
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario WMS"

    # Definimos la fila de cabeceras
    headers = ['Código del Material', 'Nombre', 'Tipo', 'Stock Actual', 'Caducidad', 'Estado']
    ws.append(headers)

    # Aplicamos estilos a la cabecera (Fondo Teal-600, Letra Blanca, Centrado)
    fill_teal = PatternFill(start_color="0D9488", end_color="0D9488", fill_type="solid")
    font_bold_white = Font(color="FFFFFF", bold=True)
    align_center = Alignment(horizontal="center", vertical="center")

    for cell in ws[1]:
        cell.fill = fill_teal
        cell.font = font_bold_white
        cell.alignment = align_center

    # Insertamos los datos de la base de datos
    for p in productos:
        # Extraemos la fecha de forma segura: si el objeto no tiene el atributo, devuelve None
        fecha_segura = getattr(p, 'fecha_caducidad', None)
        caducidad = fecha_segura.strftime('%Y-%m-%d') if fecha_segura else 'N/A'
        
        estado = 'Activo' if p.activo else 'Inactivo'
        ws.append([p.codigo, p.nombre, p.tipo, p.stock, caducidad, estado])

    # Ajustamos el ancho de las columnas para que la lectura sea limpia
    column_widths = {'A': 20, 'B': 45, 'C': 15, 'D': 15, 'E': 15, 'F': 12}
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # Empaquetamos el archivo .xlsx en la memoria RAM del servidor
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # Forzamos la descarga con el formato oficial de Microsoft Excel
    response = Response(output.read(), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response.headers['Content-Disposition'] = 'attachment; filename=Reporte_Inventario_WMS.xlsx'
    
    return response

# --- MOTOR DE ALERTAS SMTP ---
def enviar_alerta_stock(nombre_producto, stock_actual):
    # En un entorno real, estas credenciales irían en tu archivo .env
    remitente = os.getenv("EMAIL_USER", "michaelamigo29@gmail.com") 
    password = os.getenv("EMAIL_PASS", "qxvnystplixpzbrk") 
    destinatario = "michaelandresqc@gmail.com" # El correo de quien recibe la alerta

    mensaje_cuerpo = (
        f"ALERTA WMS AUTOMÁTICA\n\n"
        f"El material '{nombre_producto}' ha alcanzado un nivel de inventario crítico.\n"
        f"Stock actual disponible: {stock_actual} unidades.\n\n"
        f"Por favor, proceda con la orden de compra o reabastecimiento."
    )
    
    msg = MIMEText(mensaje_cuerpo)
    msg['Subject'] = f"⚠️ Alerta de Stock Crítico: {nombre_producto}"
    msg['From'] = remitente
    msg['To'] = destinatario

    try:
        # Configuración estándar para Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        print(f"Alerta enviada exitosamente para {nombre_producto}")
    except Exception as e:
        print(f"Error al enviar la alerta SMTP: {e}")

@app.route("/reportes")
@requiere_rol("Auditor", "Supervisor")
def reportes():
    # Consulta compleja requerida por la rúbrica (Integración de múltiples tablas con LEFT JOIN)
    sql = text("""
        SELECT 
            p.codigo AS Codigo_Material,
            p.nombre AS Material,
            p.tipo AS Categoria,
            p.stock AS Stock_Actual,
            COUNT(m.id) AS Total_Transacciones,
            ISNULL(SUM(CASE WHEN m.tipo_movimiento = 'INGRESO' THEN m.cantidad ELSE 0 END), 0) AS Total_Ingresado,
            ISNULL(SUM(CASE WHEN m.tipo_movimiento = 'DESPACHO' THEN m.cantidad ELSE 0 END), 0) AS Total_Despachado
        FROM productos p
        LEFT JOIN movimientos m ON p.id = m.producto_id
        GROUP BY p.codigo, p.nombre, p.tipo, p.stock
        ORDER BY Total_Transacciones DESC;
    """)
    
    resultados = db.session.execute(sql).fetchall()
    return render_template("reportes.html", estadisticas=resultados)

if __name__ == "__main__":
    app.run(debug=True)