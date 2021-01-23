from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Following(models.Model):
    follower = models.ForeignKey(
        User, null=True, related_name='follower', verbose_name='Takip Eden', on_delete=models.CASCADE)
    followed = models.ForeignKey(
        User, null=True, related_name='followed', verbose_name='Takip Edilen', on_delete=models.CASCADE)

    def __str__(self):
        return "Follower {} - Followed {}".format(self.follower.username, self.followed.username)

    @classmethod
    def kullanici_takip_et(cls, follower, followed):
        cls.objects.create(follower=follower, followed=followed)

    @classmethod
    def kullanici_takibi_birak(cls, follower, followed):
        cls.objects.filter(follower=follower, followed=followed).delete()

    @classmethod
    def kullanici_takip_kontrol(cls, follower, followed):
        return cls.objects.filter(follower=follower, followed=followed).exists()

    @classmethod
    def get_takipci_sayisi(cls, user):
        data = {'takip_edilenler': 0, 'takipciler': 0}
        takip_edilenler = cls.objects.filter(follower=user).count()
        takipciler = cls.objects.filter(followed=user).count()
        data.update({'takip_edilenler': takip_edilenler,
                     'takipciler': takipciler})
        return data

    @classmethod
    def takipci_listesi(cls, user):
        return cls.objects.filter(followed=user)

    @classmethod
    def takip_edilen_listesi(cls, user):
        return cls.objects.filter(follower=user)

    @classmethod
    def takip_edilen_kullanici_adlari(cls, user):
        followed = Following.takip_edilen_listesi(user)
        return followed.values_list('followed__username', flat=True)
