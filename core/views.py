from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db.models import Count
from .forms import CustomLoginForm, AsignacionForm, UserCreationFormWithRol
from .models import Producto, Asignacion


class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

from django.contrib.auth import logout
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator

@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
class CustomLogoutView(LogoutView):
    next_page = '/'

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('core:home')

def home_view(request):
    productos = Producto.objects.all()
    print(f"Cantidad de productos en DB: {productos.count()}")
    return render(request, 'core/home.html', {'productos': productos})

@login_required
def asignar_view(request):
    if request.user.rol != 'ADMIN':
        return HttpResponseForbidden("No tiene permiso para acceder a esta sección.")
    
    if request.method == 'POST':
        form = AsignacionForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.admin = request.user
            asignacion.save()
            messages.success(request, 'Asignación creada correctamente.')
            return redirect('core:asignar')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = AsignacionForm()
    
    asignaciones = Asignacion.objects.all().order_by('-fecha_asignacion')
    return render(request, 'core/asignar.html', {'form': form, 'asignaciones': asignaciones})

@login_required
def distribuidor_view(request):
    if request.user.rol != 'DISTRIBUIDOR':
        return HttpResponseForbidden("No tiene permiso para acceder a esta sección.")
    
    asignaciones = Asignacion.objects.filter(distribuidor=request.user).order_by('-fecha_asignacion')
    productos_distintos = Asignacion.objects.filter(distribuidor=request.user).aggregate(
        total=Count('producto', distinct=True)
    )['total']
    
    return render(request, 'core/distribuidor.html', {
        'asignaciones': asignaciones,
        'productos_distintos': productos_distintos
    })

@login_required
def carrito_view(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'core/carrito.html', {'producto': producto})

@login_required
def register_user(request):
    if request.user.rol != 'ADMIN':
        return HttpResponseForbidden("No tiene permiso para registrar usuarios.")
        
    if request.method == 'POST':
        form = UserCreationFormWithRol(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('core:asignar')
    else:
        form = UserCreationFormWithRol()
    
    return render(request, 'core/register.html', {'form': form})
