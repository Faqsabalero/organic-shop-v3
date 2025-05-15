from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from .forms import CustomLoginForm, AsignacionForm, UserCreationFormWithRol, ProductoForm
from .models import Producto, Asignacion


class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = 'core:home'

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

    # Calcular datos de ventas para la pestaña "Ventas"
    total_ventas = 0
    cantidad_vendida = 0
    costo_total = 0
    ganancia = 0

    ventas = Asignacion.objects.filter(estado='PAGADO')
    for venta in ventas:
        cantidad_vendida += venta.cantidad
        costo_total += venta.producto.costo * venta.cantidad
        total_ventas += venta.producto.precio * venta.cantidad

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
    
    return render(request, 'core/distribuidor.html', {
        'asignaciones': asignaciones,
        'productos_distintos': productos_distintos
    })

from decimal import Decimal
from django.http import JsonResponse
from django.conf import settings
import mercadopago

def carrito_view(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    
    cantidad = int(request.GET.get('cantidad', 1))
    preference_data = {
        "items": [
            {
                "title": producto.nombre,
                "quantity": cantidad,
                "currency_id": "ARS",
                "unit_price": float(producto.precio),
                "description": producto.descripcion[:100],  # Limitamos la descripción a 100 caracteres
                "picture_url": producto.imagen_url
            }
        ],
        "back_urls": {
            "success": request.build_absolute_uri('/pago-exitoso/'),
            "failure": request.build_absolute_uri('/pago-fallido/'),
            "pending": request.build_absolute_uri('/pago-pendiente/')
        },
        "auto_return": "approved",
    }
    
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    
    return render(request, 'core/carrito.html', {
        'producto': producto,
        'preference_id': preference['id'],
        'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
    })

def pago_exitoso(request):
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    merchant_order_id = request.GET.get('merchant_order_id')
    
    if status == 'approved':
        # Obtener detalles del pago usando el SDK de Mercado Pago
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        payment_info = sdk.payment().get(payment_id)
        
        if payment_info["status"] == 200:
            payment_data = payment_info["response"]
            
            # Crear registro de venta
            venta = Venta.objects.create(
                producto_id=payment_data["additional_info"]["items"][0]["id"],
                cantidad=payment_data["additional_info"]["items"][0]["quantity"],
                total=Decimal(str(payment_data["transaction_amount"])),
                email_comprador=payment_data.get("payer", {}).get("email"),
                estado_pago='PAGADO'
            )
            
            messages.success(request, '¡Pago realizado con éxito! Número de orden: {}'.format(merchant_order_id))
        else:
            messages.warning(request, 'El pago fue aprobado pero no pudimos procesar la venta.')
    
    return redirect('core:home')

def pago_fallido(request):
    messages.error(request, 'El pago no pudo ser procesado.')
    return redirect('core:home')

def pago_pendiente(request):
    messages.info(request, 'El pago está pendiente de confirmación.')
    return redirect('core:home')

def procesar_compra(request, producto_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        email = request.POST.get('email', '')
        
        if cantidad < 1:
            return JsonResponse({'error': 'Cantidad inválida'}, status=400)
        
        total = Decimal(producto.precio) * Decimal(cantidad)
        
        # Crear la venta
        venta = Venta.objects.create(
            producto=producto,
            cantidad=cantidad,
            total=total,
            email_comprador=email
        )
        
        # Aquí se integraría con Mercado Pago
        # Por ahora solo retornamos éxito
        return JsonResponse({
            'success': True,
            'message': 'Venta procesada correctamente',
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
