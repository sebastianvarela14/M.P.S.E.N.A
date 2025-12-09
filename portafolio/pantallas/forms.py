from django import forms
from .models import Usuario, Documento, Rol, UsuarioRol

class UsuarioForm(forms.ModelForm):

    tipo_documento = forms.ModelChoiceField(
        queryset=Documento.objects.all(),
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
            "numero_documento",
            "tipo_documento",
            "rol",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 👉 Aquí definimos cómo se ve cada opción en el <select>
        self.fields['tipo_documento'].label_from_instance = lambda obj: obj.tipo

    def save(self, commit=True):
        usuario = super().save(commit=False)

        # Guardar tipo documento
        usuario.iddocumento = self.cleaned_data["tipo_documento"]

        # Guardar número documento
        usuario.numero_documento = self.cleaned_data["numero_documento"]

        if commit:
            usuario.save()

            # Guardar rol en tabla intermedia
            rol = self.cleaned_data["rol"]

            UsuarioRol.objects.update_or_create(
                idusuario=usuario,
                defaults={"idrol": rol}
            )

        return usuario
