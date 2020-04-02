from django.contrib.auth import get_user_model
from django.forms import TextInput, ModelForm

from .models import Profile


# class LoginForm(forms.Form):
#     username = forms.CharField()
#     password = forms.CharField(widget=forms.PasswordInput)


class UserEditForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите Имя'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите Фамилию'}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите Email'}),
            # 'photo': ImageField(attrs={'type': 'date', 'class': 'form-control'}),
        }


class ProfileEditForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'phone', 'photo')
        widgets = {
            'date_of_birth': TextInput(attrs={'type': 'date', 'class': 'form-control'}),
            # 'photo': ImageField(attrs={'type': 'date', 'class': 'form-control'}),
        }
