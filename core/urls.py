from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('asignar/', views.asignar_view, name='asignar'),
    path('distribuidor/', views.distribuidor_view, name='distribuidor'),
    path('carrito/<int:producto_id>/', views.carrito_view, name='carrito'),
]
