from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser, Asignacion

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600',
                'placeholder': 'Usuario'
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600',
                'placeholder': 'Contraseña'
            }
        )
    )

class DistribuidorCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases de Tailwind CSS a los campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600'
            })
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'DISTRIBUIDOR'
        if commit:
            user.save()
        return user

class AsignacionForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        fields = ['distribuidor', 'producto', 'cantidad', 'plan_pago']
        widgets = {
            'distribuidor': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600'
                }
            ),
            'producto': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600'
                }
            ),
            'cantidad': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600',
                    'min': '1'
                }
            ),
            'plan_pago': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar distribuidores para mostrar solo usuarios con rol DISTRIBUIDOR
        self.fields['distribuidor'].queryset = CustomUser.objects.filter(rol='DISTRIBUIDOR')
