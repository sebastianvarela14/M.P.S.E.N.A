from django import forms
from .models import Usuario, Documento, Rol, UsuarioRol

class UsuarioForm(forms.ModelForm):
    tipo_documento = forms.ModelChoiceField(
        queryset=Documento.objects.all(),  # Mostrar todos los documentos
        label="Tipo Documento",
        required=True
    )

    numero_documento = forms.CharField(
        label="Número Documento",
        required=True
    )

    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        label="Rol",
        required=True
    )

    class Meta:
        model = Usuario
        fields = [
            "nombres",
            "apellidos",
            "correo",
            "telefono",
            "usuario",
            "contrasena",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar sigla si existe, sino tipo
        self.fields['tipo_documento'].label_from_instance = lambda obj: obj.sigla if obj.sigla else obj.tipo

    def save(self, commit=True):
        usuario = super().save(commit=False)

        tipo_documento_obj = self.cleaned_data["tipo_documento"]
        numero_documento_str = self.cleaned_data["numero_documento"]

        # Crear o obtener un Documento único por tipo, sigla y numero
        documento_obj, created = Documento.objects.get_or_create(
            tipo=tipo_documento_obj.tipo,
            sigla=tipo_documento_obj.sigla,
            numero=numero_documento_str
        )

        usuario.iddocumento = documento_obj

        if commit:
            usuario.save()

            rol = self.cleaned_data["rol"]
            UsuarioRol.objects.update_or_create(
                idusuario=usuario,
                defaults={"idrol": rol}
            )

        return usuario