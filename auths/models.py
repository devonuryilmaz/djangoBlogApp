from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.db.models.signals import post_save
# Create your models here.


class UserProfile(models.Model):
    SEX = ((None, 'Cinsiyet Seçiniz'), ('diger', 'DİGER'),
           ('erkek', 'ERKEK'), ('kadin', 'KADIN'))
    user = models.OneToOneField(
        User, null=True, blank=False, verbose_name="User", on_delete=models.CASCADE)
    bio = models.TextField(
        max_length=1000, verbose_name="Hakkımda", blank=True, null=True)
    profile_photo = models.ImageField(
        null=True, blank=True, verbose_name="Profil Fotoğrafı")
    born_time = models.DateField(
        null=True, blank=True, verbose_name="Doğum Tarihi")
    sex = models.CharField(choices=SEX, blank=True,
                           null=True, verbose_name="Cinsiyet", max_length=6)

    class Meta():
        verbose_name_plural = "Kullanici Profilleri"

    def getScreenName(self):
        user = self.user
        if user.get_full_name():
            return user.get_full_name()
        return user.username

    def user_full_name(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        return None

    def get_user_profile_url(self):
        url = reverse('user-profile', kwargs={'username': self.user.username})
        return url

    def getProfilePhoto(self):
        if self.profile_photo:
            return self.profile_photo.url
        return "/static/img/default-profile.png"

    def __str__(self):
        return "%s Profile" % (self.getScreenName())


def create_profile(sender, created, instance, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_profile, sender=User)
