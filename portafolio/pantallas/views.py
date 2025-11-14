import mysql.connector
from django.shortcuts import render, redirect
from django.contrib import messages
import os
from dotenv import load_dotenv

load_dotenv() 

def plantillains(request):
    return render(request, "paginas/instructor/plantilla.html", )

def agregar_evidencia(request):
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

    usuario_nombre = request.session['usuario']

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT id FROM usuario WHERE usuario = %s", (usuario_nombre,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        conexion.close()
        return redirect('sesion')

    id_usuario = usuario['id']

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
    return render(request, "paginas/instructor/evidencias.html")


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
        host="localhost",
        user="administrador",
        password="proyecto21mpsena",
        database="proyecto"
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

def evidencia_guia(request):
    return render(request, "paginas/instructor/evidencia_guia.html")

def evidencia_guia1(request):
    return render(request, "paginas/instructor/evidencia_guia1.html")

def inicio(request):
    return render(request, "paginas/aprendiz/inicio.html")


def carpetas_aprendiz1(request):
    return render(request, "paginas/instructor/carpetas_aprendiz1.html")

def carpetas_aprendiz2(request):
    return render(request, "paginas/instructor/carpetas_aprendiz2.html")


def coordinador(request):
    return render(request, "paginas/coordinador/coordinador.html")

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
    return render(request, "paginas/coordinador/inicio_coordinador.html")

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
                # ✅ Buscar el rol del usuario
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
                        request.session['usuario'] = usuario['usuario']
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
    return render(request, "paginas/coordinador/configuracion_coordinador.html")

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

def carpeta2_editar(request):
    return render(request, "paginas/instructor/carpeta2_editar.html")

def carpeta2_crear(request):
    return render(request, "paginas/instructor/carpeta2_crear.html")

