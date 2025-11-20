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
        # Guardar usuario principal
        usuario = super().save(commit=False)

        # Obtener el documento
        documento = self.cleaned_data["tipo_documento"]

        # Vincular documento al usuario
        usuario.iddocumento = documento

        # Guardar usuario
        if commit:
            usuario.save()

            # Guardar la relación Usuario-Rol
