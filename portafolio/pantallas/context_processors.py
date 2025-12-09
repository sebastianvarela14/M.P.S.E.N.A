import mysql.connector
import os
from pantallas.models import Usuario

def usuario_instructor(request):
    nombre_completo = None
    usuario_id = request.session.get('usuario_id')
    
    if usuario_id:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT nombres, apellidos FROM usuario WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()
        
        if usuario:
            primer_nombre = usuario['nombres'].split()[0].capitalize()
            primer_apellido = usuario['apellidos'].split()[0].capitalize()
            nombre_completo = f"{primer_nombre} {primer_apellido}"

    return {'usuario_nombre': nombre_completo}  


def ficha_context(request):
    return {
        "ficha_id": request.session.get("ficha_actual")
    }


# ⭐ NUEVA FUNCIÓN AQUÍ ⭐
def datos_coordinador(request):
    usuario = request.user
    if usuario.is_authenticated and hasattr(usuario, "rol") and usuario.rol == "coordinador":
        return {
            "nombre_coordinador": usuario.nombre,
            "correo_coordinador": usuario.email,
        }
    return {}
