from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('asignar/', views.asignar_view, name='asignar'),
    path('distribuidor/', views.distribuidor_view, name='distribuidor'),
    path('revendedor/', views.revendedor_view, name='revendedor'),
    path('carrito/<int:producto_id>/', views.carrito_view, name='carrito'),
    path('procesar-compra/', views.procesar_compra, name='procesar_compra'),
    path('cambiar-estado/<int:asignacion_id>/', views.cambiar_estado_asignacion, name='cambiar_estado_asignacion'),
    path('editar-producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('register/', views.register_user, name='register'),
]
