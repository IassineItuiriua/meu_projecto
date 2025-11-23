from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import UsuarioCreationForm, UsuarioChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    model = CustomUser

    list_display = ('username', 'email', 'first_name', 'last_name', 'nim', 'is_staff')
    search_fields = ('username', 'email', 'nim')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Dados militares', {'fields': ('nim',)}),
        ('Permissões', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'nim', 'password1', 'password2', 'is_staff')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
