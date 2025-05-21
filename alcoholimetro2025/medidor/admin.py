from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Empleado, MuestraAlcohol
from .forms import EmpleadoCreationForm

class EmpleadoAdmin(UserAdmin):
    # Formulario para crear usuarios
    add_form = EmpleadoCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'identificacion',
                'email',
                'first_name',
                'last_name',
                'departamento',
                'password1',
                'password2'
            ),
        }),
    )
    
    # Campos a mostrar en el listado
    list_display = (
        'username',
        'email',
        'identificacion',
        'departamento',
        'is_staff'
    )
    
    # Filtros
    list_filter = ('departamento', 'is_staff')
    
    # Campos editables
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'identificacion',
                'departamento',
                'telefono',
                'fecha_ingreso'
            )
        }),
        ('Permisos', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(MuestraAlcohol)