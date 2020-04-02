from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your models here.
user = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=30, default="+7", verbose_name="Номер телефона")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    photo = models.ImageField(upload_to="users/%Y/%m/%d", blank=True, verbose_name='Аватар')

    def __str__(self):
        return f'Profile for user {self.user.username}'

    class Meta:
        verbose_name = 'Профайл пользователя'
        verbose_name_plural = 'Профайлы пользователей'

    @property
    def photo_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        return 'media/users/no_image.png'

    def photo_tag(self):
        return mark_safe(f'<img src="/{self.photo_url}" width="50" height="50" style="object-fit: cover;"/>')
        # return self.photo_url

    photo_tag.short_description = 'Photo'


@receiver(post_save, sender=user)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=user)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
