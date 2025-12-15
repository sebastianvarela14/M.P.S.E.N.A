from django.urls import path
from . import views
urlpatterns = [
    path("plantillains/", views.plantillains, name="plantillains"),
    path("instructor/", views.fichas_ins, name="fichas_ins"),
    path('tareas/', views.tareas, name='tareas'),
    path('tareas_2/', views.tareas_2, name='tareas_2'),
    path('calificaciones/', views.calificaciones, name='calificaciones'),

    path("agregar_evidencia/", views.agregar_evidencia, name="agregar_evidencia"),
    path("agregar_evidencia_coor/", views.agregar_evidencia_coor, name="agregar_evidencia_coor"),

    path("material_coordinador/", views.material_coordinador, name="material_coordinador"),

    path("portafolio_aprendices/<int:ficha_id>/", views.portafolio_aprendices, name="portafolio_aprendices"),

    path("calificacion/", views.calificacion, name="calificacion"),
    path("tarea/", views.tarea, name="tarea"),

    path("datos/", views.datos, name="datos"),
    path("datos_ins/", views.datos_ins, name="datos_ins"),
    path("evidencias/", views.evidencias, name="evidencias"),

    path("material2/", views.material2, name="material2"),
    path("portafolio_aprendices/", views.portafolio_aprendices, name="portafolio_aprendices"),


    path("lista_aprendices/", views.lista_aprendices, name="lista_aprendices"),

    path("portafolio/<int:ficha_id>/", views.portafolio, name="portafolio"),
    path("carpetas2/", views.carpetas2, name="carpetas2"),

    path("taller/", views.taller, name="taller"),
    path("tareas/", views.tareas, name="tareas"),

    path('carpetasins/<int:ficha_id>/<int:trimestre>/', views.carpetasins, name='carpetasins'),
    path("subir_archivo_portafolio/", views.subir_archivo_portafolio, name="subir_archivo_portafolio"),
    path("eliminar_archivo_portafolio/<int:id>/", views.eliminar_archivo_portafolio, name="eliminar_archivo_portafolio"),
    path('carpetas/editar/<int:id>/<int:ficha_id>/<int:trimestre>/',views.editar_carpeta,name='editar_carpeta'),
    path('eliminar_carpeta/<int:id>/<int:ficha_id>/<str:trimestre>/', views.eliminar_carpeta, name='eliminar_carpeta'),
    path("carpeta/crear/<int:id>/<int:ficha_id>/<int:trimestre>/", views.crear_carpeta, name="crear_carpeta"),


    path("trimestre/", views.trimestre, name="trimestre"),

    path('carpetas_aprendiz/<int:aprendiz_id>/<int:trimestre>/', views.carpetas_aprendiz, name='carpetas_aprendiz'),
    path('trimestre_aprendiz/<int:aprendiz_id>/', views.trimestre_aprendiz, name='trimestre_aprendiz'),
    path("trimestre_general/", views.trimestre_general, name="trimestre_general"),
    path("carpetas/", views.carpetas, name="carpetas"),
    path("material_principal/", views.material_principal, name="material_principal"),
    path("lista_aprendices/", views.lista_aprendices, name="lista_aprendices"),
    path('material/<int:id>/', views.adentro_material, name='adentro_material'),
    path("lista_aprendices1/", views.lista_aprendices1, name="lista_aprendices1"),
    path("datoslaura/", views.datoslaura, name="datoslaura"),
    path("entrada/<int:asignatura_id>/", views.entrada, name="entrada"),
    path('archivo/agregar/<int:carpeta_id>/', views.archivo_agregar, name='archivo_agregar'),
    path('archivo/editar/<int:archivo_id>/', views.archivo_editar, name='archivo_editar'),
    path('archivo/eliminar/<int:archivo_id>/', views.archivo_eliminar, name='archivo_eliminar'),


    


    path("adentro_material1/", views.adentro_material1, name="adentro_material1"),
    path("evidencia_guia/<int:evidencia_id>/", views.evidencia_guia, name="evidencia_guia"),
    path("evidencia_guia1/", views.evidencia_guia1, name="evidencia_guia1"),
    path("aprendiz/", views.inicio, name="inicio"),
    path("carpetas_aprendiz1/", views.carpetas_aprendiz1, name="carpetas_aprendiz1"),
    path("carpetas_aprendiz2/", views.carpetas_aprendiz2, name="carpetas_aprendiz2"),
    path("coordinador/", views.coordinador, name="coordinador"),


    path("trimestre_laura/", views.trimestre_laura, name="trimestre_laura"),
    path('carpetas_laura/<int:trimestre>/', views.carpetas_laura, name='carpetas_laura'),
    path("evidencia_laura/<int:id>/", views.evidencia_laura, name="evidencia_laura"),
    path("evidencia_guialaura/<int:id>", views.evidencia_guialaura, name="evidencia_guialaura"),
    path('asignar-instructor/', views.asignar_instructor_asignatura, name='asignar_instructor_asignatura'),
    path("material_laura/", views.material_laura, name="material_laura"),
    path("adentro_material_aprendiz/", views.adentro_material_aprendiz, name="adentro_material_aprendiz"),
    path("carpetas_aprendiz_observador/", views.carpetas_aprendiz_observador, name="carpetas_aprendiz_observador"),
    path("carpetas_observador/", views.carpetas_observador, name="carpetas_observador"),
    path("inicio_observador/", views.inicio_observador, name="inicio_observador"),
    path("lista_aprendices_observador/", views.lista_aprendices_observador, name="lista_aprendices_observador"),
    path("observador/", views.observador, name="observador"),
    path("portafolio_aprendices_observador/", views.portafolio_aprendices_observador, name="portafolio_aprendices_observador"),
    path("portafolio_observador/", views.portafolio_observador, name="portafolio_observador"),
    path("trimestre_aprendiz_observador/", views.trimestre_aprendiz_observador, name="trimestre_aprendiz_observador"),
    path("trimestre_observador/", views.trimestre_observador, name="trimestre_observador"),
    path('adentro_material_observador/<int:id>/', views.adentro_material_observador, name='adentro_material_observador'),   
    path('material_principal_observador/', views.material_principal_observador, name='material_principal_observador'),
    path("evidencia_guia_observador/<int:evidencia_id>/", views.evidencia_guia_observador, name="evidencia_guia_observador"),
    path('evidencias_observador/<int:ficha_id>/', views.evidencias_observador, name='evidencias_observador'),
    path('adentro_material_coordinador/<int:id>/', views.adentro_material_coordinador, name='adentro_material_coordinador'),
    path("carpetas_coordinador/<int:ficha_id>/<int:trimestre>/", views.carpetas_coordinador, name="carpetas_coordinador"),
    path("evidencia_guia_coordinador/<int:evidencia_id>/", views.evidencia_guia_coordinador, name="evidencia_guia_coordinador"),
    path("evidencias_coordinador/<int:ficha_id>/", views.evidencias_coordinador, name="evidencias_coordinador"),
    path("inicio_coordinador/", views.inicio_coordinador, name="inicio_coordinador"),
    path("lista_aprendices_coordinador/", views.lista_aprendices_coordinador, name="lista_aprendices_coordinador"),
    path("material_principal_coordinador/", views.material_principal_coordinador, name="material_principal_coordinador"),
    path("portafolio_aprendices_coordinador/", views.portafolio_aprendices_coordinador, name="portafolio_aprendices_coordinador"),
    path("trimestre_coordinador/", views.trimestre_coordinador, name="trimestre_coordinador"),
    path("datos_coordinador/", views.datos_coordinador, name="datos_coordinador"),

    path("agregar_carpeta/", views.agregar_carpeta, name="agregar_carpeta"),
    path("plan_concertado/", views.plan_concertado, name="plan_concertado"),
    path("evidencia_calificar/", views.evidencia_calificar, name="evidencia_calificar"),
    path("calificaciones_observador/", views.calificaciones_observador, name="calificaciones_observador"),
    path("evidencia_calificar_observador/", views.evidencia_calificar_observador, name="evidencia_calificar_observador"),
    path("datos_observador/", views.datos_observador, name="datos_observador"),
    path("carpetas_general/", views.carpetas_general, name="carpetas_general"),
    path("carpetas_general_ins/", views.carpetas_general_ins, name="carpetas_general_ins"),
    path("trimestre_general_coordinador/", views.trimestre_general_coordinador, name="trimestre_general_coordinador"),

    path("trimestre_aprendiz_coordinador/<int:aprendiz_id>/", views.trimestre_aprendiz_coordinador, name="trimestre_aprendiz_coordinador"),

    path("carpetas_aprendiz_coordinador/<int:aprendiz_id>/<int:trimestre>/", views.carpetas_aprendiz_coordinador, name="carpetas_aprendiz_coordinador"),

    path("calificaciones_coordinador/", views.calificaciones_coordinador, name="calificaciones_coordinador"),

    path("evidencia_calificar_coordinador/", views.evidencia_calificar_coordinador, name="evidencia_calificar_coordinador"),
    path("", views.sesion, name="sesion"),

    path("configuracion_instructor/", views.configuracion_instructor, name="configuracion_instructor"),
    path("actualizar_contrasena/", views.actualizar_contrasena, name="actualizar_contrasena"),
    path("configuracion_instructor_2/", views.configuracion_instructor_2, name="configuracion_instructor_2"),
    path("configuracion_aprendiz/", views.configuracion_aprendiz, name="configuracion_aprendiz"),
    path("configuracion_aprendiz_2/", views.configuracion_aprendiz_2, name="configuracion_aprendiz_2"),
    path("configuracion_observador/", views.configuracion_observador, name="configuracion_observador"),
    path("configuracion_observador_2/", views.configuracion_observador_2, name="configuracion_observador_2"),
    path("configuracion_coordinador/", views.configuracion_coordinador, name="configuracion_coordinador"),
    path("evidencia_calificada/", views.evidencia_calificada, name="evidencia_calificada"),
    path("configuracion_coordinador_base/", views.configuracion_coordinador_base, name="configuracion_coordinador_base"),
    path("configuracion_coordinador_base_2/", views.configuracion_coordinador_base_2, name="configuracion_coordinador_base_2"),
    path("ficha_coordinador/", views.ficha_coordinador, name="ficha_coordinador"),
    path("ficha_aprendiz/", views.ficha_aprendiz, name="ficha_aprendiz"),
    path("ficha_aprendiz_2/", views.ficha_aprendiz_2, name="ficha_aprendiz_2"),
    path("ficha_instructor/", views.ficha_instructor, name="ficha_instructor"),
    path("ficha_observador/", views.ficha_observador, name="ficha_observador"),
    path("equipo_ejecutor/", views.equipo_ejecutor, name="equipo_ejecutor"),
    path("equipo/subcarpeta/<int:carpeta_id>/", views.crear_subcarpeta_equipo, name="crear_subcarpeta_equipo"),


    # Vista por trimestre
    path("equipo_ejecutor/<int:trimestre>/", views.opc_equipoejecutor, name="opc_equipoejecutor"),

    # CRUD Carpetas
    path("equipo_ejecutor/<int:trimestre>/crear/", views.crear_carpeta_equipo, name="crear_carpeta_equipo"),
    path("equipo_ejecutor/editar/<int:carpeta_id>/", views.editar_carpeta_equipo, name="editar_carpeta_equipo"),
    path("equipo_ejecutor/eliminar/<int:carpeta_id>/", views.eliminar_carpeta_equipo, name="eliminar_carpeta_equipo"),

    # Archivos
    path("equipo_ejecutor/subir/<int:carpeta_id>/", views.subir_archivo_equipo, name="subir_archivo_equipo"),
    path("equipo_ejecutor/eliminar_archivo/<int:archivo_id>/", views.eliminar_archivo_equipo, name="eliminar_archivo_equipo"),

    path("fichas_equipoejecutor_coordinador/", views.fichas_equipoejecutor_coordinador, name="fichas_equipoejecutor_coordinador"),
    path("equipo_coordinador/", views.equipo_coordinador, name="equipo_coordinador"),
    path('material/<int:id>/editar/', views.material_editar, name='material_editar'),
    path('material_coordinador/<int:id>/editar/', views.material_editar_coordinador, name='material_editar_coordinador'),
    path("evidencia_guia_editar/<int:evidencia_id>/", views.evidencia_guia_editar, name="evidencia_guia_editar"),
    path("evidencia_guia_editar_coordinador/<int:evidencia_id>/",views.evidencia_guia_editar_coordinador,name="evidencia_guia_editar_coordinador"),



    path("evidencia/eliminar/<int:evidencia_id>/", views.eliminar_evidencia, name="eliminar_evidencia"),
    path("evidencia_coordinador/eliminar/<int:evidencia_id>/", views.eliminar_evidencia_coordinador, name="eliminar_evidencia_coordinador"),
    path("carpetas_aprendiz_crear/", views.carpetas_aprendiz_crear, name="carpetas_aprendiz_crear"),
    path("carpetas_aprendiz_editar/", views.carpetas_aprendiz_editar, name="carpetas_aprendiz_editar"),
    path("datos_ins_editar/", views.datos_ins_editar, name="datos_ins_editar"),
    path("coordinador_editar/<int:id>/", views.coordinador_editar, name="coordinador_editar"),
    path("coordinador_agregar/", views.coordinador_agregar, name="coordinador_agregar"),
    path("carpetas2_editar/", views.carpetas2_editar, name="carpetas2_editar"),
    path("carpetas2_crear/", views.carpetas2_crear, name="carpetas2_crear"),
    path("administrar_usuario/", views.administrar_usuario, name="administrar_usuario"),
    path("administrar_usuario/crear/", views.administrar_usuario_crear, name="administrar_usuario_crear"),
    path("administrar_usuario/editar/<int:id>/", views.administrar_usuario_editar, name="administrar_usuario_editar"),
    path("usuario/eliminar/<int:usuario_id>/", views.eliminar_usuario, name="eliminar_usuario"),
    path("datos/<int:id>/", views.datos_aprendiz, name="datos"),
    path("actualizar_contrasena/", views.actualizar_contrasena, name="actualizar_contrasena"),
    

    path('seleccionar_ficha/<int:id_ficha>/', views.seleccionar_ficha, name='seleccionar_ficha'),
    path('seleccionar_ficha_coordinador/<int:id_ficha>/', views.seleccionar_ficha_coordinador, name='seleccionar_ficha_coordinador'),
    path("configuracion_coordinador/eliminar_instructor/<int:usuario_id>/<int:ficha_id>/", views.eliminar_instructor, name="eliminar_instructor"),
    path("datos_coordinador_editar/", views.datos_coordinador_editar, name="datos_coordinador_editar"),
    path("eliminar_aprendiz/<int:aprendiz_id>/<int:ficha_id>/", views.eliminar_aprendiz, name="eliminar_aprendiz"),
    path('datos_coor/<int:id>/', views.datos_coor, name='datos_coor'),
    path("eliminar_asignatura/<int:ficha_id>/<int:asig_id>/",views.eliminar_asignatura,name="eliminar_asignatura"),
    path('ficha_coordinador_editar/<int:id>/', views.ficha_coordinador_editar, name='ficha_coordinador_editar'),
    path("seleccionar_ficha_observador/<int:id_ficha>/", views.seleccionar_ficha_observador, name="seleccionar_ficha_observador"),   
    path("opc_equipoejecutor_coordinador/<int:trimestre>/", views.opc_equipoejecutor_coordinador, name="opc_equipoejecutor_coordinador"),
    path("equipo_ejecutor_coordinador/", views.equipo_ejecutor_coordinador, name="equipo_ejecutor_coordinador"),
    path("portafolio_coordinador/", views.portafolio_coordinador, name="portafolio_coordinador"),
    path("crear_material/", views.crear_material, name="crear_material"),
    path("eliminar_archivo_evidencia/<int:evidencia_id>/", views.eliminar_archivo_evidencia, name="eliminar_archivo_evidencia"),
    path("usuarios/masivo/", views.administrar_usuario_masivo, name="administrar_usuario_masivo"),
    path("usuarios/descargar-plantilla/", views.descargar_plantilla_usuarios, name="descargar_plantilla_usuarios"),
    path("usuarios/tipos-documento/", views.gestionar_tipos_documento, name="gestionar_tipos_documento"),
    path("usuarios/tipos-documento/editar/<int:id>/", views.editar_tipo_documento, name="editar_tipo_documento"),
    path("eliminar_material/<int:material_id>/", views.eliminar_material, name="eliminar_material"),

    path("agregar_jornada/", views.agregar_jornada, name="agregar_jornada"),
    path("agregar_programa/", views.agregar_programa, name="agregar_programa"),
    path("agregar_nombre_programa/", views.agregar_nombre_programa, name="agregar_nombre_programa"),
    path("material/eliminar_coordinador/<int:material_id>/", views.eliminar_material_coordinador, name="eliminar_material_coordinador"),



    ]
