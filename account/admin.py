from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User

from account.models import Profile


# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('avatar_tag', 'user') # В качестве поля указываем метод, который вернёт тег картинки в списке пользовательских профилей
#     readonly_fields = ['avatar_tag'] # обязательно read only режим
#     fields = ('avatar_tag', 'user') # Указываем поля, которые нужно отобразить в административной форме

# Register your models here.


# @register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = ['photo_tag', 'user', 'date_of_birth']
    list_display = ['photo_tag', 'user', 'date_of_birth']
    readonly_fields = ['photo_tag']

    class Meta:
        model = Profile


# Нужна inline форма
class ProfileInline(admin.StackedInline):
    model = Profile  # указываем модель профиля
    can_delete = False  # запрещаем удаление
    fields = ('photo_tag', 'date_of_birth', 'phone')  # Указываем, какое поле отображать, снова тег аватарки
    readonly_fields = ['photo_tag']  # Указываем, что это read only поле


# Создаём свою форму для отображения пользовательского профиля
class EUserAdmin(UserAdmin):
    # Указываем, что будет в качестве inline формы
    inlines = [
        ProfileInline
    ]
    # модифицируем список отображаемых полей, чтобы увидеть аватарку с остальными полями
    list_display = ('photo_tag',) + UserAdmin.list_display + ('bday', 'phone')

    # а также создаём метод для получения тега аватарки из пользовательского профиля
    def photo_tag(self, obj):
        return obj.profile.photo_tag()

    def bday(self, obj):
        return obj.profile.date_of_birth

    def phone(self, obj):
        return obj.profile.phone


admin.site.register(Profile, ProfileAdmin)
admin.site.unregister(User)
admin.site.register(User, EUserAdmin)
