from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout, login as auth_login, authenticate
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.db.models import Count, Q
from django.views.decorators.http import require_http_methods, require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout, login as auth_login, authenticate
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.db.models import Count
from django.views.decorators.csrf import csrf_protect

from .forms import (
    CustomLoginForm,
    AsignacionForm,
    UserCreationFormWithRol,
    ProductoForm,
    RevendedorCreationForm,
    CompraForm
)
from .models import Producto, Asignacion, Revendedor, Venta, CustomUser

class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = 'core:home'

def home_view(request):
    productos = Producto.objects.all()
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
    ventas = Asignacion.objects.filter(estado='PAGADO')

    total_ventas = sum(venta.producto.precio_publico * venta.cantidad for venta in ventas)
    cantidad_vendida = sum(venta.cantidad for venta in ventas)
    costo_total = sum(venta.producto.costo * venta.cantidad for venta in ventas)
    ganancia = total_ventas - costo_total

    context = {
        'form': form,
        'asignaciones': asignaciones,
        'total_ventas': total_ventas,
        'cantidad_vendida': cantidad_vendida,
        'costo_total': costo_total,
        'ganancia': ganancia,
    }

    return render(request, 'core/asignar.html', context)

@login_required
def distribuidor_view(request):
    if request.user.rol != 'DISTRIBUIDOR':
        return HttpResponseForbidden("No tiene permiso para acceder a esta sección.")

    asignaciones = Asignacion.objects.filter(distribuidor=request.user).order_by('-fecha_asignacion')
    productos_distintos = Asignacion.objects.filter(distribuidor=request.user).aggregate(
        total=Count('producto', distinct=True)
    )['total']

    if request.method == 'POST':
        form = RevendedorCreationForm(request.POST)
        if form.is_valid():
            revendedor = form.save(commit=False)
            revendedor.distribuidor = request.user
            revendedor.save()
            messages.success(request, 'Revendedor creado exitosamente.')
            return redirect('core:distribuidor')
    else:
        form = RevendedorCreationForm()

    return render(request, 'core/distribuidor.html', {
        'asignaciones': asignaciones,
        'productos_distintos': productos_distintos,
        'form': form,
    })

@login_required
def revendedor_view(request):
    if request.user.rol != 'REVENDEDOR':
        return HttpResponseForbidden("No tiene permiso para acceder a esta sección.")
    
    revendedor = get_object_or_404(Revendedor, user=request.user)
    asignaciones = Asignacion.objects.filter(
        distribuidor=revendedor.distribuidor
    ).order_by('-fecha_asignacion')
    
    return render(request, 'core/revendedor.html', {
        'asignaciones': asignaciones,
        'distribuidor': revendedor.distribuidor
    })

@login_required
def carrito_view(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            # Procesar la compra
            venta = Venta.objects.create(
                producto=producto,
                cantidad=form.cleaned_data.get('cantidad', 1),
                total=producto.precio_publico * form.cleaned_data.get('cantidad', 1),
                nombre_completo=form.cleaned_data['nombre_completo'],
                email=form.cleaned_data['email'],
                dni=form.cleaned_data['dni'],
                telefono=form.cleaned_data['telefono'],
                provincia=form.cleaned_data['provincia'],
                ciudad=form.cleaned_data['ciudad'],
                domicilio=form.cleaned_data['domicilio'],
                estado_pago='PENDIENTE'
            )
            messages.success(request, 'Compra registrada correctamente.')
            return redirect('core:home')
    else:
        form = CompraForm()
    
    return render(request, 'core/carrito.html', {
        'producto': producto,
        'form': form
    })


@csrf_protect
def procesar_compra(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        form = CompraForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'error': 'Datos inválidos'}, status=400)
        
        carrito = request.session.get('carrito', {})
        if not carrito:
            return JsonResponse({'error': 'Carrito vacío'}, status=400)
        
        total = Decimal('0')
        for producto_id, cantidad in carrito.items():
            producto = Producto.objects.get(id=producto_id)
            total += producto.precio_publico * Decimal(str(cantidad))
        
        # Crear la venta
        venta = Venta.objects.create(
            total=total,
            nombre_completo=form.cleaned_data['nombre_completo'],
            email=form.cleaned_data['email'],
            dni=form.cleaned_data['dni'],
            telefono=form.cleaned_data['telefono'],
            provincia=form.cleaned_data['provincia'],
            ciudad=form.cleaned_data['ciudad'],
            domicilio=form.cleaned_data['domicilio']
        )
        
        # Limpiar carrito
        request.session['carrito'] = {}
        
        return JsonResponse({
            'success': True,
            'message': 'Compra procesada correctamente',
            'venta_id': venta.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def cambiar_estado_asignacion(request, asignacion_id):
    if request.user.rol != 'ADMIN':
        return HttpResponseForbidden("No tiene permiso para cambiar el estado.")
    
    asignacion = get_object_or_404(Asignacion, id=asignacion_id)
    asignacion.estado = 'PAGADO' if asignacion.estado == 'PENDIENTE' else 'PENDIENTE'
    asignacion.save()
    
    messages.success(request, f'Estado actualizado a {asignacion.get_estado_display()}')
    return redirect('core:asignar')

@login_required
def editar_producto(request, producto_id):
    if request.user.rol != 'ADMIN':
        return HttpResponseForbidden("No tiene permiso para editar productos.")
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('core:home')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'core/editar_producto.html', {'form': form})

@login_required
def register_user(request):
    if request.user.rol != 'ADMIN' and request.user.rol != 'DISTRIBUIDOR':
        return HttpResponseForbidden("No tiene permiso para registrar usuarios.")
    
    if request.method == 'POST':
        if request.user.rol == 'ADMIN':
            form = UserCreationFormWithRol(request.POST)
        else:
            form = RevendedorCreationForm(request.POST)
            
        if form.is_valid():
            user = form.save()
            if request.user.rol == 'DISTRIBUIDOR':
                Revendedor.objects.create(
                    user=user,
                    distribuidor=request.user
                )
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('core:home')
    else:
        if request.user.rol == 'ADMIN':
            form = UserCreationFormWithRol()
        else:
            form = RevendedorCreationForm()
    
    return render(request, 'core/register.html', {'form': form})
