import mysql.connector
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import os
from dotenv import load_dotenv

from .forms import UsuarioForm
from django.http import HttpResponse
from .models import Usuario, UsuarioRol, Rol, Ficha, FichaUsuario

load_dotenv() 

def plantillains(request):
    return render(request, "paginas/instructor/plantilla.html", )

def agregar_evidencia(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        instrucciones = request.POST.get('instrucciones')
        calificacion = request.POST.get('calificacion')
        fecha_entrega = request.POST.get('fecha_de_entrega')
        archivo = request.FILES.get('archivo')

        # Por ahora, guardaremos solo el nombre del archivo.
        # En un futuro, podrías implementar la subida de archivos a una carpeta.
        nombre_archivo = archivo.name if archivo else "No subido"

        try:
            conexion = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO evidencias_instructor (titulo, instrucciones, calificacion, fecha_de_entrega, archivo)
                VALUES (%s, %s, %s, %s, %s)
            """, (titulo, instrucciones, calificacion, fecha_entrega, nombre_archivo))
            conexion.commit()
            messages.success(request, "Evidencia agregada correctamente.")
        except mysql.connector.Error as err:
            messages.error(request, f"Error al agregar la evidencia: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()
        return redirect('evidencias')
    return render(request, "paginas/instructor/agregar_evidencia.html")

def calificaciones(request):
    return render(request, "paginas/instructor/calificaciones.html")

def material(request):
    return render(request, "paginas/instructor/material.html")

def portafolio_aprendices(request):
    return render(request, "paginas/instructor/portafolio_aprendices.html")

def trimestre1(request):
    return render(request, "paginas/carpetas.html")

def trimestre2(request):
    return render(request, "paginas/carpetas.html")

def trimestre3(request):
    return render(request, "paginas/carpetas.html")

def fichas_ins(request):
    if 'usuario' not in request.session:
        return redirect('sesion')

    usuario_login = request.session['usuario']  # nombre de usuario, NO el nombre real

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)

    # Obtener ID del usuario
    cursor.execute("SELECT id FROM usuario WHERE usuario = %s", (usuario_login,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        conexion.close()
        return redirect('sesion')

    id_usuario = usuario['id']

    # 🔥 Obtener primer nombre y primer apellido
    cursor.execute("""
        SELECT nombres, apellidos 
        FROM usuario 
        WHERE id = %s
    """, (id_usuario,))
    datos_nombre = cursor.fetchone()

    if datos_nombre:
        primer_nombre = datos_nombre['nombres'].split()[0].capitalize()     # Primer nombre
        primer_apellido = datos_nombre['apellidos'].split()[0].capitalize()   # Primer apellido
        usuario_nombre = f"{primer_nombre} {primer_apellido}"
    else:
        usuario_nombre = usuario_login

    # Obtener fichas asignadas
    cursor.execute("""
        SELECT f.id, f.numero_ficha, p.programa, j.nombre AS jornada
        FROM ficha f
        INNER JOIN ficha_usuario fu ON fu.idficha = f.id
        INNER JOIN usuario u ON fu.idusuario = u.id
        INNER JOIN programa p ON f.idprograma = p.id
        INNER JOIN jornada j ON f.idjornada = j.id
        WHERE u.id = %s
    """, (id_usuario,))

    fichas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render(request, "paginas/instructor/fichas_ins.html", {
        'usuario_nombre': usuario_nombre,
        'fichas': fichas
    })

def tarea(request):
    return render(request, "paginas/aprendiz/tarea.html")

def calificacion(request):
    return render(request, "paginas/aprendiz/calificacion.html")

def datos(request):
    return render(request, "paginas/instructor/datos.html")

def datos_ins(request):
    usuario_id = request.session.get('usuario_id')  # 🔹 Obtener ID de la sesión

    if not usuario_id:
        messages.error(request, "Debes iniciar sesión primero.")
        return redirect('sesion')

    # Conectar a la base de datos
    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)
    
    # Obtener los datos del usuario por ID
    cursor.execute("""
        SELECT u.nombres, u.apellidos, u.correo, u.telefono,
                d.tipo AS tipo_documento, d.numero AS num_documento
        FROM usuario u
        LEFT JOIN documento d ON u.iddocumento = d.id
        WHERE u.id = %s
    """, (usuario_id,))

    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render(request, "paginas/instructor/datos_ins.html", {
        'usuario': usuario
    })


def evidencias(request):
    # Conectar a la base de datos
    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)
    
    # Obtener todas las evidencias del instructor
    cursor.execute("SELECT * FROM evidencias_instructor")
    evidencias = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render(request, "paginas/instructor/evidencias.html", {"evidencias": evidencias})


def material2(request):
    return render(request, "paginas/instructor/material2.html")

def portafolio_aprendices(request):
    return render(request, "paginas/instructor/portafolio_aprendices.html")

def tareas(request):
    return render(request, "paginas/aprendiz/tareas.html")

def tareas_2(request):
    return render(request, "paginas/aprendiz/tareas_2.html")

def lista_aprendices(request):
    conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.id, u.nombres, u.apellidos
        FROM usuario u
        WHERE u.id IN (3, 4)
    """)

    aprendices = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render(request, "paginas/instructor/lista_aprendices.html", {
        "aprendices": aprendices
    })

def datos_aprendiz(request, id):

    # Conexion a base de datos
    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)

    # Obtener datos del aprendiz
    cursor.execute("""
        SELECT u.nombres, u.apellidos, u.correo, u.telefono,
        d.tipo AS tipo_documento, d.numero AS num_documento
        FROM usuario u
        LEFT JOIN documento d ON u.iddocumento = d.id
        WHERE u.id = %s
    """, (id,))

    aprendiz = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render(request, "paginas/instructor/datos.html", {
        "aprendiz": aprendiz
    })



def carpetas2(request):
    return render(request, "paginas/instructor/carpetas2.html")

def portafolio(request):
    return render(request, "paginas/instructor/portafolio.html")

def taller(request):
    return render(request, "paginas/instructor/taller.html")


def carpetasins(request):
    return render(request, "paginas/instructor/carpetasins.html")

def trimestre(request):
    return render(request, "paginas/instructor/trimestre.html")

def carpetas_aprendiz(request):
    return render(request, "paginas/instructor/carpetas_aprendiz.html")

def trimestre_aprendiz(request):
    return render(request, "paginas/instructor/trimestre_aprendiz.html")

def trimestre_general(request):
    return render(request, "paginas/instructor/trimestre_general.html")

def carpetas(request):
    return render(request, "paginas/instructor/carpetas.html")

def material_principal(request):
    return render(request, "paginas/instructor/material_principal.html")

def adentro_material(request):
    return render(request, "paginas/instructor/adentro_material.html")

def lista_aprendices1(request):
    return render(request, "paginas/aprendiz/lista_aprendices1.html")

def datoslaura(request):
    return render(request, "paginas/aprendiz/datoslaura.html")


def adentro_material1(request):
    return render(request, "paginas/instructor/adentro_material1.html")

def evidencia_guia(request, evidencia_id):
    # Conectar a la base de datos
    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)
    
    # Obtener la evidencia específica por su ID
    cursor.execute("SELECT * FROM evidencias_instructor WHERE id = %s", (evidencia_id,))
    evidencia = cursor.fetchone()

    cursor.close()
    conexion.close()

    # Pasar la evidencia encontrada a la plantilla
    return render(request, "paginas/instructor/evidencia_guia.html", {"evidencia": evidencia})

def evidencia_guia1(request):
    return render(request, "paginas/instructor/evidencia_guia1.html")

def inicio(request):
    id_aprendiz = request.session.get('id_usuario')
    nombre_aprendiz = request.session.get('nombre_usuario', '')
    competencias = []

    if id_aprendiz:
        try:
            conexion = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
        )
            cursor = conexion.cursor(dictionary=True)

            # Consulta SQL para obtener las competencias de la ficha del aprendiz
            query = """
                SELECT c.id, c.nombre AS nombre_competencia
                FROM competencia c
                JOIN ficha_competencia fc ON c.id = fc.idcompetencia
                JOIN ficha f ON fc.idficha = f.id
                JOIN usuario_ficha uf ON f.id = uf.idficha
                WHERE uf.idusuario = %s
            """
            cursor.execute(query, (id_aprendiz,))
            competencias = cursor.fetchall()

            cursor.close()
            conexion.close()
        except mysql.connector.Error as err:
            messages.error(request, f"")

    return render(request, "paginas/aprendiz/inicio.html", {'competencias': competencias, 'nombre_aprendiz': nombre_aprendiz})


def carpetas_aprendiz1(request):
    return render(request, "paginas/instructor/carpetas_aprendiz1.html")

def carpetas_aprendiz2(request):
    return render(request, "paginas/instructor/carpetas_aprendiz2.html")


def coordinador(request):
    ficha_id = request.GET.get("ficha")

    # Si viene ficha en la URL → guardarla en sesión
    if ficha_id:
        request.session["ficha_actual"] = ficha_id

    fichas = Ficha.objects.all()

    return render(request, "paginas/coordinador/coordinador.html", {
        "fichas": fichas,
        "ficha_id": ficha_id
    })

def entrada(request):
    return render(request, "paginas/aprendiz/entrada.html")

def trimestre_laura(request):
    return render(request, "paginas/aprendiz/trimestre_laura.html")

def carpetas_laura(request):
    return render(request, "paginas/aprendiz/carpetas_laura.html")

def evidencia_laura(request):
    return render(request, "paginas/aprendiz/evidencia_laura.html")

def evidencia_guialaura(request):
    return render(request, "paginas/aprendiz/evidencia_guialaura.html")

def material_laura(request):
    return render(request, "paginas/aprendiz/material_laura.html")

def adentro_material_aprendiz(request):
    return render(request, "paginas/aprendiz/adentro_material_aprendiz.html")

def carpetas_aprendiz_observador(request):
    return render(request, "paginas/observador/carpetas_aprendiz_observador.html")

def carpetas_observador(request):
    return render(request, "paginas/observador/carpetas_observador.html")

def inicio_observador(request):
    return render(request, "paginas/observador/inicio_observador.html")

def lista_aprendices_observador(request):
    return render(request, "paginas/observador/lista_aprendices_observador.html")

def observador(request):
    return render(request, "paginas/observador/observador.html")

def portafolio_aprendices_observador(request):
    return render(request, "paginas/observador/portafolio_aprendices_observador.html")

def portafolio_observador(request):
    return render(request, "paginas/observador/portafolio_observador.html")

def trimestre_aprendiz_observador(request):
    return render(request, "paginas/observador/trimestre_aprendiz_observador.html")

def trimestre_observador(request):
    return render(request, "paginas/observador/trimestre_observador.html")

def adentro_material_observador(request):
    return render(request, "paginas/observador/adentro_material_observador.html")

def material_principal_observador(request):
    return render(request, "paginas/observador/material_principal_observador.html")

def evidencia_guia_observador(request):
    return render(request, "paginas/observador/evidencia_guia_observador.html")

def evidencias_observador(request):
    return render(request, "paginas/observador/evidencias_observador.html")

def adentro_material_coordinador(request):
    return render(request, "paginas/observador/evidencias_observador.html")

def evidencias_observador(request):
    return render(request, "paginas/observador/evidencias_observador.html")

def adentro_material_coordinador(request):
    return render(request, "paginas/coordinador/adentro_material_coordinador.html")

def carpetas_coordinador(request):
    return render(request, "paginas/coordinador/carpetas_coordinador.html")

def evidencia_guia_coordinador(request):
    return render(request, "paginas/coordinador/evidencia_guia_coordinador.html")

def evidencias_coordinador(request):
    return render(request, "paginas/coordinador/evidencias_coordinador.html")

def inicio_coordinador(request):
    # Recuperamos la ficha seleccionada de la sesión
    ficha_id = request.session.get('ficha_id')
    return render(request, "paginas/coordinador/inicio_coordinador.html", {"ficha_id": ficha_id})

def lista_aprendices_coordinador(request):
    return render(request, "paginas/coordinador/lista_aprendices_coordinador.html")

def material_principal_coordinador(request):
    return render(request, "paginas/coordinador/material_principal_coordinador.html")

def portafolio_aprendices_coordinador(request):
    return render(request, "paginas/coordinador/portafolio_aprendices_coordinador.html")

def portafolio_coordinador(request):
    return render(request, "paginas/coordinador/portafolio_coordinador.html")

def trimestre_coordinador(request):
    return render(request, "paginas/coordinador/trimestre_coordinador.html")

def datos_coordinador(request):
    return render(request, "paginas/coordinador/datos_coordinador.html")

def agregar_carpeta(request):
    return render(request, "paginas/instructor/agregar_carpeta.html")

def plan_concertado(request):
    return render(request, "paginas/instructor/plan_concertado.html")

def evidencia_calificar(request):
    return render(request, "paginas/instructor/evidencia_calificar.html")

def calificaciones_observador(request):
    return render(request, "paginas/observador/calificaciones_observador.html")

def evidencia_calificar_observador(request):
    return render(request, "paginas/observador/evidencia_calificar_observador.html")

def datos_observador(request):
    return render(request, "paginas/observador/datos_observador.html")

def carpetas_general(request):
    return render(request, "paginas/coordinador/carpetas_general.html")

def trimestre_general_coordinador(request):
    return render(request, "paginas/coordinador/trimestre_general_coordinador.html")

def trimestre_aprendiz_coordinador(request):
    return render(request, "paginas/coordinador/trimestre_aprendiz_coordinador.html")

def carpetas_aprendiz_coordinador(request):
    return render(request, "paginas/coordinador/carpetas_aprendiz_coordinador.html")

def calificaciones_coordinador(request):
    return render(request, "paginas/coordinador/calificaciones_coordinador.html")

def evidencia_calificar_coordinador(request):
    return render(request, "paginas/coordinador/evidencia_calificar_coordinador.html")

def sesion(request):
    usuario_ingresado = ""

    # 🔹 Limpiar mensajes antiguos al entrar por GET
    if request.method == "GET":
        storage = messages.get_messages(request)
        storage.used = True

    if request.method == 'POST':
        usuario_input = request.POST.get('usuario')
        contrasena_input = request.POST.get('contrasena')
        usuario_ingresado = usuario_input

        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario WHERE usuario = %s", (usuario_input,))
        usuario = cursor.fetchone()

        if not usuario:
            messages.error(request, "El usuario no existe.")
            return redirect('sesion')
        else:
            contrasena_correcta = usuario['contrasena']
            if contrasena_input != contrasena_correcta:
                messages.error(request, "Contraseña incorrecta.")
                return redirect('sesion')
            else:
                request.session['id_usuario'] = usuario['id']
                request.session['usuario'] = usuario['usuario']
                request.session['nombre_usuario'] = f"{usuario['nombres']} {usuario['apellidos']}".upper()
                cursor.execute("""
                    SELECT r.tipo
                    FROM rol r
                    INNER JOIN usuario_rol ur ON ur.idrol = r.id
                    WHERE ur.idusuario = %s
                """, (usuario['id'],))
                rol = cursor.fetchone()

                if rol:
                    tipo_rol = rol['tipo'].lower()
                    
                    request.session['usuario_id'] = usuario['id']
                    request.session['usuario_nombre'] = usuario['usuario']

                    # Redirigir según el tipo de rol
                    if tipo_rol == 'instructor':
                        return redirect('fichas_ins')
                    elif tipo_rol == 'aprendiz':
                        return redirect('inicio')
                    elif tipo_rol == 'coordinacion':
                        return redirect('coordinador')
                    elif tipo_rol == 'observador':
                        return redirect('observador')
                    else:
                        messages.error(request, f"Rol desconocido: {tipo_rol}")
                        return redirect('sesion')
                else:
                    messages.error(request, "No se encontró un rol asignado para este usuario.")
                    return redirect('sesion')
                
        cursor.close()
        conexion.close()

    return render(request, "paginas/instructor/sesion.html", {
        'usuario_ingresado': usuario_ingresado
        }
    )

def configuracion_instructor(request):
    return render(request, "paginas/instructor/configuracion_instructor.html")


def configuracion_instructor_2(request):
    return render(request, "paginas/instructor/configuracion_instructor_2.html",)


def configuracion_aprendiz(request):
    return render(request, "paginas/aprendiz/configuracion_aprendiz.html")

def configuracion_aprendiz_2(request):
    return render(request, "paginas/aprendiz/configuracion_aprendiz_2.html")

def configuracion_observador(request):
    return render(request, "paginas/observador/configuracion_observador.html")

def configuracion_observador_2(request):
    return render(request, "paginas/observador/configuracion_observador_2.html")

def configuracion_coordinador(request):
    # 1. Leer ficha desde URL o sesión
    ficha_id = request.GET.get("ficha") or request.session.get("ficha_actual")

    if not ficha_id:
        messages.error(request, "Primero debes seleccionar una ficha.")
        return redirect("inicio_coordinador")

    # Guardar ficha en sesión para futuras acciones
    request.session["ficha_actual"] = ficha_id

    # 2. Traer instructores
    instructores = Usuario.objects.filter(
        usuariorol__idrol__tipo="instructor"
    ).distinct()

    if request.method == "POST":
        seleccionados = request.POST.getlist("instructores")

        # 3. Eliminar instructores anteriores
        FichaUsuario.objects.filter(
            idficha_id=ficha_id,
            idusuario__usuariorol__idrol__tipo="instructor"
        ).delete()

        # 4. Guardar nuevos instructores asignados
        for ins_id in seleccionados:
            FichaUsuario.objects.create(
                idficha_id=ficha_id,
                idusuario_id=ins_id
            )

        messages.success(request, "¡Instructores asignados correctamente!")

    # 5. Obtener instructores ya asignados a la ficha
    instructores_asignados = Usuario.objects.filter(
        fichausuario__idficha_id=ficha_id,
        usuariorol__idrol__tipo="instructor"
    ).distinct()

    # Crear lista de IDs para usar en el template
    ids_instructores_asignados = instructores_asignados.values_list('id', flat=True)

    # 6. Pasar todo al contexto
    return render(request, "paginas/coordinador/configuracion_coordinador.html", {
        "instructores": instructores,
        "instructores_asignados": instructores_asignados,
        "ids_instructores_asignados": ids_instructores_asignados,
        "ficha_id": ficha_id
    })

def evidencia_calificada(request):
    return render(request, "paginas/instructor/evidencia_calificada.html")

def configuracion_coordinador_base(request):
    return render(request, "paginas/coordinador/configuracion_coordinador_base.html")

def configuracion_coordinador_base_2(request):
    return render(request, "paginas/coordinador/configuracion_coordinador_base_2.html")

def ficha_coordinador(request):
    return render(request, "paginas/coordinador/ficha_coordinador.html")

def ficha_aprendiz(request):
    return render(request, "paginas/aprendiz/ficha_aprendiz.html")

def ficha_aprendiz_2(request):
    return render(request, "paginas/aprendiz/ficha_aprendiz_2.html")

def ficha_instructor(request):
    return render(request, "paginas/instructor/ficha_instructor.html")

def ficha_observador(request):
    return render(request, "paginas/observador/ficha_observador.html")

def equipo_ejecutor(request):
    return render(request, "paginas/instructor/equipo_ejecutor.html")

def opc_equipoejecutor(request):
    return render(request, "paginas/instructor/opc_equipoejecutor.html")

def fichas_equipoejecutor_coordinador(request):
    return render(request, "paginas/coordinador/fichas_equipoejecutor_coordinador.html")

def equipo_coordinador(request):
    return render(request, "paginas/coordinador/equipo_coordinador.html")

def material_editar(request):
    return render(request, "paginas/instructor/material_editar.html")

def evidencia_guia_editar(request):
    return render(request, "paginas/instructor/evidencia_guia_editar.html")

def carpetasins_editar(request):
    return render(request, "paginas/instructor/carpetasins_editar.html")

def carpetasins_crear(request):
    return render(request, "paginas/instructor/carpetasins_crear.html")

def carpetas_aprendiz_crear(request):
    return render(request, "paginas/instructor/carpetas_aprendiz_crear.html")

def carpetas_aprendiz_editar(request):
    return render(request, "paginas/instructor/carpetas_aprendiz_editar.html")

def datos_ins_editar(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        messages.error(request, "Debes iniciar sesión primero.")
        return redirect('sesion')

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)

    # Obtener datos actuales
    cursor.execute("SELECT * FROM usuario u LEFT JOIN documento d ON u.iddocumento = d.id WHERE u.id = %s", (usuario_id,))
    usuario = cursor.fetchone()

    if request.method == "POST":
        nombres = request.POST.get("nombres")
        apellidos = request.POST.get("apellidos")
        correo = request.POST.get("correo")
        telefono = request.POST.get("telefono")
        tipo_documento = request.POST.get("tipo_documento")
        numero_documento_str = request.POST.get("numero_documento", "").strip()

        # Validar que no esté vacío
        if numero_documento_str == "":
            messages.error(request, "El número de documento no puede estar vacío.")
            return redirect('datos_ins_editar')
        try:
            numero_documento = int(numero_documento_str)
        except ValueError:
            messages.error(request, "El número de documento debe ser un número válido.")
            return redirect('datos_ins_editar')

        if usuario['iddocumento']:
            # Actualizar documento existente
            cursor.execute("""
                UPDATE documento 
                SET tipo = %s, numero = %s 
                WHERE id = %s
            """, (tipo_documento, numero_documento, usuario['iddocumento']))
        else:
            # Insertar nuevo documento
            cursor.execute("""
                INSERT INTO documento (tipo, numero)
                VALUES (%s, %s)
            """, (tipo_documento, numero_documento, usuario['iddocumento']))
            nuevo_id = cursor.lastrowid
            # Asociar el nuevo documento al usuario
            cursor.execute("""
                UPDATE usuario 
                SET iddocumento = %s
                WHERE id = %s
            """, (nuevo_id, usuario_id))


        # Actualizar tabla usuario
        cursor.execute("""
            UPDATE usuario 
            SET nombres = %s, apellidos = %s, correo = %s, telefono = %s
            WHERE id = %s
        """, (nombres, apellidos, correo, telefono, usuario_id))

        conexion.commit()
        cursor.close()
        conexion.close()
        messages.success(request, "Tus datos se actualizaron correctamente.")
        return redirect('datos_ins')

    cursor.close()
    conexion.close()

    return render(request, "paginas/instructor/datos_ins_editar.html", {
        "usuario": usuario
    })

def coordinador_editar(request):
    return render(request, "paginas/coordinador/coordinador_editar.html")

def coordinador_agregar(request):
    return render(request, "paginas/coordinador/coordinador_agregar.html")

def carpetas2_editar(request):
    return render(request, "paginas/instructor/carpetas2_editar.html")

def carpetas2_crear(request):
    return render(request, "paginas/instructor/carpetas2_crear.html") 

# LISTAR USUARIOS
def administrar_usuario(request):

    usuarios = (
        Usuario.objects
        .select_related("iddocumento")  # traer tipo y número de documento
        .prefetch_related(
            "usuariorol_set__idrol"     # traer roles relacionados
        )
    )

    return render(request, "paginas/coordinador/administrar_usuario.html", {
        "usuarios": usuarios
    })



# CREAR USUARIO
def administrar_usuario_crear(request):
    if request.method == "POST":
        formulario = UsuarioForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect("administrar_usuario")
    else:
        formulario = UsuarioForm()

    return render(request, "paginas/coordinador/administrar_usuario_crear.html", {
        "formulario": formulario
    })


def administrar_usuario_editar(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == "POST":
        formulario = UsuarioForm(request.POST, instance=usuario)
        if formulario.is_valid():
            formulario.save()
            return redirect("administrar_usuario")
    else:
        initial = {
            "tipo_documento": usuario.iddocumento.id if usuario.iddocumento else None,
            "numero_documento": usuario.iddocumento.numero if usuario.iddocumento else "",
            "rol": usuario.usuariorol_set.first().idrol.id if usuario.usuariorol_set.exists() else None,
        }

        formulario = UsuarioForm(instance=usuario, initial=initial)

    return render(request, "paginas/coordinador/administrar_usuario_editar.html", {
        "formulario": formulario
    })

def eliminar_usuario(request, usuario_id):
    Usuario.objects.filter(id=usuario_id).delete()
    return redirect("administrar_usuario")

def actualizar_contrasena(request):

    if request.method == "POST":

        contrasena_actual = request.POST.get("actual")
        nueva = request.POST.get("nueva")
        confirmar = request.POST.get("confirmar")

        # Obtener ID del usuario en sesión
        id_usuario = request.session.get("id_usuario")

        if not id_usuario:
            messages.error(request, "No se encontró el usuario en la sesión.")
            return redirect("configuracion_instructor")

        try:
            # Conexión a la BD
            conexion = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            cursor = conexion.cursor(dictionary=True)

            # Obtener la contraseña actual
            cursor.execute("SELECT contrasena FROM usuario WHERE id = %s", (id_usuario,))
            usuario = cursor.fetchone()

            if not usuario:
                messages.error(request, "Usuario no encontrado.")
                return redirect("configuracion_instructor")

            # Validar contraseña actual
            if usuario["contrasena"] != contrasena_actual:
                messages.error(request, "La contraseña actual es incorrecta.")
                return redirect("configuracion_instructor")

            # Validar coincidencia
            if nueva != confirmar:
                messages.error(request, "Las contraseñas nuevas no coinciden.")
                return redirect("configuracion_instructor")

            # Actualizar contraseña
            cursor.execute(
                "UPDATE usuario SET contrasena = %s WHERE id = %s",
                (nueva, id_usuario)
            )
            conexion.commit()

            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect("configuracion_instructor")

        except mysql.connector.Error as error:
            messages.error(request, f"Error de base de datos: {error}")
            return redirect("configuracion_instructor")

        finally:
            try:
                cursor.close()
                conexion.close()
            except:
                pass

    return redirect("configuracion_instructor")


def seleccionar_ficha(request, id_ficha):
    # Guardamos la ficha seleccionada en la sesión
    request.session['ficha_id'] = id_ficha
    # Redirigimos a la pantalla principal del coordinador
    return redirect('inicio_coordinador')

def eliminar_instructor(request, usuario_id, ficha_id):
    FichaUsuario.objects.filter(
        idusuario_id=usuario_id,
        idficha_id=ficha_id
    ).delete()
    messages.success(request, "Instructor eliminado correctamente.")
    return redirect(f"/configuracion_coordinador/?ficha={ficha_id}")
