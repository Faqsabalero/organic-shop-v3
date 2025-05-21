from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser, Asignacion, Producto, Revendedor

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

class UserCreationFormWithRol(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'rol', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases de Tailwind CSS a los campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600'
            })

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'costo', 'precio_distribuidor', 'precio_revendedor', 'precio_publico', 'imagen_url']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600', 'rows': 4}),
            'costo': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600', 'min': '0', 'step': '0.01'}),
            'precio_distribuidor': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600', 'min': '0', 'step': '0.01'}),
            'precio_revendedor': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600', 'min': '0', 'step': '0.01'}),
            'precio_publico': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600', 'min': '0', 'step': '0.01'}),
            'imagen_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600'}),
        }

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

class RevendedorCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600'
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'REVENDEDOR'
        if commit:
            user.save()
        return user

class CompraForm(forms.Form):
    nombre_completo = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600',
            'placeholder': 'Nombre completo'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600',
            'placeholder': 'Correo electrónico'
        })
    )
    dni = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600',
            'placeholder': 'DNI'
        })
    )
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600',
            'placeholder': 'Teléfono'
        })
    )
    provincia = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600',
            'placeholder': 'Provincia'
        })
    )
    ciudad = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600',
            'placeholder': 'Ciudad'
        })
    )
    domicilio = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-600',
            'placeholder': 'Domicilio'
        })
    )
