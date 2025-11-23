from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'nim')


class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'nim', 'is_staff')
