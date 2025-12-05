from django.db import models


class Archivos(models.Model):
    nombre_archivo = models.CharField(max_length=100)
    fecha_entrega = models.DateField(blank=True, null=True)
    archivo = models.FileField(upload_to='archivos/', null=True, blank=True)
    idcarpetas = models.ForeignKey('Carpetas', models.DO_NOTHING, db_column='idcarpetas', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archivos'



class Carpetas(models.Model):
    nombre = models.CharField(
        max_length=100, 
        db_comment='nombre de la carpeta (ej: plan concertado, evidencias de aprendizaje, etc.)'
    )
    descripcion = models.TextField(
        null=True, 
        blank=True, 
        db_comment='descripción informativa de la carpeta'
    )

    class Meta:
        managed = False
        db_table = 'carpetas'



class Documento(models.Model):
    tipo = models.CharField(max_length=20, db_comment='que tipo de documento tiene el usuario cedula, tarjeta de identidad, etc')
    numero = models.BigIntegerField(blank=True, null=True, db_comment='es el numero de identificacion')

    def __str__(self):
        return f"{self.tipo}"

    class Meta:
        managed = False
        db_table = 'documento'



class EvidenciasAprendiz(models.Model):
    archivo = models.CharField(max_length=50, db_comment='documentos evidencias, material de apoyo')
    observaciones = models.CharField(max_length=300, blank=True, null=True, db_comment=' observaciones del intructor')
    fecha_entrega = models.DateField(blank=True, null=True, db_comment='la fecha de la entrega de las evidencias')
    idusuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='idusuario', blank=True, null=True, db_comment=' esta es la llave foranea que conecta la tabla evidencias_aprendiz con usuario')
    idevidencias_instructor = models.ForeignKey('EvidenciasInstructor', models.DO_NOTHING, db_column='idevidencias_instructor', blank=True, null=True, db_comment=' esta es la llave foranea que conecta la tabla evidencias_aprendiz con evidencias_instructor')

    class Meta:
        managed = False
        db_table = 'evidencias_aprendiz'


class EvidenciasFicha(models.Model):
    idficha = models.ForeignKey('Ficha', models.DO_NOTHING, db_column='idficha', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla evidenciasins_usuario con usuario')
    idevidencias_instructor = models.ForeignKey('EvidenciasInstructor', models.DO_NOTHING, db_column='idevidencias_instructor', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla evidenciasins_usuario con evidencias_instructor')

    class Meta:
        managed = False
        db_table = 'evidencias_ficha'

class EvidenciasInstructor(models.Model):
    titulo = models.CharField(max_length=70, db_comment='titulo de la evidencia que el instructor crea')
    instrucciones = models.CharField(max_length=200, blank=True, null=True, db_comment='instrucciones detalladas de la evidencia a entregar')
    calificacion = models.CharField(max_length=20, db_comment='nota maxima o calificacion asignada a la evidencia')
    fecha_de_entrega = models.DateField(blank=True, null=True, db_comment='fecha limite en la que el aprendiz debe entregar la evidencia')
    
    
    archivo = models.FileField(
        upload_to="evidencias/",
        blank=True,
        null=True,
        db_comment='archivo adjunto correspondiente a la evidencia'
    )

    class Meta:
        managed = False
        db_table = 'evidencias_instructor'



class Ficha(models.Model):
    numero_ficha = models.IntegerField()
    idjornada = models.ForeignKey('Jornada', models.DO_NOTHING, db_column='idjornada', null=True, blank=True)
    idprograma = models.ForeignKey('Programa', models.DO_NOTHING, db_column='idprograma', null=True, blank=True)
    nombre_programa = models.ForeignKey(
        'NombrePrograma',
        models.DO_NOTHING,
        db_column='idnombre_programa',
        null=True,
        blank=True
    )

    ESTADOS = (
        ('Activa', 'Activa'),
        ('Inactiva', 'Inactiva'),
        ('Finalizada', 'Finalizada'),
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Activa')

    class Meta:
        managed = False
        db_table = 'ficha'





class FichaCarpetas(models.Model):
    idficha = models.ForeignKey(Ficha, models.DO_NOTHING, db_column='idficha', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla ficha_carpetas con ficha')
    idcarpetas = models.ForeignKey(Carpetas, models.DO_NOTHING, db_column='idcarpetas', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla usuario_carpeta con carpeta')

    class Meta:
        managed = False
        db_table = 'ficha_carpetas'


class FichaUsuario(models.Model):
    idusuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='idusuario', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla ficha_usuario con usuario')
    idficha = models.ForeignKey(Ficha, models.DO_NOTHING, db_column='idficha', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla ficha_usuario con ficha')

    class Meta:
        managed = False
        db_table = 'ficha_usuario'


class Jornada(models.Model):
    nombre = models.CharField(max_length=50, db_comment='aqui va si es diurna, nocturna o mixta')

    class Meta:
        managed = False
        db_table = 'jornada'


class Material(models.Model):
    titulo = models.CharField(max_length=100, db_comment='titulo del material')
    descripcion = models.CharField(max_length=500, blank=True, null=True, db_comment='instrucciones o descripcion del material de apoyo')
    archivo = models.FileField(
        upload_to="material/",
        blank=True,
        null=True,
        db_comment='archivo adjunto correspondiente a la evidencia'
    )
    class Meta:
        managed = False
        db_table = 'material'


class MaterialUsuario(models.Model):
    idusuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='idusuario', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla material_usuario con usuario')
    idmaterial = models.ForeignKey(Material, models.DO_NOTHING, db_column='idmaterial', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla material_usuario con material')

    class Meta:
        managed = False
        db_table = 'material_usuario'


class NombreAsignatura(models.Model):
    idtipo_asignatura = models.ForeignKey('TipoAsignatura', models.DO_NOTHING, db_column='idtipo_asignatura', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla nombre_asignatura con tipo_asignatura')
    idficha = models.ForeignKey(Ficha, models.DO_NOTHING, db_column='idficha', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla nombre_asignatura con ficha')
    nombre = models.CharField(max_length=200, db_comment='aqui va el nombre que se le asigne a la competencia')

    class Meta:
        managed = False
        db_table = 'nombre_asignatura'


class Programa(models.Model):
    programa = models.CharField(max_length=150, db_comment='tecnico o tecnologo')

    class Meta:
        managed = False
        db_table = 'programa'


class Rol(models.Model):
    tipo = models.CharField(max_length=50, db_comment='aqui se define el rol del usuario que son (aprendiz, instructor, coordinacion y observador)')

    def __str__(self):
        return self.tipo

    class Meta:
        managed = False
        db_table = 'rol'


class TipoAsignatura(models.Model):
    nombre = models.CharField(max_length=200, db_comment='Si la competencia es tecnica o transversal')

    class Meta:
        managed = False
        db_table = 'tipo_asignatura'


class Usuario(models.Model):
    nombres = models.CharField(max_length=100, db_comment='aqui van los nombre del usuario')
    apellidos = models.CharField(max_length=100, db_comment='aqui van los apellidos del usuario')
    correo = models.CharField(max_length=100, db_comment='aqui estara el correo del usuario')
    telefono = models.BigIntegerField(db_comment='aqui va el numero de telefono del usuario')
    usuario = models.CharField(max_length=100, db_comment='aqui va el usuario de regristro de cada uno de los usuarios')
    contrasena = models.CharField(max_length=20, db_comment='aca estara la contrasena para entrar al sistema de cada usuario')
    iddocumento = models.ForeignKey(Documento, models.DO_NOTHING, db_column='iddocumento', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla usuario con documento')

    class Meta:
        managed = False
        db_table = 'usuario'


class UsuarioRol(models.Model):
    idusuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='idusuario', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla usuario_rol con usuario')
    idrol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='idrol', blank=True, null=True, db_comment='esta es la llave foranea que une la tabla usuario_rol con rol')

    class Meta:
        managed = False
        db_table = 'usuario_rol'

class FichaAsignatura(models.Model):
    idficha = models.ForeignKey(Ficha, models.DO_NOTHING, db_column='idficha')
    idasignatura = models.ForeignKey(
        'NombreAsignatura',
        models.DO_NOTHING,
        db_column='idnombre_asignatura'
    )

    class Meta:
        managed = False
        db_table = 'ficha_asignatura'

class ArchivoInstructorFicha(models.Model):
    idarchivoficha = models.AutoField(primary_key=True)
    archivo = models.FileField(upload_to='portafolio_instructor/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    instructor = models.ForeignKey(
        'Usuario',
        on_delete=models.DO_NOTHING,
        db_column='idusuario'
    )
    ficha = models.ForeignKey(
        'Ficha',
        on_delete=models.DO_NOTHING,
        db_column='idficha'
    )
    carpeta = models.ForeignKey(
        'Carpetas',
        on_delete=models.DO_NOTHING,
        db_column='idcarpetas'
    )

    class Meta:
        managed = True
        db_table = 'archivo_instructor_ficha'

class NombrePrograma(models.Model):
    nombre = models.CharField(max_length=200, unique=True)

    class Meta:
        managed = False   # si la tabla ya existe
        db_table = 'nombre_programa'

    def __str__(self):
        return self.nombre

class PortafolioInstructor(models.Model):
    ficha = models.ForeignKey('Ficha', models.DO_NOTHING, db_column='idficha')
    carpeta = models.ForeignKey('Carpetas', models.DO_NOTHING, db_column='idcarpeta')
    trimestre = models.IntegerField(db_comment='trimestre asignado (1-7)')
    
    titulo_archivo = models.CharField(max_length=150, db_comment='nombre visible del archivo')
    archivo = models.FileField(upload_to="portafolio_instructor/", null=True, blank=True)
    
    fecha_subida = models.DateTimeField(auto_now_add=True)
    idinstructor = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='idinstructor')

    class Meta:
        managed = False
        db_table = 'portafolio_instructor'

from django.db import models
from django.contrib.auth.models import User

class CarpetaEquipo(models.Model):
    ficha = models.ForeignKey('Ficha', on_delete=models.CASCADE)
    trimestre = models.IntegerField()
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} (T{self.trimestre}) - Ficha {self.ficha.id}"

    class Meta:
        managed = False
        db_table = 'carpeta_equipo'


class ArchivoEquipo(models.Model):
    carpeta = models.ForeignKey(CarpetaEquipo, on_delete=models.CASCADE, related_name="archivos")
    archivo = models.FileField(upload_to="equipo_ejecutor/")
    nombre_editable = models.CharField(max_length=255)
    subido_por = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_editable

    class Meta:
        managed = False
        db_table = 'archivo_equipo'

