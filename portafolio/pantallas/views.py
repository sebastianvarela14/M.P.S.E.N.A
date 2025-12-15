import mysql.connector
import os
import shutil
import re
import pandas as pd
import requests 

from dotenv import load_dotenv

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError
from django.db.models import Q 
from django.utils import timezone

from .forms import UsuarioForm
from .models import *
from pantallas.models import Usuario, Documento, Rol, UsuarioRol 
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
        id_asignatura = request.POST.get('idasignatura')

        # 🔑 Obtener ficha desde sesión
        ficha_id = request.session.get("ficha_id")
        if not ficha_id:
            messages.error(request, "No se encontró la ficha seleccionada.")
            return redirect('evidencias')

        try:
            ficha = Ficha.objects.get(id=ficha_id)
        except Ficha.DoesNotExist:
            messages.error(request, "Ficha no encontrada.")
            return redirect('evidencias')

        # 🔑 Obtener instructor
        instructor_id = (
            request.user.id
            if request.user.is_authenticated
            else request.session.get("usuario_id")
        )

        if not instructor_id:
            messages.error(request, "Instructor no identificado.")
            return redirect('evidencias')

        # 📂 Guardar archivo físico
        nombre_archivo = "No subido"
        if archivo:
            fs = FileSystemStorage(location='media/evidencias/')
            nombre_archivo = fs.save(archivo.name, archivo)

        # 1️⃣ Crear Evidencia Instructor (El registro primario del archivo)
        evidencia = EvidenciasInstructor.objects.create(
            titulo=titulo,
            instrucciones=instrucciones,
            calificacion=calificacion,
            fecha_de_entrega=fecha_entrega,
            archivo=nombre_archivo, # <-- Aquí se guarda la ruta del archivo
            idinstructor_id=instructor_id,
            idasignatura_id=id_asignatura
        )

        # 2️⃣ Relacionar evidencia con ficha
        EvidenciasFicha.objects.create(
            idficha=ficha,
            idevidencias_instructor=evidencia
        )

        # 3️⃣ Obtener carpeta "Guias de aprendizaje"
        try:
            carpeta_guias = Carpetas.objects.get(
                nombre__icontains="guias de aprendizaje"
            )
        except Carpetas.DoesNotExist:
            messages.warning(
                request,
                "La carpeta 'Guias de aprendizaje' no existe. Créala primero."
            )
            return redirect('evidencias')

        # 4️⃣ Asegurar relación ficha ↔ carpeta
        FichaCarpetas.objects.get_or_create(
            idficha=ficha,
            idcarpetas=carpeta_guias
        )

        # 5️⃣ Crear registro en PortafolioInstructor (CORRECCIÓN CLAVE: ASIGNAR EL ARCHIVO)
        # Este es el registro que usa el aprendiz en 'carpetas_laura'
        PortafolioInstructor.objects.create(
            titulo_archivo=titulo,
            ficha=ficha,
            carpeta=carpeta_guias,
            trimestre=ficha.trimestre_actual,
            idinstructor_id=instructor_id,
            idevidencias_instructor=evidencia,
            archivo=nombre_archivo # 🔑 ¡CLAVE! Se sincroniza la ruta del archivo aquí
        )

        messages.success(
            request,
            f"Evidencia creada y agregada al portafolio "
            f"(Trimestre {ficha.trimestre_actual})."
        )
        return redirect('evidencias')

    return render(
        request,
        "paginas/instructor/agregar_evidencia.html"
    )


def agregar_evidencia_coor(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        instrucciones = request.POST.get('instrucciones')
        calificacion = request.POST.get('calificacion')
        fecha_entrega = request.POST.get('fecha_de_entrega')
        archivo = request.FILES.get('archivo')

        nombre_archivo = archivo.name if archivo else "No subido"

        # 🔹 Agregar guardado del archivo en media/evidencias/
        ruta_archivo_guardado = None
        if archivo:
            fs = FileSystemStorage(location='media/evidencias/')
            filename = fs.save(archivo.name, archivo)  # Guarda el archivo y obtiene el nombre
            ruta_archivo_guardado = fs.path(filename)  # Ruta física completa (opcional, si necesitas usarla después)
            nombre_archivo = filename  # Usar el nombre guardado para la DB (incluye subcarpetas si las hay)

        try:
            conexion = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            cursor = conexion.cursor()

            # 1️⃣ INSERT en evidencias_instructor
            cursor.execute("""
                INSERT INTO evidencias_instructor 
                (titulo, instrucciones, calificacion, fecha_de_entrega, archivo)
                VALUES (%s, %s, %s, %s, %s)
            """, (titulo, instrucciones, calificacion, fecha_entrega, nombre_archivo))
            conexion.commit()

            # 2️⃣ Obtener el id de la evidencia recién creada
            id_evidencia = cursor.lastrowid

            # 3️⃣ Obtener la ficha actual desde la sesión
            id_ficha = request.session.get("ficha_id")

            # Obtener todas las fichas que tienen la asignatura del formulario
            idasignatura = request.POST.get('idasignatura')
            cursor.execute("""
                SELECT fa.idficha 
                FROM ficha_asignatura fa
                WHERE fa.idasignatura = %s
            """, (idasignatura,))
            fichas = cursor.fetchall()

            # Registrar la evidencia en cada ficha
            for f in fichas:
                cursor.execute("""
                    INSERT INTO evidencias_ficha (idficha, idevidencias_instructor)
                    VALUES (%s, %s)
                """, (f[0], id_evidencia))
            conexion.commit()

            messages.success(request, "Evidencia agregada y vinculada a la ficha.")

        except mysql.connector.Error as err:
            messages.error(request, f"Error al agregar la evidencia: {err}")

        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()
        return redirect('evidencias_coordinador')
    return render(request, "paginas/coordinador/agregar_evidencia_coor.html")



def calificaciones(request):
    ficha_id = request.session.get("ficha_id")
    if not ficha_id:
        messages.error(request, "Por favor, selecciona una ficha primero.")
        return redirect('fichas_ins')

    try:
        # ================= FICHA =================
        ficha = Ficha.objects.select_related('idprograma').get(id=ficha_id)

        # ================= GUIAS (MISMAS QUE EN OTRAS PANTALLAS) =================
        guias_ficha = EvidenciasInstructor.objects.all().order_by('id')

        # ================= APRENDICES =================
        aprendices = Usuario.objects.filter(
            fichausuario__idficha_id=ficha_id,
            usuariorol__idrol__tipo='aprendiz'
        ).order_by('apellidos', 'nombres').distinct()

        # ================= CALIFICACIONES =================
        aprendices_calificaciones = []

        for aprendiz in aprendices:
            calificaciones_aprendiz = []

            for guia in guias_ficha:
                entrega = EvidenciasAprendiz.objects.filter(
                    idusuario=aprendiz,
                    idevidencias_instructor=guia
                ).first()

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

            aprendices_calificaciones.append({
                "aprendiz": aprendiz,
                "calificaciones": calificaciones_aprendiz
            })

        return render(request, "paginas/instructor/calificaciones.html", {
            "ficha": ficha,
            "guias_ficha": guias_ficha,
            "aprendices_calificaciones": aprendices_calificaciones
        })

    except Ficha.DoesNotExist:
        messages.error(request, "La ficha seleccionada no existe.")
        return redirect('fichas_ins')


def material_coordinador(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        archivo = request.FILES.get("archivo")

        nuevo = Material(
            titulo=titulo,
            descripcion=descripcion,
            archivo=archivo  # Django lo almacena automáticamente en media/material/
        )
        nuevo.save()

        messages.success(request, "Material creado correctamente.")
        return redirect("material_principal_coordinador")

    # Cargar lista de materiales para mostrarlos en la tabla
    materiales = Material.objects.all().order_by("-id")

    return render(request, "paginas/coordinador/material_coordinador.html", {
        "materiales": materiales
    })


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
    usuario_id = request.session.get("id_usuario")

    evidencias = EvidenciasInstructor.objects.all().order_by("id")

    evidencias_con_nota = []

    for evidencia in evidencias:
        entrega = EvidenciasAprendiz.objects.filter(
            idusuario_id=usuario_id,
            idevidencias_instructor=evidencia
        ).first()

        evidencias_con_nota.append({
            "id": evidencia.id,
            "titulo": evidencia.titulo,
            "calificacion": entrega.calificacion if entrega else None
        })

    return render(request, "paginas/aprendiz/calificacion.html", {
        "evidencias": evidencias_con_nota
    })

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
    evidencias = EvidenciasInstructor.objects.all()

    return render(request, "paginas/instructor/evidencias.html", {
        "evidencias": evidencias
    })

def material2(request):
    return render(request, "paginas/instructor/material2.html")

def tareas(request):
    return render(request, "paginas/aprendiz/tareas.html")

def tareas_2(request):
    return render(request, "paginas/aprendiz/tareas_2.html")

def lista_aprendices(request):
    # Si usas autenticación de Django y tu usuario coincide con el id de instructor:
    instructor_id = request.user.id if request.user.is_authenticated else 1

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)

    try:
        # Obtener la(s) ficha(s) del instructor
        cursor.execute("""
            SELECT idficha
            FROM ficha_usuario
            WHERE idusuario = %s
        """, (instructor_id,))
        filas = cursor.fetchall()  # leer todo para no dejar resultados sin procesar

        if not filas:
            aprendices = []
        else:
            # Si hay varias fichas, tomamos la primera; ajusta si necesitas otro comportamiento
            ficha_del_instructor = filas[0]["idficha"]

            # Consulta corregida: INNER JOIN y WHERE (no INNER_JOIN ni DONDE)
            cursor.execute("""
                SELECT u.id, u.nombres, u.apellidos
                FROM usuario u
                INNER JOIN ficha_usuario fu ON u.id = fu.idusuario
                INNER JOIN usuario_rol ur ON u.id = ur.idusuario
                WHERE fu.idficha = %s AND ur.idrol = 1
            """, (ficha_del_instructor,))
            aprendices = cursor.fetchall()

    finally:
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
    ficha_id = request.GET.get("ficha")

    if ficha_id:
        request.session["ficha_actual"] = ficha_id
    else:
        ficha_id = request.session.get("ficha_actual")
    return render(request, "paginas/instructor/carpetas2.html", {
        "ficha_id": ficha_id
    })

def portafolio(request, ficha_id):
    ficha = Ficha.objects.get(id=ficha_id)

    return render(request, "paginas/instructor/portafolio.html", {
        "ficha": ficha,
        "ficha_id": ficha_id  # <-- Esto es lo que faltaba
    })


def taller(request):
    return render(request, "paginas/instructor/taller.html")

import unicodedata


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



def carpetasins(request, ficha_id, trimestre):
    # 🔒 Verificar sesión
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect('sesion')

    # 🔒 Verificar rol instructor
    if not UsuarioRol.objects.filter(
        idusuario_id=usuario_id,
        idrol__tipo='instructor'
    ).exists():
        return redirect('inicio')

    ficha = get_object_or_404(Ficha, id=ficha_id)

    # 📁 Obtener carpetas asignadas a la ficha
    carpetas_ficha = FichaCarpetas.objects.filter(
        idficha=ficha
    ).select_related("idcarpetas")

    # Crear carpetas base si no existen
    if not carpetas_ficha.exists():
        nombres_base = [
            "1. Plan concertado de trabajo",
            "2. Guias de aprendizaje",
            "3. Evidencias de aprendizaje",
            "4. Planes de acción de mejora",
            "5. Formato diligenciado de planeación, seguimiento y evaluación"
        ]
        for nombre in nombres_base:
            try:
                # Modificación para usar números si tu DB tiene prefijos numericos
                carpeta_nombre_exacto = Carpetas.objects.get(nombre__iexact=nombre)
            except Carpetas.DoesNotExist:
                # Si no existe con el número, busca sin él para compatibilidad
                try:
                    carpeta_nombre_exacto = Carpetas.objects.get(nombre__iexact=nombre.split('. ')[-1])
                except Carpetas.DoesNotExist:
                    continue # Salta si la carpeta base no existe

            FichaCarpetas.objects.get_or_create(
                idficha=ficha,
                idcarpetas=carpeta_nombre_exacto
            )

        carpetas_ficha = FichaCarpetas.objects.filter(
            idficha=ficha
        ).select_related("idcarpetas")

    # 🔢 Ordenar carpetas por número
    def extraer_numero(texto):
        # Intenta extraer un número al inicio del texto
        match = re.search(r'^(\d+)\.', texto) 
        return int(match.group(1)) if match else 9999

    carpetas_ficha = sorted(
        carpetas_ficha,
        key=lambda c: extraer_numero(c.idcarpetas.nombre)
    )

    # 📎 Asignar archivos y evidencias
    for cf in carpetas_ficha:
        carpeta_obj = cf.idcarpetas


        # 🧠 EVIDENCIAS (viejas y nuevas)
        # Filtra las evidencias para que solo se muestren las que tienen el archivo subido
        cf.evidencias = EvidenciasInstructor.objects.filter(
            evidenciasficha__idficha=ficha,
            idinstructor_id=usuario_id,
        ).filter(
            archivo__isnull=False
        ).exclude(
            archivo=''
        ).order_by('-fecha_de_entrega')

    return render(request, "paginas/instructor/carpetasins.html", {
        "ficha": ficha,
        "trimestre": trimestre,
        "carpetas_ficha": carpetas_ficha
    })


# --- Vista para subir archivos (subir_archivo_portafolio) (SIN CAMBIOS) ---
def subir_archivo_portafolio(request):
    if request.method == "POST":
        
        # 🔑 CORRECCIÓN: OBTENER EL ID DEL INSTRUCTOR USANDO 'usuario_id'
        instructor_id = request.session.get("usuario_id")
        
        if instructor_id is None:
            # Si no hay ID de instructor, no puede guardar (IntegrityError)
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Obtener datos del formulario
        titulo = request.POST.get("titulo_archivo")
        archivo = request.FILES.get("archivo")
        ficha_id = request.POST.get("ficha")
        carpeta_id = request.POST.get("carpeta")
        trimestre = request.POST.get("trimestre")

        # Obtener objetos Foreign Key
        ficha = get_object_or_404(Ficha, id=ficha_id)
        carpeta = get_object_or_404(Carpetas, id=carpeta_id) 

        # Crear y guardar el nuevo registro en PortafolioInstructor
        nuevo = PortafolioInstructor(
            titulo_archivo=titulo,
            archivo=archivo,
            ficha=ficha,
            carpeta=carpeta,
            trimestre=trimestre,
            # ASIGNAR EL ID DEL INSTRUCTOR (ya obtenido de la sesión)
            idinstructor_id=instructor_id 
        )
        nuevo.save()

        # Redirigir a la misma página
        return redirect(request.META.get("HTTP_REFERER", "/"))

    return redirect("/")

# --- Vista para eliminar archivos (eliminar_archivo_portafolio) ---
def eliminar_archivo_portafolio(request, id):
    archivo = get_object_or_404(PortafolioInstructor, id=id)

    # 🔥 1. Eliminar archivo físico si existe
    if archivo.archivo and archivo.archivo.storage.exists(archivo.archivo.name):
        archivo.archivo.delete(save=False)

    # 🔥 2. Eliminar registro de la base de datos
    archivo.delete()

    return redirect(request.META.get("HTTP_REFERER", "/"))


# --- Vista para editar carpeta (editar_carpeta) (SIN CAMBIOS) ---
def editar_carpeta(request, id, ficha_id, trimestre):
    carpeta = get_object_or_404(Carpetas, id=id)

    if request.method == "POST":
        carpeta.nombre = request.POST.get("nombre")
        carpeta.descripcion = request.POST.get("descripcion")
        carpeta.save()

        return redirect('carpetasins', ficha_id=ficha_id, trimestre=trimestre)

    return render(request, 'paginas/instructor/editar_carpeta.html', {
        'carpeta': carpeta,
        'ficha_id': ficha_id,
        'trimestre': trimestre,
    })


def crear_carpeta(request, id, ficha_id, trimestre):


    if request.method == "POST":
        nombre = request.POST.get("nombre")
        # 🔑 CAMBIO: Obtener la descripción del formulario
        descripcion = request.POST.get("descripcion")

        if not nombre:
            messages.error(request, "El nombre de la carpeta es obligatorio.")
            return redirect("crear_carpeta", id=id, ficha_id=ficha_id, trimestre=trimestre)

        Carpetas.objects.create(
            nombre=nombre,
            descripcion=descripcion 
        )
        messages.success(request, "Carpeta creada exitosamente.")

        
        return redirect('carpetasins', ficha_id=ficha_id, trimestre=trimestre)

    return render(request, "paginas/instructor/crear_carpeta.html", {
        "ficha_id": ficha_id,
        "trimestre": trimestre
    })

def eliminar_carpeta(request, id, ficha_id, trimestre):
    carpeta = get_object_or_404(Carpetas, id=id)
    nombre_carpeta = carpeta.nombre


    try:
        carpeta.delete()
        messages.success(request, f"La carpeta '{nombre_carpeta}' y sus archivos asociados han sido eliminados correctamente.")
    except Exception as e:
        messages.error(request, f"Error al intentar eliminar la carpeta: {e}")

    return redirect('carpetasins', ficha_id=ficha_id, trimestre=trimestre)



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

def carpetas_aprendiz(request, aprendiz_id, trimestre):
    ficha_id = request.session.get("ficha_actual")
    if not ficha_id:
        return render(request, "error.html", {"mensaje": "No tienes ficha asignada."})
    
    ficha = get_object_or_404(Ficha, id=ficha_id)
    aprendiz = get_object_or_404(Usuario, id=aprendiz_id)
    
    # Obtener carpetas asignadas a la ficha
    carpetas_ficha = FichaCarpetas.objects.filter(idficha=ficha).select_related("idcarpetas").distinct()
    
    # Si no hay asignadas, asignar automáticamente las 5 carpetas base
    if not carpetas_ficha.exists():
        nombres_base = [
            "Plan concertado de trabajo",
            "Guias de aprendizaje",
            "Evidencias de aprendizaje",
            "Planes de acción de mejora",
            "Formato diligenciado de planeación, seguimiento y evaluación"
        ]
        for nombre in nombres_base:
            try:
                carpeta = Carpetas.objects.get(nombre=nombre)
                FichaCarpetas.objects.get_or_create(idficha=ficha, idcarpetas=carpeta)
            except Carpetas.DoesNotExist:
                pass  # No crear si no existe
        # Refetch
        carpetas_ficha = FichaCarpetas.objects.filter(idficha=ficha).select_related("idcarpetas")
    
    # Ordenar carpetas por número
    def extraer_numero(texto):
        match = re.search(r'(\d+)', texto)
        return int(match.group(1)) if match else 9999
    
    carpetas_ficha = sorted(carpetas_ficha, key=lambda c: extraer_numero(c.idcarpetas.nombre))
    
    # Asignar archivos del portafolio del aprendiz específico (usando PortafolioInstructor)
    for cf in carpetas_ficha:
        carpeta_obj = cf.idcarpetas

        # 📁 Archivos generales
        cf.archivos_generales = Archivos.objects.filter(
            idcarpetas=carpeta_obj
        ).order_by('-id')

        # 📂 Archivos del instructor (guías, planes, etc.)
        cf.archivos_instructor = PortafolioInstructor.objects.filter(
            ficha=ficha,
            trimestre=trimestre,
            carpeta=carpeta_obj,
            archivo__isnull=False
        ).exclude(
            archivo=''
        ).order_by('-fecha_subida')

        # 🔥 EVIDENCIAS REALES DEL APRENDIZ
        if carpeta_obj.nombre == "Evidencias de aprendizaje":
            cf.archivos_aprendiz = PortafolioAprendiz.objects.filter(
                idusuario=aprendiz,          # 👈 aprendiz que el instructor está viendo
                idevidencias_instructor__trimestre=trimestre,
                archivo__isnull=False
            ).exclude(
                archivo=''
            ).order_by('-fecha_entrega')
        else:
            cf.archivos_aprendiz = []

    
    return render(request, "paginas/instructor/carpetas_aprendiz.html", {
        "ficha": ficha,
        "trimestre": trimestre,
        "carpetas_ficha": carpetas_ficha,
        "aprendiz": aprendiz
    })

def trimestre_aprendiz(request, aprendiz_id):
    ficha_id = request.session.get("ficha_actual")
    ficha_actual = None
    trimestres = []
    aprendiz = get_object_or_404(Usuario, id=aprendiz_id)  # Obtener el aprendiz específico

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
        "trimestres": trimestres,
        "aprendiz": aprendiz  # Pasar el aprendiz al template
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
        ficha_usuario = FichaUsuario.objects.filter(idusuario_id=id_aprendiz).first()
        if ficha_usuario:
            ficha_id = ficha_usuario.idficha_id

            # Obtener asignaturas de la ficha
            asignaturas_qs = NombreAsignatura.objects.filter(
                fichaasignatura__idficha_id=ficha_id
            ).distinct()

            # Crear lista con instructor resuelto
            asignaturas = []
            for asig in asignaturas_qs:
                # Tomar la relación con esa ficha
                fa_rel = asig.fichaasignatura_set.filter(idficha_id=ficha_id).first()
                instructor = fa_rel.instructor if fa_rel and fa_rel.instructor else None
                asignaturas.append({
                    'id': asig.id,
                    'nombre': asig.nombre,
                    'instructor': instructor
                })

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

import re  # ⬅️ IMPORTANTE para extraer_numero

def carpetas_laura(request, trimestre):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect('sesion')

    if not UsuarioRol.objects.filter(
        idusuario_id=usuario_id,
        idrol__tipo='aprendiz'
    ).exists():
        return redirect('inicio')

    ficha_id = request.session.get("ficha_actual")
    asignatura_id = request.session.get("asignatura_actual")

    if not ficha_id or not asignatura_id:
        return render(request, "error.html", {
            "mensaje": "No hay ficha o asignatura activa."
        })

    ficha = get_object_or_404(Ficha, id=ficha_id)

    carpetas_ficha = FichaCarpetas.objects.filter(
        idficha=ficha
    ).select_related("idcarpetas")

    def extraer_numero(texto):
        match = re.search(r'(\d+)', texto)
        return int(match.group(1)) if match else 9999

    carpetas_ficha = sorted(
        carpetas_ficha,
        key=lambda c: extraer_numero(c.idcarpetas.nombre)
    )

    for cf in carpetas_ficha:
        carpeta_obj = cf.idcarpetas

        # 📁 Archivos generales
        cf.archivos_generales = Archivos.objects.filter(
            idcarpetas=carpeta_obj
        ).order_by('-id')

        # 📂 Archivos del instructor (GUÍAS DE APRENDIZAJE) - AJUSTADO PARA USAR TRIMESTRE DE LA FICHA
        cf.archivos_instructor = PortafolioInstructor.objects.filter(
            ficha=ficha,
            trimestre=ficha.trimestre_actual,  # 🔑 CAMBIO: Usa el trimestre actual de la ficha, no el de la URL
            carpeta=carpeta_obj,
            archivo__isnull=False
        ).exclude(
            archivo=''
        ).order_by('-fecha_subida')

        # 🔥 EVIDENCIAS DEL APRENDIZ (AQUÍ ESTABA EL ERROR)
        if carpeta_obj.nombre == "Evidencias de aprendizaje":
            cf.archivos_aprendiz = PortafolioAprendiz.objects.filter(
                idusuario_id=usuario_id,
                idasignatura_id=asignatura_id,
                idevidencias_instructor__trimestre=trimestre,  # Mantén el trimestre de la URL aquí, ya que es para evidencias
                archivo__isnull=False
            ).exclude(
                archivo=''
            ).order_by('-fecha_entrega')
        else:
            cf.archivos_aprendiz = []

    return render(request, "paginas/aprendiz/carpetas_laura.html", {
        "ficha": ficha,
        "trimestre": trimestre,
        "carpetas_ficha": carpetas_ficha
    })


def eliminar_archivo_portafolio(request, id):
    archivo = get_object_or_404(PortafolioInstructor, id=id)

    # 🔥 1. Eliminar archivo físico si existe
    if archivo.archivo and archivo.archivo.storage.exists(archivo.archivo.name):
        archivo.archivo.delete(save=False)

    # 🔥 2. Eliminar registro de la base de datos
    archivo.delete()

    return redirect(request.META.get("HTTP_REFERER", "/"))



def evidencia_laura(request, id):
    evidencias = EvidenciasInstructor.objects.all()

    return render(request, "paginas/aprendiz/evidencia_laura.html", {
        "evidencias": evidencias
    })

def evidencia_guialaura(request, id):
    # 🔒 Verificar sesión
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión.")
        return redirect("sesion")

    aprendiz = get_object_or_404(Usuario, id=usuario_id)

    # 🔥 ASIGNATURA ACTUAL (OBLIGATORIA)
    asignatura_id = request.session.get("asignatura_actual")
    if not asignatura_id:
        messages.error(request, "No hay asignatura seleccionada.")
        return redirect("inicio")

    asignatura = get_object_or_404(NombreAsignatura, id=asignatura_id)

    # Evidencia del instructor
    evidencia_inst = get_object_or_404(EvidenciasInstructor, id=id)

    # Ver si ya existe entrega
    entrega = PortafolioAprendiz.objects.filter(
        idusuario=aprendiz,
        idevidencias_instructor=evidencia_inst,
        idasignatura=asignatura
    ).first()

    if request.method == "POST":
        archivo = request.FILES.get("archivo")
        observaciones = request.POST.get("observaciones")

        if entrega:
            # 🔁 Actualizar
            if archivo:
                entrega.archivo = archivo
            entrega.observaciones = observaciones
            entrega.fecha_entrega = timezone.now()
            entrega.save()
        else:
            # 🆕 Crear
            PortafolioAprendiz.objects.create(
                idusuario=aprendiz,
                idevidencias_instructor=evidencia_inst,
                idasignatura=asignatura,
                archivo=archivo,
                observaciones=observaciones,
                fecha_entrega=timezone.now()
            )

        messages.success(request, "Evidencia enviada correctamente.")
        return redirect("evidencia_guialaura", id=id)

    return render(request, "paginas/aprendiz/evidencia_guialaura.html", {
        "evidencia": evidencia_inst,
        "entrega": entrega,
        "aprendiz": aprendiz,
    })



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

    id_ficha = 1  # ficha actual

    # Usuarios asignados a esta ficha
    relaciones = FichaUsuario.objects.filter(idficha=id_ficha).values_list('idusuario', flat=True)

    # Filtrar SOLO aprendices (idrol = 1) en esta ficha
    aprendices = Usuario.objects.filter(
        id__in=relaciones,
        usuariorol__idrol=1       # <-- nombre correcto del campo
    ).distinct()

    context = {
        "aprendices": aprendices,
        "total": aprendices.count()
    }

    return render(request, "paginas/observador/lista_aprendices_observador.html", context)

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


def adentro_material_observador(request, id):
    material = Material.objects.get(id=id)
    return render(request, "paginas/observador/adentro_material_observador.html", {
        "material": material
    })


def material_principal_observador(request):
    materiales = Material.objects.all().order_by('-id')
    return render(request, "paginas/observador/material_principal_observador.html", {
        "materiales": materiales
    })

def evidencia_guia_observador(request, evidencia_id):
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

    # Obtener la ficha activa desde la sesión
    ficha_id = request.session.get("ficha_id")

    return render(request, "paginas/observador/evidencia_guia_observador.html", {
        "evidencia": evidencia,
        "ficha_id": ficha_id       # <-- SE AGREGA ESTO
    })


def evidencias_observador(request, ficha_id):
    # Guardar la ficha en la sesión para usarla después
    request.session["ficha_id"] = ficha_id

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)

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

    return render(request, "paginas/observador/evidencias_observador.html", {"evidencias": evidencias})


def adentro_material_coordinador(request, id):
    material = Material.objects.get(id=id)
    return render(
        request,
        "paginas/coordinador/adentro_material_coordinador.html",
        {"material": material}
    )

def carpetas_coordinador(request):
    return render(request, "paginas/coordinador/carpetas_coordinador.html")


def evidencia_guia_coordinador(request, evidencia_id):
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

    # Obtener la ficha activa desde la sesión
    ficha_id = request.session.get("ficha_id")

    return render(request, "paginas/coordinador/evidencia_guia_coordinador.html", {
        "evidencia": evidencia,
        "ficha_id": ficha_id       # <-- SE AGREGA ESTO
    })



def evidencias_coordinador(request, ficha_id):
    # Guardar la ficha en la sesión para usarla después
    request.session["ficha_id"] = ficha_id

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conexion.cursor(dictionary=True)

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

    return render(request, "paginas/coordinador/evidencias_coordinador.html", {"evidencias": evidencias})


def inicio_coordinador(request):
    ficha_id = request.session.get('ficha_actual')  # ← ahora sí coincide
    return render(request, "paginas/coordinador/inicio_coordinador.html", {"ficha_id": ficha_id})


def lista_aprendices_coordinador(request):

    # Aquí deberías obtener el id de la ficha seleccionada por el coordinador
    idficha = 1  # <-- cámbialo luego por dinámico

    # Capturar el texto buscado (si existe)
    q = request.GET.get("q", "").strip()

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    
    cursor = conexion.cursor(dictionary=True)

    try:
        if q:  
            # FILTRAR POR BUSQUEDA (nombre o apellido)
            cursor.execute("""
                SELECT u.id, u.nombres, u.apellidos
                FROM usuario u
                INNER JOIN ficha_usuario fu ON fu.idusuario = u.id
                INNER JOIN usuario_rol ur ON ur.idusuario = u.id
                WHERE fu.idficha = %s
                AND ur.idrol = 1
                AND (u.nombres LIKE %s OR u.apellidos LIKE %s)
            """, (idficha, f"%{q}%", f"%{q}%"))
        else:
            # MOSTRAR TODOS SIN FILTRO
            cursor.execute("""
                SELECT u.id, u.nombres, u.apellidos
                FROM usuario u
                INNER JOIN ficha_usuario fu ON fu.idusuario = u.id
                INNER JOIN usuario_rol ur ON ur.idusuario = u.id
                WHERE fu.idficha = %s AND ur.idrol = 1
            """, (idficha,))

        aprendices = cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()

    total = len(aprendices)  # TOTAL FILTRADO

    return render(request, "paginas/coordinador/lista_aprendices_coordinador.html", {
        "aprendices": aprendices,
        "total": total,
        "q": q,
    })

def material_principal_coordinador(request):
    materiales = Material.objects.all().order_by('-id')
    return render(request, "paginas/coordinador/material_principal_coordinador.html", {
        "materiales": materiales
    })


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
    ficha_id = request.session.get("ficha_actual")
    if not ficha_id:
        messages.error(request, "Por favor, selecciona una ficha primero.")
        return redirect('fichas_coordinador')

    try:
        # ✔ Obtener ficha
        ficha = Ficha.objects.select_related('idprograma').get(id=ficha_id)

        # ✔ Obtener guías vinculadas a la ficha
        guias_ficha = EvidenciasInstructor.objects.filter(
            evidenciasficha__idficha=ficha_id
        ).order_by('id').distinct()

        # ✔ Obtener aprendices de la ficha
        aprendices = Usuario.objects.filter(
            fichausuario__idficha_id=ficha_id,
            usuariorol__idrol__tipo='aprendiz'
        ).order_by('apellidos', 'nombres').distinct()

        aprendices_calificaciones = []

        for aprendiz in aprendices:
            calificaciones_aprendiz = []

            for guia in guias_ficha:
                # ✔ Buscar entrega del aprendiz
                entrega = EvidenciasAprendiz.objects.filter(
                    idusuario=aprendiz,
                    idevidencias_instructor=guia
                ).first()

                if entrega and entrega.calificacion:
                    calificaciones_aprendiz.append({
                        "texto": entrega.calificacion,
                        "clase_css": "text-success",
                        "url": "#"  # Cambia luego si necesitas enlace
                    })
                else:
                    calificaciones_aprendiz.append({
                        "texto": "Sin calificar",
                        "clase_css": "text-warning",
                        "url": "#"
                    })

            aprendices_calificaciones.append({
                "aprendiz": aprendiz,
                "calificaciones": calificaciones_aprendiz
            })

        # ✔ Render
        return render(request, "paginas/coordinador/calificaciones_coordinador.html", {
            "ficha": ficha,
            "guias_ficha": guias_ficha,
            "aprendices_calificaciones": aprendices_calificaciones
        })

    except Ficha.DoesNotExist:
        messages.error(request, "La ficha seleccionada no existe.")
        return redirect('fichas_coordinador')


def evidencia_calificar_coordinador(request):
    return render(request, "paginas/coordinador/evidencia_calificar_coordinador.html")



def sesion(request):
    # Limpiar SOLO mensajes viejos ANTES de mostrar el login
    if request.method == "GET":
        storage = messages.get_messages(request)
        storage.used = True  # Esto sí borra los mensajes que quedaron por error

    usuario_ingresado = ""

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
            messages.error(request, "El usuario no existe", extra_tags="login")
            return redirect('sesion')

        if contrasena_input != usuario['contrasena']:
            messages.error(request, "Contraseña incorrecta", extra_tags="login")
            return redirect('sesion')

        # Guardar en sesión
        request.session['usuario_id'] = usuario['id']
        request.session['usuario'] = usuario['usuario']
        request.session['nombre_usuario'] = f"{usuario['nombres']} {usuario['apellidos']}".upper()

        cursor.execute("""
            SELECT r.tipo
            FROM rol r
            INNER JOIN usuario_rol ur ON ur.idrol = r.id
            WHERE ur.idusuario = %s
        """, (usuario['id'],))
        rol = cursor.fetchone()

        cursor.execute("""
            SELECT idficha 
            FROM ficha_usuario
            WHERE idusuario = %s
        """, (usuario['id'],))

        ficha = cursor.fetchone()
        request.session['ficha_id'] = ficha['idficha'] if ficha else None

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
                messages.error(request, f"Rol desconocido: {tipo_rol}", extra_tags="login")
                return redirect('sesion')

        messages.error(request, "No se encontró un rol asignado para este usuario.", extra_tags="login")
        return redirect('sesion')

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

from datetime import date

def obtener_max_trimestres(ficha):
    """
    Devuelve el máximo de trimestres basado en el tipo de programa de la ficha.
    """
    if not ficha or not ficha.idprograma:
        return 3  # Default si no hay programa
    tipo_programa = ficha.idprograma.programa.lower()
    
    if "tecnico" in tipo_programa:
        return 3
    elif "tecnologo" in tipo_programa:
        return 6
    elif "articulacion" in tipo_programa:
        return 5
    elif "cadena" in tipo_programa or "cadena de formacion" in tipo_programa:
        return 6
    elif "adso" in tipo_programa:
        return 7
    elif "mixta" in tipo_programa:
        return 7
    else:
        return 3  # Default

def calcular_trimestre_sugerido(fecha_inicio, max_trimestres):
    """
    Calcula el trimestre sugerido basado en el tiempo transcurrido desde fecha_inicio.
    Cada 3 meses (aprox. 90 días) avanza un trimestre, máximo según el programa.
    """
    if not fecha_inicio:
        return 1
    dias_transcurridos = (date.today() - fecha_inicio).days
    meses_transcurridos = dias_transcurridos // 30  # Aproximación simple de meses
    trimestre = (meses_transcurridos // 3) + 1
    return min(trimestre, max_trimestres)  # Máximo según el programa

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
        usuariorol__idrol__tipo="instructor"
    ).distinct()

    instructores_asignados = Usuario.objects.filter(
        fichausuario__idficha_id=ficha_id,
        usuariorol__idrol__tipo="instructor"
    ).distinct()

    ids_instructores_asignados = [i.id for i in instructores_asignados]

    # ========= APRENDICES =========
    aprendices = Usuario.objects.filter(
        usuariorol__idrol__tipo="aprendiz"
    ).distinct()

    aprendices_asignados = Usuario.objects.filter(
        fichausuario__idficha_id=ficha_id,
        usuariorol__idrol__tipo="aprendiz"
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

    # NUEVO: Obtener máximo de trimestres y calcular sugerido
    max_trimestres = obtener_max_trimestres(ficha)
    trimestre_sugerido = calcular_trimestre_sugerido(ficha.fecha_inicio, max_trimestres)
    
    # Generar lista de trimestres disponibles (1 a max_trimestres)
    trimestres_disponibles = list(range(1, max_trimestres + 1))

    # ========= GUARDAR =========
    if request.method == "POST":

        # ---------- Guardar Instructores ----------
        if "instructores" in request.POST:
            seleccionados = request.POST.getlist("instructores")

            FichaUsuario.objects.filter(
                idficha_id=ficha_id,
                idusuario__usuariorol__idrol__tipo="instructor"
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
                idusuario__usuariorol__idrol__tipo="aprendiz"
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

        # NUEVO: Manejar cambio de trimestre (con validación de máximo)
        if request.POST.get("accion") == "cambiar_trimestre":
            nuevo_trimestre = int(request.POST.get("nuevo_trimestre", 1))
            if 1 <= nuevo_trimestre <= max_trimestres:
                ficha.trimestre_actual = nuevo_trimestre
                ficha.save()
                messages.success(request, f"Trimestre actualizado a {nuevo_trimestre}.")
            else:
                messages.error(request, f"Trimestre inválido. Máximo permitido: {max_trimestres}.")
            return redirect("configuracion_coordinador")

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

        # NUEVO: Trimestre sugerido y lista dinámica
        "trimestre_sugerido": trimestre_sugerido,
        "trimestres_disponibles": trimestres_disponibles,
        "max_trimestres": max_trimestres,
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

    contexto = {
        "ficha": None,
        "aprendices_count": 0,
        "instructor_responsable": "No asignado"
    }

    if usuario_id:
        try:
            # 1. Buscar la relación entre el aprendiz y la ficha
            relacion = FichaUsuario.objects.select_related('idficha').get(idusuario_id=usuario_id)
            ficha = relacion.idficha

            # 2. Contar aprendices en la ficha
            aprendices_count = Usuario.objects.filter(
                fichausuario__idficha=ficha,
                usuariorol__idrol__tipo='aprendiz'
            ).count()

            # 3. Encontrar un instructor para la ficha
            instructor = Usuario.objects.filter(
                fichausuario__idficha=ficha,
                usuariorol__idrol__tipo='instructor'
            ).first()

            contexto['ficha'] = ficha
            contexto['aprendices_count'] = aprendices_count
            if instructor:
                contexto['instructor_responsable'] = f"{instructor.nombres} {instructor.apellidos}"

        except FichaUsuario.DoesNotExist:
            messages.error(request, "No estás asignado a ninguna ficha.")

    return render(request, "paginas/aprendiz/ficha_aprendiz.html", contexto)

def ficha_aprendiz_2(request):
    usuario_id = request.session.get("id_usuario")

    contexto = {
        "ficha": None,
        "aprendices_count": 0,
        "instructor_responsable": "No asignado"
    }

    if usuario_id:
        try:
            # 1. Buscar la relación entre el aprendiz y la ficha
            relacion = FichaUsuario.objects.select_related('idficha').get(idusuario_id=usuario_id)
            ficha = relacion.idficha

            # 2. Contar aprendices en la ficha
            aprendices_count = Usuario.objects.filter(
                fichausuario__idficha=ficha,
                usuariorol__idrol__tipo='aprendiz'
            ).count()

            # 3. Encontrar un instructor para la ficha
            instructor = Usuario.objects.filter(
                fichausuario__idficha=ficha,
                usuariorol__idrol__tipo='instructor'
            ).first()

            contexto['ficha'] = ficha
            contexto['aprendices_count'] = aprendices_count
            if instructor:
                contexto['instructor_responsable'] = f"{instructor.nombres} {instructor.apellidos}"

        except FichaUsuario.DoesNotExist:
            messages.error(request, "No estás asignado a ninguna ficha.")

    return render(request, "paginas/aprendiz/ficha_aprendiz_2.html", contexto)

def ficha_instructor(request):
    ficha_id = request.session.get('ficha_actual')

    if not ficha_id:
        messages.error(request, "No se ha seleccionado ninguna ficha. Por favor, vuelve a la lista de fichas.")
        return redirect('fichas_ins')

    try:
        ficha = Ficha.objects.select_related('idjornada', 'idprograma').get(id=ficha_id)

        aprendices = Usuario.objects.filter(
            fichausuario__idficha=ficha,
            usuariorol__idrol__tipo='aprendiz'
        ).order_by('apellidos', 'nombres').distinct()

    except Ficha.DoesNotExist:
        messages.error(request, "La ficha seleccionada no existe o fue eliminada.")
        return redirect('fichas_ins')

    # Obtener el nombre del instructor desde la sesión para mostrarlo en la plantilla
    usuario_nombre = request.session.get('nombre_usuario', 'No identificado')

    return render(request, "paginas/instructor/ficha_instructor.html", {
        'ficha': ficha, 
        'aprendices': aprendices,
        'usuario_nombre': usuario_nombre
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

def opc_equipoejecutor(request, trimestre):
    ficha_id = request.session.get("ficha_actual")
    ficha = get_object_or_404(Ficha, id=ficha_id)

    carpetas = CarpetaEquipo.objects.filter(
        ficha=ficha,
        trimestre=trimestre,
        parent__isnull=True   # SOLO CARPETAS PRINCIPALES
    ).order_by("nombre")

    return render(request, "paginas/instructor/opc_equipoejecutor.html", {
        "ficha": ficha,
        "trimestre": trimestre,
        "carpetas": carpetas
    })


def crear_carpeta_equipo(request, trimestre):
    ficha_id = request.session.get("ficha_actual")
    ficha = get_object_or_404(Ficha, id=ficha_id)

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")

        CarpetaEquipo.objects.create(
            ficha=ficha,
            trimestre=trimestre,
            nombre=nombre,
            descripcion=descripcion
        )

        messages.success(request, "Carpeta creada correctamente.")
        return redirect("opc_equipoejecutor", trimestre=trimestre)

    return render(request, "paginas/instructor/crear_carpeta_equipo.html", {
        "trimestre": trimestre
    })

def crear_subcarpeta_equipo(request, carpeta_id):
    parent_carpeta = get_object_or_404(CarpetaEquipo, id=carpeta_id)
    ficha = parent_carpeta.ficha
    trimestre = parent_carpeta.trimestre

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")

        CarpetaEquipo.objects.create(
            ficha=ficha,
            trimestre=trimestre,
            nombre=nombre,
            descripcion=descripcion,
            parent=parent_carpeta   
        )

        messages.success(request, "Subcarpeta creada correctamente.")
        return redirect("opc_equipoejecutor", trimestre=trimestre)

    return render(request, "paginas/instructor/crear_subcarpeta_equipo.html", {
        "carpeta": parent_carpeta,
        "trimestre": trimestre
    })


def editar_carpeta_equipo(request, carpeta_id):
    carpeta = get_object_or_404(CarpetaEquipo, id=carpeta_id)

    if request.method == "POST":
        carpeta.nombre = request.POST.get("nombre")
        carpeta.descripcion = request.POST.get("descripcion")
        carpeta.save()

        return redirect("opc_equipoejecutor", trimestre=carpeta.trimestre)

    return render(request, "paginas/instructor/editar_carpeta_equipo.html", {
        "carpeta": carpeta
    })

def eliminar_carpeta_equipo(request, carpeta_id):
    carpeta = get_object_or_404(CarpetaEquipo, id=carpeta_id)
    trimestre = carpeta.trimestre
    carpeta.delete()

    return redirect("opc_equipoejecutor", trimestre=trimestre)

def subir_archivo_equipo(request, carpeta_id):
    carpeta = get_object_or_404(CarpetaEquipo, id=carpeta_id)

    if request.method == "POST":

        archivo = request.FILES.get("archivo")
        nombre_editable = request.POST.get("nombre_editable")

        if archivo is None:
            messages.error(request, "Debes seleccionar un archivo.")
            return redirect("opc_equipoejecutor", trimestre=carpeta.trimestre)

        ArchivoEquipo.objects.create(
            carpeta=carpeta,
            archivo=archivo,
            nombre_editable=nombre_editable
        )

        messages.success(request, "Archivo subido correctamente.")
        return redirect("opc_equipoejecutor", trimestre=carpeta.trimestre)


def eliminar_archivo_equipo(request, archivo_id):
    # usar el mismo nombre que en la URL: archivo_id
    archivo = get_object_or_404(ArchivoEquipo, id=archivo_id)

    # 1) eliminar fichero físico si existe
    try:
        if archivo.archivo and archivo.archivo.name:
            # exist check (seguro para cualquier storage)
            storage = archivo.archivo.storage
            if storage.exists(archivo.archivo.name):
                archivo.archivo.delete(save=False)
    except Exception as e:
        # opcional: loguear el error, pero no impedir la eliminación del registro
        # import logging; logging.exception(e)
        pass

    # 2) eliminar registro de la BD
    carpeta = archivo.carpeta  # lo guardamos para la redirección
    archivo.delete()

    messages.success(request, "Archivo eliminado correctamente.")
    return redirect("opc_equipoejecutor", trimestre=carpeta.trimestre)



def fichas_equipoejecutor_coordinador(request):
    return render(request, "paginas/coordinador/fichas_equipoejecutor_coordinador.html")

def equipo_coordinador(request):
    return render(request, "paginas/coordinador/equipo_coordinador.html")

def material_editar(request, id):
    material = get_object_or_404(Material, id=id)

    if request.method == "POST":
        # --- Lógica para eliminar el archivo adjunto ---
        if "eliminar_archivo" in request.POST:
            if material.archivo:
                material.archivo.delete() # Borra el archivo del sistema y del modelo
            messages.success(request, "Archivo adjunto eliminado.")
            return redirect("material_editar", id=id)

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

def material_editar_observador(request, id):
    material = get_object_or_404(Material, id=id)

    if request.method == "POST":
        material.titulo = request.POST.get("titulo")
        material.descripcion = request.POST.get("descripcion")
        archivo = request.FILES.get("archivo")
        if archivo:
            material.archivo = archivo
        material.save()
        messages.success(request, "Material actualizado correctamente.")
        return redirect("adentro_material_observador", id=id)

    return render(request, "paginas/observador/material_editar_observador.html", {
        "material": material
    })

def material_editar_coordinador(request, id):
    material = get_object_or_404(Material, id=id)

    if request.method == "POST":
        if "eliminar_archivo" in request.POST:
            if material.archivo:
                material.archivo.delete()
            messages.success(request, "Archivo adjunto eliminado.")
            return redirect("material_editar_coordinador", id=id)

        material.titulo = request.POST.get("titulo")
        material.descripcion = request.POST.get("descripcion")
        material.fecha_entrega = request.POST.get("fecha_entrega")

        archivo = request.FILES.get("archivo")
        if archivo:
            material.archivo = archivo

        material.save()

        return redirect("material_principal_coordinador")

    return render(request, "paginas/coordinador/material_editar_coordinador.html", {
        "material": material
    })


def material_eliminar_observador(request, id):
    material = get_object_or_404(Material, id=id)
    if request.method == "POST":
        material.delete()
        messages.success(request, "Material eliminado correctamente.")
        return redirect("material_principal_observador")
    return render(request, "paginas/observador/material_eliminar_confirmar.html", {
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

def evidencia_guia_editar_coordinador(request, evidencia_id):

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
        return redirect("evidencia_guia_coordinador", evidencia_id)

    cursor.close()
    conexion.close()

    return render(request, "paginas/coordinador/evidencia_guia_editar_coordinador.html", {
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
        numero = request.POST.get("numero_ficha", "").strip()
        aprendices = request.POST.get("numero_aprendices", "").strip()
        estado = request.POST.get("estado", "").strip()

        jornada = request.POST.get("idjornada")
        programa = request.POST.get("idprograma")
        nombre_programa = request.POST.get("nombre_programa")

        # VALIDACIÓN PRINCIPAL
        if not numero or not numero.isdigit():
            messages.error(request, "❗ Debes ingresar un número de ficha válido.")
            return redirect("coordinador_agregar")

        # Si todo bien, guardar
        Ficha.objects.create(
            numero_ficha=int(numero),
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

def administrar_usuario_masivo(request):
    if request.method == "POST":
        archivo = request.FILES.get("archivo")
        import pandas as pd
        
        # Leer Excel o CSV
        df = pd.read_excel(archivo) if archivo.name.endswith(".xlsx") else pd.read_csv(archivo)

        # Normalizar columnas → elimina espacios y pone todo en minúscula
        df.columns = df.columns.str.strip().str.lower()

        print("COLUMNAS NORMALIZADAS:", df.columns)  # debug

        # Validar columnas necesarias
        columnas_obligatorias = [
            "nombres", "apellidos", "correo", "telefono",
            "tipo doc", "documento", "usuario", "contraseña", "rol"
        ]

        for col in columnas_obligatorias:
            if col not in df.columns:
                raise ValueError(f"La columna requerida '{col}' NO existe en el archivo Excel.")

        # Procesar fila por fila
        for _, row in df.iterrows():

            # --- Crear o buscar documento ---
            documento_obj, _ = Documento.objects.get_or_create(
                tipo=row["tipo doc"].strip(),
                numero=str(row["documento"]).strip()
            )

            # --- Crear usuario ---
            usuario = Usuario.objects.create(
                nombres=row["nombres"].strip(),
                apellidos=row["apellidos"].strip(),
                correo=row["correo"].strip(),
                telefono=str(row["telefono"]).strip(),
                usuario=row["usuario"].strip(),
                contrasena=row["contraseña"],   # sin .strip por si usa números o caracteres especiales
                iddocumento=documento_obj
            )

            # --- Validación de rol ---
            rol_texto = row["rol"].strip().lower()

            if rol_texto not in ["aprendiz", "instructor", "coordinador", "observador"]:
                raise ValueError(f"El rol '{rol_texto}' no es válido.")

            rol_obj = Rol.objects.get(tipo=rol_texto)

            # Asignar rol
            UsuarioRol.objects.create(
                idusuario=usuario,
                idrol=rol_obj
            )

        messages.success(request, "Usuarios cargados exitosamente.")
        return redirect("administrar_usuario")

    return render(request, "paginas/coordinador/administrar_usuario_masivo.html")





def descargar_plantilla_usuarios(request):
    # Ruta única, siempre válida en desarrollo
    ruta_archivo = os.path.join(
        settings.BASE_DIR,
        "static",
        "plantillas",
        "plantilla_usuarios.xlsx"
    )

    # Verifica que exista
    if not os.path.exists(ruta_archivo):
        raise Http404("La plantilla no existe en: " + ruta_archivo)

    # Devolver archivo
    return FileResponse(
        open(ruta_archivo, "rb"),
        as_attachment=True,
        filename="plantilla_usuarios.xlsx"
    )

def gestionar_tipos_documento(request):
    tipos = Documento.objects.all()

    if request.method == "POST":
        sigla = request.POST.get("sigla")
        nombre = request.POST.get("tipo")

        if sigla.strip() and nombre.strip():
            Documento.objects.create(
                sigla=sigla.strip(), 
                tipo=nombre.strip()
            )
            messages.success(request, "Tipo de documento agregado.")
            return redirect("gestionar_tipos_documento")

    return render(request, "paginas/coordinador/gestionar_tipos_documento.html", {
        "tipos": tipos
    })




def editar_tipo_documento(request, id):
    tipo = get_object_or_404(Documento, id=id)

    if request.method == "POST":
        nueva_sigla = request.POST.get("sigla")
        nuevo_nombre = request.POST.get("tipo")

        if nueva_sigla.strip() and nuevo_nombre.strip():
            tipo.sigla = nueva_sigla.strip()      # SE ACTUALIZA LA SIGLA ✔
            tipo.tipo = nuevo_nombre.strip()      # SE ACTUALIZA EL NOMBRE ✔
            tipo.save()
            messages.success(request, "Tipo de documento actualizado.")
            return redirect("gestionar_tipos_documento")

    return render(request, "paginas/coordinador/tipos_documento_editar.html", {
        "tipo": tipo
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
        # Buscar el tipo_documento correspondiente (el Documento con el mismo tipo y sigla, sin numero)
        tipo_doc = Documento.objects.filter(
            tipo=usuario.iddocumento.tipo,
            sigla=usuario.iddocumento.sigla,
            numero__isnull=True
        ).first() if usuario.iddocumento else None

        initial = {
            "tipo_documento": tipo_doc,
            "numero_documento": usuario.iddocumento.numero if usuario.iddocumento else "",
            "rol": usuario.usuariorol_set.first().idrol if usuario.usuariorol_set.exists() else None,
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

        id_usuario = request.session.get("usuario_id")

        if not id_usuario:
            messages.error(request, "No se encontró el usuario en la sesión.")
            return redirect("configuracion_instructor")

        try:
            conexion = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            cursor = conexion.cursor(dictionary=True)

            cursor.execute("SELECT contrasena FROM usuario WHERE id = %s", (id_usuario,))
            usuario = cursor.fetchone()

            if not usuario:
                messages.error(request, "Usuario no encontrado.")
                return redirect("configuracion_instructor")

            if usuario["contrasena"] != contrasena_actual:
                messages.error(request, "La contraseña actual es incorrecta.")
                return redirect("configuracion_instructor")

            if nueva != confirmar:
                messages.error(request, "Las contraseñas nuevas no coinciden.")
                return redirect("configuracion_instructor")

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

    # Asignaciones actuales
    asignaturas_ficha = FichaAsignatura.objects.filter(
        idficha=ficha
    ).select_related('idasignatura')

    asignadas_ids = list(
        asignaturas_ficha.values_list("idasignatura_id", flat=True)
    )

    instructores = Usuario.objects.filter(rol__iexact="instructor")

    if request.method == "POST":
        seleccionadas = request.POST.getlist("asignaturas")
        seleccionadas = [int(x) for x in seleccionadas]

        # Eliminar asignaturas que se quitaron
        FichaAsignatura.objects.filter(idficha=ficha)\
            .exclude(idasignatura_id__in=seleccionadas)\
            .delete()

        # Procesar asignaturas marcadas
        for asig_id in seleccionadas:

            # Crear la relación ficha-asignatura si no existe
            FichaAsignatura.objects.get_or_create(
                idficha=ficha,
                idasignatura_id=asig_id
            )

            # Obtener el instructor asignado a esta asignatura
            instructor_id = request.POST.get(f"instructor_{asig_id}")

            if instructor_id:
                # Guardar instructor en la tabla NombreAsignatura
                NombreAsignatura.objects.filter(id=asig_id).update(
                    instructor_id=int(instructor_id)
                )

        messages.success(request, "Asignaturas e instructores actualizados correctamente.")
        return redirect("configuracion_asignaturas")

    return render(request, "paginas/coordinador/configuracion_asignaturas.html", {
        "ficha": ficha,
        "todas_asignaturas": todas_asignaturas,
        "asignadas_ids": asignadas_ids,
        "asignaturas_ficha": asignaturas_ficha,
        "ficha_id": ficha_id,
        "instructores": instructores,
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

def asignar_instructor_asignatura(request):
    if request.method == "POST":
        ficha_id = request.POST.get('ficha_id')
        asignatura_id = request.POST.get('asignatura_id')
        instructor_id = request.POST.get('instructor_id')

        # Obtener la relación FichaAsignatura
        fa = get_object_or_404(FichaAsignatura, idficha_id=ficha_id, idasignatura_id=asignatura_id)
        fa.instructor_id = instructor_id
        fa.save()

    return redirect('configuracion_coordinador')

def eliminar_evidencia(request, evidencia_id):

    # 1. Buscar evidencia
    evidencia = get_object_or_404(EvidenciasInstructor, id=evidencia_id)

    # Nombre del archivo (string correcto)
    nombre_archivo = evidencia.archivo.name if evidencia.archivo else None

    # 2. Borrar archivo del instructor en media/evidencias/
    if nombre_archivo:
        ruta_archivo = os.path.join(settings.MEDIA_ROOT, "evidencias", os.path.basename(nombre_archivo))

        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)

    # 3. Buscar relaciones en evidencias_ficha
    relaciones = EvidenciasFicha.objects.filter(idevidencias_instructor=evidencia)

    for rel in relaciones:
        id_ficha = rel.idficha_id

        # Obtener aprendices
        from pantallas.models import FichaUsuario
        aprendices = FichaUsuario.objects.filter(idficha=id_ficha)

        for apr in aprendices:
            carpeta_aprendiz = os.path.join(settings.MEDIA_ROOT, "evidencias_aprendiz", str(apr.idusuario_id))
            ruta_copia = os.path.join(carpeta_aprendiz, os.path.basename(nombre_archivo))

            if os.path.exists(ruta_copia):
                os.remove(ruta_copia)

    # 4. Borrar relaciones
    relaciones.delete()

    # 5. Borrar evidencia
    evidencia.delete()

    messages.success(request, "La evidencia y sus archivos fueron eliminados correctamente.")
    return redirect("evidencias")


def eliminar_evidencia_coordinador(request, evidencia_id):

    evidencia = get_object_or_404(EvidenciasInstructor, id=evidencia_id)

    # Nombre del archivo
    nombre_archivo = evidencia.archivo.name if evidencia.archivo else None

    # 1. Eliminar archivo principal
    if nombre_archivo:
        ruta_archivo = os.path.join(settings.MEDIA_ROOT, "evidencias", os.path.basename(nombre_archivo))

        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)

    # 2. Buscar relaciones con fichas
    relaciones = EvidenciasFicha.objects.filter(idevidencias_instructor=evidencia)

    for rel in relaciones:
        id_ficha = rel.idficha_id

        # Copias en aprendices del coordinador
        from pantallas.models import FichaUsuario
        aprendices = FichaUsuario.objects.filter(idficha=id_ficha)

        for apr in aprendices:
            carpeta_aprendiz = os.path.join(settings.MEDIA_ROOT, "evidencias_aprendiz", str(apr.idusuario_id))
            ruta_copia = os.path.join(carpeta_aprendiz, os.path.basename(nombre_archivo))

            if os.path.exists(ruta_copia):
                os.remove(ruta_copia)

    # 3. eliminar relaciones
    relaciones.delete()

    # 4. eliminar evidencia
    evidencia.delete()

    messages.success(request, "La evidencia del coordinador fue eliminada correctamente.")

    # ⚠️ ESTA REDIRECCIÓN ES IMPORTANTE
    return redirect("evidencias_coordinador", ficha_id=id_ficha)


def eliminar_material(request, material_id):

    # 1. Buscar el material
    material = get_object_or_404(Material, id=material_id)

    # Nombre del archivo (string correcto)
    nombre_archivo = material.archivo.name if material.archivo else None

    # 2. Borrar archivo dentro de media/material/
    if nombre_archivo:
        ruta_archivo = os.path.join(
            settings.MEDIA_ROOT,
            "material",
            os.path.basename(nombre_archivo)
        )

        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)

    # 3. Borrar el registro del material
    material.delete()

    messages.success(request, "El material y su archivo fueron eliminados correctamente.")
    return redirect("material_principal")

def eliminar_material_coordinador(request, material_id):

    # 1. Buscar el material
    material = get_object_or_404(Material, id=material_id)

    # Nombre del archivo (string correcto)
    nombre_archivo = material.archivo.name if material.archivo else None

    # 2. Borrar archivo dentro de media/material/
    if nombre_archivo:
        ruta_archivo = os.path.join(
            settings.MEDIA_ROOT,
            "material",
            os.path.basename(nombre_archivo)
        )

        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)

    # 3. Borrar el registro del material
    material.delete()

    messages.success(request, "El material y su archivo fueron eliminados correctamente.")
    return redirect("material_principal_coordinador")


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
            archivo=archivo  # Django lo guarda en media/material automáticamente
        )
        nuevo.save()

        return redirect("material_principal")

    return render(request, "paginas/instructor/crear_material.html")
