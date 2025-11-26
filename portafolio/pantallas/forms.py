from django import forms
from .models import Usuario, Documento, Rol, UsuarioRol

class UsuarioForm(forms.ModelForm):

    tipo_documento = forms.ModelChoiceField(
        queryset=Documento.objects.all(),
        label="Tipo Documento"
    )

    numero_documento = forms.CharField(
        label="Número Documento",
        required=True
    )

    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        label="Rol"
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

    def save(self, commit=True):
        usuario = super().save(commit=False)

        # Asignar tipo de documento
        usuario.iddocumento = self.cleaned_data["tipo_documento"]

        if commit:
            usuario.save()

            # Crear o actualizar relación usuario-rol
            rol = self.cleaned_data["rol"]

            UsuarioRol.objects.update_or_create(
                idusuario=usuario,
                defaults={"idrol": rol}
            )

        return usuario

