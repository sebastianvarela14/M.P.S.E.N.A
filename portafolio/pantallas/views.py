import mysql.connector
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import os
from dotenv import load_dotenv
from .forms import UsuarioForm
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from .models import Usuario, UsuarioRol, Rol, Ficha, FichaUsuario, NombreAsignatura, TipoAsignatura
from .models import *
from django.conf import settings


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

        nombre_archivo = archivo.name if archivo else "No subido"

        try:
            conexion = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            cursor = conexion.cursor()

            # ⿡ INSERT en evidencias_instructor
            cursor.execute("""
                INSERT INTO evidencias_instructor 
                (titulo, instrucciones, calificacion, fecha_de_entrega, archivo)
                VALUES (%s, %s, %s, %s, %s)
            """, (titulo, instrucciones, calificacion, fecha_entrega, nombre_archivo))
            conexion.commit()

            # ⿢ Obtener el id de la evidencia recién creada
            id_evidencia = cursor.lastrowid

            # ⿣ Obtener la ficha actual desde la sesión
            id_ficha = request.session.get("ficha_id")

            # ⿤ Registrar la evidencia en evidencias_ficha
            cursor.execute("""
                INSERT INTO evidencias_ficha (idficha, idevidencias_instructor)
                VALUES (%s, %s)
            """, (id_ficha, id_evidencia))
            conexion.commit()

            messages.success(request, "Evidencia agregada y vinculada a la ficha.")

        except mysql.connector.Error as err:
            messages.error(request, f"Error al agregar la evidencia: {err}")

        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()
        return redirect('evidencias')
    return render(request, "paginas/instructor/agregar_evidencia.html")

def calificaciones(request):
    ficha_id = request.session.get("ficha_actual")
    if not ficha_id:
        messages.error(request, "Por favor, selecciona una ficha primero.")
        return redirect('fichas_ins')

    try:
        ficha = Ficha.objects.select_related('idprograma').get(id=ficha_id)
        guias_ficha = EvidenciasInstructor.objects.filter(
            evidenciasficha__idficha=ficha_id
        ).order_by('id').distinct()

        aprendices = Usuario.objects.filter(
            fichausuario__idficha_id=ficha_id,
            usuariorol__idrol__tipo='aprendiz'
        ).order_by('apellidos', 'nombres').distinct()
        
        aprendices_calificaciones = []
        for aprendiz in aprendices:
            calificaciones_aprendiz = []
            for guia in guias_ficha:
                entrega = EvidenciasAprendiz.objects.filter(idusuario=aprendiz, idevidencias_instructor=guia).first()

                if entrega and entrega.calificacion:
                    calificaciones_aprendiz.append({
                        "texto": entrega.calificacion,
                        "clase_css": "text-success",
                        "url": "#" 
                    })
                else:
                    calificaciones_aprendiz.append({
                        "texto": "Sin calificar",
                        "clase_css": "text-warning",
                        "url": "#" 
                    })
            
            aprendices_calificaciones.append({"aprendiz": aprendiz, "calificaciones": calificaciones_aprendiz})

        return render(request, "paginas/instructor/calificaciones.html", {
            "ficha": ficha,
            "guias_ficha": guias_ficha,
            "aprendices_calificaciones": aprendices_calificaciones
        })
    except Ficha.DoesNotExist:
        messages.error(request, "La ficha seleccionada no existe.")
        return redirect('fichas_ins')

def material(request):
    return render(request, "paginas/instructor/material.html")

def portafolio_aprendices(request, ficha_id):

    # Guardar ficha para otras vistas si la necesitas
    request.session["ficha_actual"] = ficha_id

    aprendices = []

    # Buscar todos los usuarios asociados a esa ficha
    usuarios_ficha = FichaUsuario.objects.filter(idficha=ficha_id)

    # Rol aprendiz
    rol_aprendiz = Rol.objects.get(tipo="aprendiz")

    # Filtrar aprendices
    for relacion in usuarios_ficha:
        usuario = relacion.idusuario
        if UsuarioRol.objects.filter(idusuario=usuario, idrol=rol_aprendiz).exists():
            aprendices.append(usuario)

    return render(request, "paginas/instructor/portafolio_aprendices.html", {
        "aprendices": aprendices
    })


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
    ficha_id = request.session.get('ficha_id')

    if not ficha_id:
        return HttpResponse("No hay ficha seleccionada")

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)

    # Traer evidencias SOLO de la ficha seleccionada
    query = """
        SELECT ei.*
        FROM evidencias_instructor ei
        INNER JOIN evidencias_ficha ef ON ei.id = ef.idevidencias_instructor
        WHERE ef.idficha = %s
    """
    cursor.execute(query, (ficha_id,))
    evidencias = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render(request, "paginas/instructor/evidencias.html", {"evidencias": evidencias})

def material2(request):
    return render(request, "paginas/instructor/material2.html")

def tareas(request):
    return render(request, "paginas/aprendiz/tareas.html")

def tareas_2(request):
    return render(request, "paginas/aprendiz/tareas_2.html")

def lista_aprendices(request):
    ficha_id = request.session.get("ficha_actual")

    if not ficha_id:
        messages.error(request, "Por favor, selecciona una ficha primero.")
        return redirect('fichas_ins')

    aprendices = Usuario.objects.filter(
        fichausuario__idficha_id=ficha_id,
        usuariorol__idrol__tipo='aprendiz'
    ).order_by('apellidos', 'nombres').distinct()
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
    # 1. Intentar obtener ficha desde la URL ?ficha=xx
    ficha_id = request.GET.get("ficha")

    # 2. Si viene en el GET, guardarla en sesión
    if ficha_id:
        request.session["ficha_id"] = ficha_id
    else:
        # 3. Si no viene, intentar recuperarla desde la sesión
        ficha_id = request.session.get("ficha_id")

    # 4. Enviar ficha_id al template (IMPORTANTE)
    return render(request, "paginas/instructor/carpetas2.html", {
        "ficha_id": ficha_id
    })


def portafolio(request, ficha_id):
    ficha = Ficha.objects.get(id=ficha_id)

    return render(request, "paginas/instructor/portafolio.html", {
        "ficha": ficha
    })

def taller(request):
    return render(request, "paginas/instructor/taller.html")

import unicodedata

def normalizar(texto):
    if not texto:
        return ""
    texto = texto.lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn')
    return texto.strip()


def normalizar(texto):
    """Convierte texto a minúsculas y elimina tildes para comparar correctamente."""
    if not texto:
        return ""
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto.strip()


def carpetasins(request):
    # Orden personalizado normalizado
    orden = [
        "plan concertado",
        "guias de aprendizaje",
        "evidencias de aprendizaje",
        "planes de accion de mejora",
        "formato diligenciado de planeacion, seguimiento y evaluacion etapa productiva."
    ]

    orden_normalizado = [normalizar(o) for o in orden]

    # Obtener carpetas desde BD
    carpetas = Carpetas.objects.all()

    # Ordenarlas según el orden definido
    carpetas = sorted(
        carpetas,
        key=lambda c: (
            orden_normalizado.index(normalizar(c.nombre))
            if normalizar(c.nombre) in orden_normalizado
            else 999
        )
    )

    # Agregar archivos a cada carpeta
    for carpeta in carpetas:
        carpeta.archivos = Archivos.objects.filter(idcarpetas=carpeta.id)

    return render(request, "paginas/instructor/carpetasins.html", {
        "carpetas": carpetas
    })


def archivo_agregar(request, carpeta_id):
    carpeta = get_object_or_404(Carpetas, id=carpeta_id)

    if request.method == "POST":
        archivo_subido = request.FILES.get("archivo")

        Archivos.objects.create(
            nombre_archivo=request.POST.get("nombre_archivo"),
            fecha_entrega=request.POST.get("fecha_entrega"),
            archivo=archivo_subido,
            idcarpetas=carpeta
        )
        return redirect("carpetasins")

    return render(request, "paginas/instructor/archivo_form.html", {
        "carpeta": carpeta,
    })


def archivo_editar(request, archivo_id):
    archivo = get_object_or_404(Archivos, id=archivo_id)

    if request.method == "POST":
        archivo.nombre_archivo = request.POST.get("nombre_archivo")
        archivo.fecha_entrega = request.POST.get("fecha_entrega")
        archivo.save()
        return redirect("carpetasins")

    return render(request, "paginas/instructor/archivo_form.html", {
        "archivo": archivo,
    })


def archivo_eliminar(request, archivo_id):
    archivo = get_object_or_404(Archivos, id=archivo_id)
    archivo.delete()
    return redirect("carpetasins")


def trimestre(request):
    ficha_id = request.session.get("ficha_actual")
    ficha_actual = None
    trimestres = []

    if ficha_id:
        ficha_actual = Ficha.objects.get(id=ficha_id)

        tipo_programa = ficha_actual.idprograma.programa.lower()

        if "tecnico" in tipo_programa:
            trimestres = [1, 2, 3]
        elif "tecnologo" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]
                    # Nuevas reglas
        elif "articulacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5]

        elif "cadena" in tipo_programa or "cadena de formacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]

        elif "adso" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

        elif "mixta" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

    return render(request, "paginas/instructor/trimestre.html", {
        "ficha": ficha_actual,
        "trimestres": trimestres
    })

def carpetas_aprendiz(request):
    return render(request, "paginas/instructor/carpetas_aprendiz.html")

def trimestre_aprendiz(request):
    ficha_id = request.session.get("ficha_actual")
    ficha_actual = None
    trimestres = []

    if ficha_id:
        ficha_actual = Ficha.objects.get(id=ficha_id)

        tipo_programa = ficha_actual.idprograma.programa.lower()

        if "tecnico" in tipo_programa:
            trimestres = [1, 2, 3]
        elif "tecnologo" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]

        elif "articulacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5]

        elif "cadena" in tipo_programa or "cadena de formacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]

        elif "adso" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

        elif "mixta" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

    return render(request, "paginas/instructor/trimestre_aprendiz.html", {
        "ficha": ficha_actual,
        "trimestres": trimestres
    })


def trimestre_general(request):
    return render(request, "paginas/instructor/trimestre_general.html")

def carpetas(request):
    return render(request, "paginas/instructor/carpetas.html")

def material_principal(request):
    materiales = Material.objects.all().order_by('-id')
    return render(request, "paginas/instructor/material_principal.html", {
        "materiales": materiales
    })

def adentro_material(request, id):
    # Obtener el material
    material = get_object_or_404(Material, id=id)

    # PROCESAR ELIMINACIÓN DE ARCHIVO
    if request.method == "POST" and "eliminar_archivo" in request.POST:
        # Guardar el nombre del archivo para borrarlo del disco si quieres
        archivo_path = os.path.join(settings.MEDIA_ROOT, material.archivo) if material.archivo else None

        # Eliminar el archivo de la base de datos
        material.archivo = ""
        material.save()

        # Eliminar físicamente el archivo del disco (opcional)
        if archivo_path and os.path.exists(archivo_path):
            os.remove(archivo_path)

        messages.success(request, "Archivo eliminado correctamente.")
        return redirect("adentro_material", id=material.id)

    if request.method == "POST" and "eliminar_material" in request.POST:
        material.delete()
        messages.success(request, f"El material '{material.titulo}' ha sido eliminado.")
        return redirect("material_principal")


    # Renderizar template
    return render(request, "paginas/instructor/adentro_material.html", {
        "material": material
    })

def lista_aprendices1(request):
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

    return render(request, "paginas/aprendiz/lista_aprendices1.html", {
        "aprendices": aprendices
    })

def datoslaura(request):
    return render(request, "paginas/aprendiz/datoslaura.html")


def adentro_material1(request):
    return render(request, "paginas/instructor/adentro_material1.html")

def evidencia_guia(request, evidencia_id):
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("SELECT * FROM evidencias_instructor WHERE id = %s", (evidencia_id,))
        evidencia = cursor.fetchone()

        if not evidencia:
            messages.error(request, "La evidencia no existe.")
            return redirect("evidencias")

    finally:
        cursor.close()
        conexion.close()

    return render(request, "paginas/instructor/evidencia_guia.html", {
        "evidencia": evidencia
    })


def evidencia_guia1(request):
    return render(request, "paginas/instructor/evidencia_guia1.html")

def inicio(request):
    id_aprendiz = request.session.get('id_usuario')
    nombre_aprendiz = request.session.get('nombre_usuario', '')

    asignaturas = []

    if id_aprendiz:

        # 1️⃣ Obtener la ficha a la que pertenece el aprendiz
        ficha_usuario = FichaUsuario.objects.filter(idusuario_id=id_aprendiz).first()

        if ficha_usuario:
            ficha_id = ficha_usuario.idficha_id

            # 2️⃣ Obtener las asignaturas asignadas a esa ficha
            asignaturas = NombreAsignatura.objects.filter(
                fichaasignatura__idficha_id=ficha_id
            ).distinct()

    return render(request, "paginas/aprendiz/inicio.html", {
        'asignaturas': asignaturas,
        'nombre_aprendiz': nombre_aprendiz
    })



def carpetas_aprendiz1(request):
    return render(request, "paginas/instructor/carpetas_aprendiz1.html")

def carpetas_aprendiz2(request):
    return render(request, "paginas/instructor/carpetas_aprendiz2.html")


def coordinador(request):
    ficha_id = request.GET.get("ficha")
    ficha_actual = None

    # Guardar ficha seleccionada en sesión
    if ficha_id:
        request.session["ficha_actual"] = ficha_id
        try:
            ficha_actual = Ficha.objects.get(id=ficha_id)
        except Ficha.DoesNotExist:
            ficha_actual = None
    else:
        # Si entra sin seleccionar ficha, mirar la sesión
        ficha_session = request.session.get("ficha_actual")
        if ficha_session:
            ficha_actual = Ficha.objects.get(id=ficha_session)

    fichas = Ficha.objects.all()

    return render(request, "paginas/coordinador/coordinador.html", {
        "fichas": fichas,
        "ficha": ficha_actual
    })

def entrada(request, asignatura_id):
    request.session["asignatura_actual"] = asignatura_id  # guardar asignatura actual

    asignatura = NombreAsignatura.objects.get(id=asignatura_id)

    return render(request, "paginas/aprendiz/entrada.html", {
        "asignatura": asignatura
    })

def trimestre_laura(request):
    ficha_id = request.session.get("ficha_actual")
    ficha_actual = None
    trimestres = []

    if ficha_id:
        ficha_actual = Ficha.objects.get(id=ficha_id)

        tipo_programa = ficha_actual.idprograma.programa.lower()

        if "tecnico" in tipo_programa:
            trimestres = [1, 2, 3]
        elif "tecnologo" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]
                    # Nuevas reglas
        elif "articulacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5]

        elif "cadena" in tipo_programa or "cadena de formacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]

        elif "adso" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

        elif "mixta" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

    return render(request, "paginas/aprendiz/trimestre_laura.html", {
        "ficha": ficha_actual,
        "trimestres": trimestres
    })

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
    ficha_id = request.GET.get("ficha")
    ficha_actual = None

    # Guardar ficha seleccionada en sesión
    if ficha_id:
        request.session["ficha_actual"] = ficha_id
        try:
            ficha_actual = Ficha.objects.get(id=ficha_id)
        except Ficha.DoesNotExist:
            ficha_actual = None
    else:
        # Si entra sin seleccionar ficha, mirar la sesión
        ficha_session = request.session.get("ficha_actual")
        if ficha_session:
            ficha_actual = Ficha.objects.get(id=ficha_session)

    fichas = Ficha.objects.all()

    return render(request, "paginas/observador/observador.html", {
        "fichas": fichas,
        "ficha": ficha_actual
    })

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

def evidencia_guia_observador(request, id):
    evidencia = EvidenciasInstructor.objects.get(id=id)
    return render(request, "paginas/observador/evidencia_guia_observador.html", {
        "evidencia": evidencia
    })

def evidencias_observador(request, ficha_id):
    evidencias = EvidenciasInstructor.objects.filter(
        evidenciasficha__idficha=ficha_id
    )

    return render(request, "paginas/observador/evidencias_observador.html", {
        "evidencias": evidencias
    })

def adentro_material_coordinador(request):
    return render(request, "paginas/coordinador/adentro_material_coordinador.html")

def carpetas_coordinador(request):
    return render(request, "paginas/coordinador/carpetas_coordinador.html")

def evidencia_guia_coordinador(request, id):
    evidencia = EvidenciasInstructor.objects.get(id=id)
    return render(request, "paginas/coordinador/evidencia_guia_coordinador.html", {
        "evidencia": evidencia
    })

def evidencias_coordinador(request, ficha_id):
    evidencias = EvidenciasInstructor.objects.filter(
        evidenciasficha__idficha=ficha_id
    )

    return render(request, "paginas/coordinador/evidencias_coordinador.html", {
        "evidencias": evidencias
    })

def inicio_coordinador(request):
    ficha_id = request.session.get('ficha_actual')  # ← ahora sí coincide
    return render(request, "paginas/coordinador/inicio_coordinador.html", {"ficha_id": ficha_id})


def lista_aprendices_coordinador(request):
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

        return render(request, "paginas/coordinador/lista_aprendices_coordinador.html", {
            "aprendices": aprendices
    })

def material_principal_coordinador(request):
    return render(request, "paginas/coordinador/material_principal_coordinador.html")

def portafolio_aprendices_coordinador(request):
    ficha_id = request.session.get("ficha_actual")

    aprendices = []

    if ficha_id:
        # 1. Traer usuarios de esa ficha
        usuarios_ficha = FichaUsuario.objects.filter(idficha=ficha_id)

        # 2. Identificar cuáles de esos usuarios son aprendices
        rol_aprendiz = Rol.objects.get(tipo="aprendiz")

        for relacion in usuarios_ficha:
            usuario = relacion.idusuario
            
            # Revisar que el usuario tenga el rol de aprendiz
            if UsuarioRol.objects.filter(idusuario=usuario, idrol=rol_aprendiz).exists():
                aprendices.append(usuario)

    return render(request, "paginas/coordinador/portafolio_aprendices_coordinador.html", {
        "aprendices": aprendices
    })

def portafolio_coordinador(request):
    return render(request, "paginas/coordinador/portafolio_coordinador.html")

def trimestre_coordinador(request):
    ficha_id = request.session.get("ficha_actual")
    ficha_actual = None
    trimestres = []

    if ficha_id:
        ficha_actual = Ficha.objects.get(id=ficha_id)

        tipo_programa = ficha_actual.idprograma.programa.lower()

        if "tecnico" in tipo_programa:
            trimestres = [1, 2, 3]
        elif "tecnologo" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]
                    # Nuevas reglas
        elif "articulacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5]

        elif "cadena" in tipo_programa or "cadena de formacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]

        elif "adso" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

        elif "mixta" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

    return render(request, "paginas/coordinador/trimestre_coordinador.html", {
        "ficha": ficha_actual,
        "trimestres": trimestres
    })

def datos_coordinador(request):
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

    return render(request, "paginas/coordinador/datos_coordinador.html", {
        'usuario': usuario
    })

def datos_coordinador_editar(request):
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
            return redirect('datos_coordinador_editar')
        try:
            numero_documento = int(numero_documento_str)
        except ValueError:
            messages.error(request, "El número de documento debe ser un número válido.")
            return redirect('datos_coordinador_editar')

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
        return redirect('datos_coordinador')

    cursor.close()
    conexion.close()

    return render(request, "paginas/coordinador/datos_coordinador_editar.html", {
        "usuario": usuario
    })

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

def trimestre_general_coordinador(request,):
    ficha_id = request.session.get("ficha_actual")
    ficha_actual = None
    trimestres = []

    if ficha_id:
        ficha_actual = Ficha.objects.get(id=ficha_id)

        tipo_programa = ficha_actual.idprograma.programa.lower()

        if "tecnico" in tipo_programa:
            trimestres = [1, 2, 3]
        elif "tecnologo" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]
                    # Nuevas reglas
        elif "articulacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5]

        elif "cadena" in tipo_programa or "cadena de formacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]

        elif "adso" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

        elif "mixta" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

    return render(request, "paginas/coordinador/trimestre_general_coordinador.html", {
        "ficha": ficha_actual,
        "trimestres": trimestres
    })

def trimestre_aprendiz_coordinador(request, ):
    ficha_id = request.session.get("ficha_actual")
    ficha_actual = None
    trimestres = []

    if ficha_id:
        ficha_actual = Ficha.objects.get(id=ficha_id)

        tipo_programa = ficha_actual.idprograma.programa.lower()

        if "tecnico" in tipo_programa:
            trimestres = [1, 2, 3]
        elif "tecnologo" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]
                    # Nuevas reglas
        elif "articulacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5]

        elif "cadena" in tipo_programa or "cadena de formacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]

        elif "adso" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

        elif "mixta" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

    return render(request, "paginas/coordinador/trimestre_aprendiz_coordinador.html", {
        "ficha": ficha_actual,
        "trimestres": trimestres
    })

def carpetas_aprendiz_coordinador(request):
    return render(request, "paginas/coordinador/carpetas_aprendiz_coordinador.html")

def calificaciones_coordinador(request):
    return render(request, "paginas/coordinador/calificaciones_coordinador.html")

def evidencia_calificar_coordinador(request):
    return render(request, "paginas/coordinador/evidencia_calificar_coordinador.html")

def sesion(request):
    usuario_ingresado = ""

    # Limpiar mensajes antiguos
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

        if contrasena_input != usuario['contrasena']:
            messages.error(request, "Contraseña incorrecta.")
            return redirect('sesion')

        # Guardamos datos base del usuario
        request.session['id_usuario'] = usuario['id']
        request.session['usuario'] = usuario['usuario']
        request.session['nombre_usuario'] = f"{usuario['nombres']} {usuario['apellidos']}".upper()

        # Obtener ROL del usuario
        cursor.execute("""
            SELECT r.tipo
            FROM rol r
            INNER JOIN usuario_rol ur ON ur.idrol = r.id
            WHERE ur.idusuario = %s
        """, (usuario['id'],))
        rol = cursor.fetchone()

        # 🔹 OBTENER FICHA DEL USUARIO Y GUARDARLA EN SESIÓN
        cursor.execute("""
            SELECT idficha 
            FROM ficha_usuario
            WHERE idusuario = %s
        """, (usuario['id'],))

        ficha = cursor.fetchone()
        request.session['ficha_id'] = ficha['idficha'] if ficha else None

        # Redirección según el rol
        if rol:
            tipo_rol = rol['tipo'].lower()

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
    })


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

    # 1. Recuperar ficha desde sesión
    ficha_id = request.session.get("ficha_actual")
    if not ficha_id:
        messages.error(request, "Primero debes seleccionar una ficha.")
        return redirect("inicio_coordinador")

    # 2. Traer objeto ficha para mostrar datos en pantalla
    ficha = Ficha.objects.get(id=ficha_id)

    # ========= INSTRUCTORES =========
    instructores = Usuario.objects.filter(
        usuariorol_idrol_tipo="instructor"
    ).distinct()

    instructores_asignados = Usuario.objects.filter(
        fichausuario__idficha_id=ficha_id,
        usuariorol_idrol_tipo="instructor"
    ).distinct()

    ids_instructores_asignados = [i.id for i in instructores_asignados]

    # ========= APRENDICES =========
    aprendices = Usuario.objects.filter(
        usuariorol_idrol_tipo="aprendiz"
    ).distinct()

    aprendices_asignados = Usuario.objects.filter(
        fichausuario__idficha_id=ficha_id,
        usuariorol_idrol_tipo="aprendiz"
    ).distinct()

    ids_aprendices_asignados = [a.id for a in aprendices_asignados]

    # ========= ASIGNATURAS =========
    todas_asignaturas = NombreAsignatura.objects.all()

    # Asignaturas reales en la ficha
    asignaturas_ficha = FichaAsignatura.objects.filter(
        idficha_id=ficha_id
    ).select_related("idasignatura")

    # IDs asignados (para marcar checkboxes)
    asignadas_ids = list(
        asignaturas_ficha.values_list("idasignatura_id", flat=True)
    )

    # ========= GUARDAR =========
    if request.method == "POST":

        # ---------- Guardar Instructores ----------
        if "instructores" in request.POST:
            seleccionados = request.POST.getlist("instructores")

            FichaUsuario.objects.filter(
                idficha_id=ficha_id,
                idusuario_usuariorolidrol_tipo="instructor"
            ).delete()

            for ins_id in seleccionados:
                FichaUsuario.objects.create(
                    idficha_id=ficha_id,
                    idusuario_id=ins_id
                )

            messages.success(request, "¡Instructores asignados correctamente!")

        # ---------- Guardar Aprendices ----------
        if "aprendices" in request.POST:
            seleccionados = request.POST.getlist("aprendices")

            FichaUsuario.objects.filter(
                idficha_id=ficha_id,
                idusuario_usuariorolidrol_tipo="aprendiz"
            ).delete()

            for apr_id in seleccionados:
                FichaUsuario.objects.create(
                    idficha_id=ficha_id,
                    idusuario_id=apr_id
                )

            messages.success(request, "¡Aprendices asignados correctamente!")

        # ---------- Guardar Asignaturas ----------
        if "asignaturas" in request.POST:
            seleccionadas = request.POST.getlist("asignaturas")
            seleccionadas = [int(x) for x in seleccionadas]

            # Borrar asignaciones antiguas
            FichaAsignatura.objects.filter(idficha_id=ficha_id).exclude(idasignatura_id__in=seleccionadas).delete()

            # Crear nuevas asignaciones
            for asig_id in seleccionadas:
                FichaAsignatura.objects.get_or_create(
                    idficha_id=ficha_id,
                    idasignatura_id=asig_id
                )

            messages.success(request, "Asignaturas guardadas correctamente!")


        return redirect("configuracion_coordinador")

    # ========= RENDER =========
    return render(request, "paginas/coordinador/configuracion_coordinador.html", {
        "ficha": ficha,
        "ficha_id": ficha_id,

        # Instructores
        "instructores": instructores,
        "instructores_asignados": instructores_asignados,
        "ids_instructores_asignados": ids_instructores_asignados,

        # Aprendices
        "aprendices": aprendices,
        "aprendices_asignados": aprendices_asignados,
        "ids_aprendices_asignados": ids_aprendices_asignados,

        # Asignaturas
        "todas_asignaturas": todas_asignaturas,
        "asignaturas_ficha": asignaturas_ficha,
        "asignadas_ids": asignadas_ids,
    })

def evidencia_calificada(request):
    return render(request, "paginas/instructor/evidencia_calificada.html")

def configuracion_coordinador_base(request):
    return render(request, "paginas/coordinador/configuracion_coordinador_base.html")

def configuracion_coordinador_base_2(request):
    return render(request, "paginas/coordinador/configuracion_coordinador_base_2.html")

def ficha_coordinador(request):
    ficha_id = request.session.get("ficha_actual")

    if not ficha_id:
        return redirect("coordinador")

    ficha = Ficha.objects.select_related(
        "idjornada",
        "idprograma",
        "nombre_programa"  
    ).get(id=ficha_id)

    return render(request, "paginas/coordinador/ficha_coordinador.html", {
        "ficha": ficha
    })

def ficha_aprendiz(request):
    usuario_id = request.session.get("id_usuario")

    ficha_info = None

    if usuario_id:
        try:
            # 1. Buscar la relación entre el aprendiz y la ficha
            relacion = FichaUsuario.objects.get(idusuario_id=usuario_id)

            # 2. Obtener la información completa de la ficha
            ficha_info = Ficha.objects.get(id=relacion.idficha_id)

        except FichaUsuario.DoesNotExist:
            ficha_info = None
        except Ficha.DoesNotExist:
            ficha_info = None

    return render(request, "paginas/aprendiz/ficha_aprendiz.html", {
        "ficha": ficha_info
    })

def ficha_aprendiz_2(request):
    return render(request, "paginas/aprendiz/ficha_aprendiz_2.html")

def ficha_instructor(request):
    ficha_id = request.session.get('ficha_actual')

    if not ficha_id:
        messages.error(request, "No se ha seleccionado ninguna ficha. Por favor, vuelve a la lista de fichas.")
        return redirect('fichas_ins')

    try:
        ficha = Ficha.objects.select_related('idjornada', 'idprograma').get(id=ficha_id)

        aprendices = Usuario.objects.filter(
            fichausuario__idficha_id=ficha_id,
            usuariorol_idrol_tipo='aprendiz'
        ).order_by('apellidos', 'nombres').distinct()

    except Ficha.DoesNotExist:
        messages.error(request, "La ficha seleccionada no existe o fue eliminada.")
        return redirect('fichas_ins')

    return render(request, "paginas/instructor/ficha_instructor.html", {
        'ficha': ficha, 
        'aprendices': aprendices
    })

def ficha_observador(request):
    return render(request, "paginas/observador/ficha_observador.html")

def equipo_ejecutor(request):
    ficha_id = request.session.get("ficha_actual")
    ficha_actual = None
    trimestres = []

    if ficha_id:
        ficha_actual = Ficha.objects.get(id=ficha_id)

        tipo_programa = ficha_actual.idprograma.programa.lower()

        if "tecnico" in tipo_programa:
            trimestres = [1, 2, 3]
        elif "tecnologo" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]
                    # Nuevas reglas
        elif "articulacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5]

        elif "cadena" in tipo_programa or "cadena de formacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]

        elif "adso" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

        elif "mixta" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

    return render(request, "paginas/instructor/equipo_ejecutor.html", {
        "ficha": ficha_actual,
        "trimestres": trimestres
    })

def opc_equipoejecutor(request):
    return render(request, "paginas/instructor/opc_equipoejecutor.html")

def fichas_equipoejecutor_coordinador(request):
    return render(request, "paginas/coordinador/fichas_equipoejecutor_coordinador.html")

def equipo_coordinador(request):
    return render(request, "paginas/coordinador/equipo_coordinador.html")

def material_editar(request, id):
    material = get_object_or_404(Material, id=id)

    if request.method == "POST":
        material.titulo = request.POST.get("titulo")
        material.descripcion = request.POST.get("descripcion")
        material.fecha_entrega = request.POST.get("fecha_entrega")

        archivo = request.FILES.get("archivo")
        if archivo:
            material.archivo = archivo

        material.save()

        return redirect("material_principal")

    return render(request, "paginas/instructor/material_editar.html", {
        "material": material
    })

def evidencia_guia_editar(request, evidencia_id):

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)

    # Obtener la evidencia
    cursor.execute("SELECT * FROM evidencias_instructor WHERE id = %s", (evidencia_id,))
    evidencia = cursor.fetchone()

    if not evidencia:
        messages.error(request, "La evidencia no existe.")
        return redirect("evidencia_guia", evidencia_id)

    # Si envían POST → actualizar
    if request.method == "POST":
        nuevo_titulo = request.POST.get("titulo")
        nuevas_instrucciones = request.POST.get("instrucciones")

        archivo = request.FILES.get("archivo")

        # Si suben un archivo nuevo → reemplazar
        if archivo:
            nombre_archivo = archivo.name

            # Guardar archivo físico
            ruta = f"media/evidencias/{nombre_archivo}"
            with open(ruta, "wb+") as destino:
                for chunk in archivo.chunks():
                    destino.write(chunk)

            cursor.execute("""
                UPDATE evidencias_instructor
                SET titulo = %s, instrucciones = %s, archivo = %s
                WHERE id = %s
            """, (nuevo_titulo, nuevas_instrucciones, nombre_archivo, evidencia_id))

        else:
            cursor.execute("""
                UPDATE evidencias_instructor
                SET titulo = %s, instrucciones = %s
                WHERE id = %s
            """, (nuevo_titulo, nuevas_instrucciones, evidencia_id))

        conexion.commit()
        cursor.close()
        conexion.close()

        messages.success(request, "La evidencia fue actualizada correctamente.")
        return redirect("evidencia_guia", evidencia_id)

    cursor.close()
    conexion.close()

    return render(request, "paginas/instructor/evidencia_guia_editar.html", {
        "evidencia": evidencia
    })

def eliminar_archivo_evidencia(request, evidencia_id):
    evidencia = get_object_or_404(EvidenciasInstructor, id=evidencia_id)

    if evidencia.archivo:
        archivo_path = evidencia.archivo.path
        
        # Validar que el archivo realmente exista
        if os.path.exists(archivo_path):
            os.remove(archivo_path)

        evidencia.archivo = None
        evidencia.save()

    return redirect("evidencia_guia_editar", evidencia_id)


def carpetasins_editar(request, carpeta_id):
    carpeta = get_object_or_404(Carpetas, id=carpeta_id)

    if request.method == "POST":
        carpeta.nombre = request.POST.get("nombre")
        carpeta.descripcion = request.POST.get("descripcion")
        carpeta.save()
        return redirect("carpetasins")

    return render(request, "paginas/instructor/carpetasins_editar.html", {
        "carpeta": carpeta,
    })


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

def coordinador_editar(request, id):
    ficha = get_object_or_404(Ficha, id=id)
    jornadas = Jornada.objects.all()
    programas = Programa.objects.all()
    nombres_programa = NombrePrograma.objects.all()

    if request.method == "POST":
        ficha.numero_ficha = request.POST.get("numero_ficha")
        ficha.idjornada_id = request.POST.get("idjornada")
        ficha.idprograma_id = request.POST.get("idprograma")
        ficha.nombre_programa_id = request.POST.get("nombre_programa")
        ficha.estado = request.POST.get("estado")

        ficha.save()
        return redirect("coordinador")

    return render(request, "paginas/coordinador/coordinador_editar.html", {
        "ficha": ficha,
        "jornadas": jornadas,
        "programas": programas,
        "nombres_programa": nombres_programa
    })


def coordinador_agregar(request):
    jornadas = Jornada.objects.all()
    programas = Programa.objects.all()
    nombres_programa = NombrePrograma.objects.all()

    if request.method == "POST":
        numero = request.POST.get("numero_ficha")
        aprendices = request.POST.get("numero_aprendices")
        estado = request.POST.get("estado")

        jornada = request.POST.get("idjornada")
        programa = request.POST.get("idprograma")
        nombre_programa = request.POST.get("nombre_programa")

        Ficha.objects.create(
            numero_ficha=numero,
            estado=estado,
            idjornada_id=jornada,
            idprograma_id=programa,
            nombre_programa_id=nombre_programa
        )

        return redirect("coordinador")

    return render(request, "paginas/coordinador/coordinador_agregar.html", {
        "jornadas": jornadas,
        "programas": programas,
        "nombres_programa": nombres_programa
    })


def agregar_jornada(request):

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )
    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.POST["nombre"].strip().upper()

        # Validar duplicado
        cursor.execute("SELECT id FROM jornada WHERE nombre = %s", (nombre,))
        existente = cursor.fetchone()

        if existente:
            messages.error(request, "❗ Esta jornada ya existe.")
            return redirect("coordinador_agregar")

        cursor.execute("INSERT INTO jornada (nombre) VALUES (%s)", (nombre,))
        conexion.commit()

        return redirect("coordinador_agregar")

    return render(request, "paginas/coordinador/agregar_jornada.html")



def agregar_programa(request):

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )
    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.POST["programa"].strip().upper()

        # Validar duplicado
        cursor.execute("SELECT id FROM programa WHERE programa = %s", (nombre,))
        existente = cursor.fetchone()

        if existente:
            messages.error(request, "❗ Este programa ya existe.")
            return redirect("coordinador_agregar")

        cursor.execute("INSERT INTO programa (programa) VALUES (%s)", (nombre,))
        conexion.commit()

        return redirect("coordinador_agregar")

    return render(request, "paginas/coordinador/agregar_programa.html")



def agregar_nombre_programa(request):

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )
    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.POST["nombre"].strip().upper()

        # Validar duplicado
        cursor.execute("SELECT id FROM nombre_programa WHERE nombre = %s", (nombre,))
        existente = cursor.fetchone()

        if existente:
            messages.error(request, "❗ Este nombre de programa ya existe.")
            return redirect("coordinador_agregar")

        cursor.execute("INSERT INTO nombre_programa (nombre) VALUES (%s)", (nombre,))
        conexion.commit()

        return redirect("coordinador_agregar")

    return render(request, "paginas/coordinador/agregar_nombre_programa.html")


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
    request.session['ficha_actual'] = id_ficha
    # Redirigimos a la pantalla principal del coordinador
    return redirect('inicio_coordinador')

def eliminar_instructor(request, usuario_id, ficha_id):
    FichaUsuario.objects.filter(
        idusuario_id=usuario_id,
        idficha_id=ficha_id
    ).delete()
    messages.success(request, "Instructor eliminado correctamente.")
    return redirect(f"/configuracion_coordinador/?ficha={ficha_id}")

def eliminar_aprendiz(request, aprendiz_id, ficha_id):
    if request.method == "POST":
        FichaUsuario.objects.filter(
            idficha_id=ficha_id,
            idusuario_id=aprendiz_id
        ).delete()

        messages.success(request, "Aprendiz eliminado correctamente.")

    return redirect("configuracion_coordinador")

def configuracion_asignaturas(request):
    ficha_id = request.session.get("ficha_actual")
    if not ficha_id:
        messages.error(request, "Primero debes seleccionar una ficha.")
        return redirect("inicio_coordinador")

    ficha = Ficha.objects.get(id=ficha_id)

    # Todas las asignaturas
    todas_asignaturas = NombreAsignatura.objects.all()

    # Asignaciones (traer la asignatura relacionada para evitar N+1 y para comprobar nombre)
    asignaturas_ficha = FichaAsignatura.objects.filter(idficha=ficha).select_related('idasignatura')

    # IDs ya asignados (como ints)
    asignadas_ids = list(asignaturas_ficha.values_list("idasignatura_id", flat=True))
    # diagnóstico en consola
    print("DEBUG asignadas_ids:", asignadas_ids)
    print("DEBUG asignaturas_ficha count:", asignaturas_ficha.count())
    # muestra primeros 5 tuplas (ida, nombre) para verificar
    for fa in asignaturas_ficha[:5]:
        print("DEBUG fa:", fa.id, "idasignatura_id=", getattr(fa, "idasignatura_id", None),
              "nombre_rel=", getattr(fa.idasignatura, "nombre", None))

    if request.method == "POST":
        seleccionadas = request.POST.getlist("asignaturas")  # vienen como strings
        print("DEBUG seleccionadas raw:", seleccionadas)
        seleccionadas = [int(x) for x in seleccionadas]  # normalizamos a ints
        print("DEBUG seleccionadas ints:", seleccionadas)

        # Eliminar asignaciones no seleccionadas
        FichaAsignatura.objects.filter(idficha=ficha).exclude(idasignatura_id__in=seleccionadas).delete()

        # Crear/garantizar nuevas asignaciones
        for asig_id in seleccionadas:
            FichaAsignatura.objects.get_or_create(idficha=ficha, idasignatura_id=asig_id)

        messages.success(request, "Asignaturas actualizadas correctamente.")
        return redirect("configuracion_asignaturas")

    return render(request, "paginas/coordinador/configuracion_asignaturas.html", {
        "ficha": ficha,
        "todas_asignaturas": todas_asignaturas,
        "asignadas_ids": asignadas_ids,
        "asignaturas_ficha": asignaturas_ficha,
        "ficha_id": ficha_id,
    })
def eliminar_asignatura(request, ficha_id, asig_id):
    try:
        FichaAsignatura.objects.filter(
            idficha_id=ficha_id,
            idasignatura_id=asig_id
        ).delete()

        messages.success(request, "Asignatura eliminada de la ficha.")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("configuracion_coordinador")

def eliminar_evidencia(request, evidencia_id):

    # 1. Buscar la evidencia de instructor
    evidencia = EvidenciasInstructor.objects.get(id=evidencia_id)

    # 2. Buscar relación en EvidenciasFicha
    evidencia_ficha = EvidenciasFicha.objects.filter(
        idevidencias_instructor=evidencia
    ).first()

    # 4. Primero eliminar la relación (evita el IntegrityError)
    if evidencia_ficha:
        evidencia_ficha.delete()

    # 5. Ahora sí eliminar la evidencia sin violar la FK
    evidencia.delete()

    messages.success(request, "La evidencia fue eliminada correctamente.")

    # 6. Redirigir SIEMPRE a la lista de evidencias
    return redirect("evidencias")




def datos_coor(request, id):
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

    return render(request, "paginas/coordinador/datos_coor.html", {
        "aprendiz": aprendiz
    })


def ficha_coordinador_editar(request, id):
    ficha = get_object_or_404(Ficha, id=id)
    jornadas = Jornada.objects.all()
    programas = Programa.objects.all()
    nombres_programa = NombrePrograma.objects.all()

    if request.method == "POST":
        ficha.numero_ficha = request.POST.get("numero_ficha")
        ficha.idjornada_id = request.POST.get("idjornada")
        ficha.idprograma_id = request.POST.get("idprograma")
        ficha.nombre_programa_id = request.POST.get("nombre_programa")
        ficha.estado = request.POST.get("estado")   # ← Agregado

        ficha.save()
        return redirect("ficha_coordinador")

    return render(request, "paginas/coordinador/ficha_coordinador_editar.html", {
        "ficha": ficha,
        "jornadas": jornadas,
        "programas": programas,
        "nombres_programa": nombres_programa
    })

def seleccionar_ficha_observador(request, id_ficha):
    # Guardamos la ficha seleccionada en la sesión
    request.session['ficha_actual'] = id_ficha
    # Redirigimos a la pantalla principal del coordinador
    return redirect('inicio_observador')

def equipo_ejecutor_coordinador(request):
    ficha_id = request.session.get("ficha_actual")
    ficha_actual = None
    trimestres = []

    if ficha_id:
        ficha_actual = Ficha.objects.get(id=ficha_id)

        tipo_programa = ficha_actual.idprograma.programa.lower()

        if "tecnico" in tipo_programa:
            trimestres = [1, 2, 3]
        elif "tecnologo" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]
                    # Nuevas reglas
        elif "articulacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5]

        elif "cadena" in tipo_programa or "cadena de formacion" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6]

        elif "adso" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

        elif "mixta" in tipo_programa:
            trimestres = [1, 2, 3, 4, 5, 6, 7]

    return render(request, "paginas/coordinador/equipo_ejecutor_coordinador.html", {
        "ficha": ficha_actual,
        "trimestres": trimestres
    })


def opc_equipoejecutor_coordinador(request):
    usuario = request.session.get("id_usuario")

    # 1. Verificar rol
    es_coordinador = UsuarioRol.objects.filter(
        idusuario=usuario,
        idrol__tipo="coordinacion"
    ).exists()

    if not es_coordinador:
        return HttpResponse("<h3 style='color:red;'>No eres coordinador</h3>")

    # 2. Ficha seleccionada
    ficha_id = request.session.get("ficha_actual")
    if not ficha_id:
        return HttpResponse("<h3>No hay ficha seleccionada</h3>")

    ficha = Ficha.objects.get(id=ficha_id)

    # 3. Carpetas
    carpetas = FichaCarpetas.objects.filter(idficha=ficha_id)

    # 4. Archivos
    data = []
    for fc in carpetas:
        archivos = Archivos.objects.filter(idcarpetas=fc.idcarpetas)
        data.append({
            "carpeta": fc.idcarpetas,
            "archivos": archivos
        })

    return render(request, "paginas/coordinador/opc_equipoejecutor_coordinador.html", {
        "data": data,
        "ficha": ficha
    })

def crear_material(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        archivo = request.FILES.get("archivo")

        nuevo = Material(
            titulo=titulo,
            descripcion=descripcion,
            archivo=archivo 
        )
        nuevo.save()

        return redirect("material_principal")

    return render(request, "paginas/instructor/crear_material.html")