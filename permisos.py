from functools import wraps
from flask import session, flash, redirect, url_for

def requiere_rol(*roles_permitidos):
    """
    Decorador que verifica si el rol del usuario actual en sesión 
    coincide con los roles permitidos para ejecutar la ruta.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Verifica si el usuario está logueado
            if 'usuario_id' not in session:
                flash("Acceso denegado: Debes iniciar sesión.", "error")
                return redirect(url_for('login'))
                
            # 2. Verifica el rol
            rol_actual = session.get('rol', 'Operador') # Por defecto asume Operador por seguridad
            
            if rol_actual not in roles_permitidos:
                flash(f"Acceso restringido. Esta acción requiere nivel de: {', '.join(roles_permitidos)}", "error")
                return redirect(url_for('inicio'))
                
            # Si pasa las pruebas, ejecuta la función original
            return f(*args, **kwargs)
        return decorated_function
    return decorator