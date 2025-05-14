from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Producto, Asignacion

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'rol'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'imagen_url')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('precio',)

class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('distribuidor', 'producto', 'cantidad', 'fecha_asignacion', 'plan_pago')
    list_filter = ('fecha_asignacion', 'plan_pago', 'distribuidor', 'producto')
    search_fields = ('distribuidor__username', 'producto__nombre')
    date_hierarchy = 'fecha_asignacion'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Asignacion, AsignacionAdmin)
