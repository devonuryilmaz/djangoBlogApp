from django.db import models
from django.shortcuts import reverse
from unidecode import unidecode
from django.template.defaultfilters import slugify, safe

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User

from ckeditor.fields import RichTextField
from uuid import uuid4
import os


def upload_to(instance, filename):
    extension = filename.split('.')[-1]
    new_name = '%s.%s' % (str(uuid4()), extension)
    unique_id = instance.unique_id
    return os.path.join('blog', unique_id, new_name)


class Kategori(models.Model):
    isim = models.CharField(max_length=20, verbose_name="Kategori İsim")

    class Meta:
        verbose_name_plural = 'Kategoriler'

    def __str__(self):
        return self.isim


class Blog(models.Model):

    YAYIN_TASLAK = ((None, 'Lütfen birini seçiniz..'),
                    ('yayin', 'YAYIN'), ('taslak', 'TASLAK'))

    title = models.CharField(max_length=100, blank=False, null=True,
                             verbose_name='Başlık Giriniz', help_text='Başlık bilgisi burada girilir.')
    icerik = RichTextField(
        max_length=1000, verbose_name='İçerik Giriniz', blank=False, null=True)
    # models.TextField(max_length=1000, verbose_name='İçerik Giriniz', blank=False, null=True)

    slug = models.SlugField(null=True, unique=True, editable=False)
    image = models.ImageField(default='default/default.png', blank=True, verbose_name='Resim', null=True,
                              help_text='Kapak Fotoğrafı Yükleyiniz', upload_to=upload_to)
    unique_id = models.CharField(max_length=100, editable=True, null=True)
    kategoriler = models.ManyToManyField(
        to=Kategori, related_name='blog', blank=True)
    createdDate = models.DateTimeField(auto_now_add=True, auto_now=False)
    yayin_taslak = models.CharField(
        choices=YAYIN_TASLAK, max_length=6, null=True, blank=False)

    user = models.ForeignKey(User, default=1, null=True,
                             on_delete=models.CASCADE, verbose_name='User', related_name='blog')

    class Meta:
        verbose_name_plural = 'Blog'
        ordering = ['-id']

    def __str__(self):
        return "%s - %s" % (self.title, self.user)

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.slug})

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return '/media/default/default.png'

    def getUniqueSlug(self):
        sayi = 0
        slug = slugify(unidecode(self.title))
        new_slug = slug
        while Blog.objects.filter(slug=new_slug).exists():
            sayi += 1
            new_slug = "%s-%s" % (slug, sayi)

        slug = new_slug
        return slug

    def get_yayin_taslak_html(self):
        if self.yayin_taslak == 'taslak':
            return safe('<small><span class="label label-{1}">{0}</span></small>'.format(self.get_yayin_taslak_display(), 'danger'))
        else:
            return safe('<small><span class="label label-{1}">{0}</span></small>'.format(self.get_yayin_taslak_display(), 'success'))

    def save(self, *args, **kwargs):
        if self.id is None:
            new_unique_id = str(uuid4())
            self.unique_id = new_unique_id
            self.slug = self.getUniqueSlug()
        else:
            blog = Blog.objects.get(slug=self.slug)
            if blog.title != self.title:
                self.slug = self.getUniqueSlug()
        super(Blog, self).save(*args, **kwargs)

    def get_added_favorite_user(self):
        # self.favorite_blog.all()
        return self.favorite_blog.values_list('user__username', flat=True)

    def get_comments_count(self):
        yorum_sayisi = self.comment.count()
        if yorum_sayisi > 0:
            return yorum_sayisi
        return 'Yorum Yok'

    def get_favorite_count(self):
        favorite_count = self.favorite_blog.count()
        if favorite_count > 0:
            return favorite_count
        return 'Beğeni Yok'

    def get_added_favorite_users_object(self):
        data_list = []
        querySet = self.favorite_blog.all()
        for obj in querySet:
            data_list.append(obj.user)
        return data_list

    @classmethod
    def get_taslak_or_yayin(cls, taslak_yayin):
        return cls.objects.filter(yayin_taslak=taslak_yayin)

    def get_blog_comments(self):
        return self.comment.all()

    def get_blog_comment_count(self):
        return len(self.get_blog_new_comments())

    def get_blog_new_comments(self):
        content_type = ContentType.objects.get_for_model(self)
        object_id = self.id
        all_comment = NewComment.objects.filter(
            content_type=content_type, object_id=object_id)
        return all_comment


class Yorum(models.Model):
    user = models.ForeignKey(User, null=True, default=1,
                             related_name='comment', on_delete=models.CASCADE)

    blog = models.ForeignKey(
        Blog, null=True, on_delete=models.CASCADE, related_name="comment")
    yorum_tarihi = models.DateTimeField(auto_now_add=True, null=True)
    icerik = models.TextField(verbose_name='Yorum',
                              max_length=1000, blank=False, null=True)

    class Meta:
        verbose_name_plural = "Yorumlar"

    def __str__(self):
        return '%s %s' % (self.user, self.blog)

    def get_screen_name(self):
        if self.user.first_name:
            return "%s" % (self.user.userprofile.user_full_name())
        else:
            return self.user.username


class NewComment(models.Model):
    user = models.ForeignKey(User, null=True, default=1,
                             related_name='+', on_delete=models.CASCADE)
    is_parent = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, models.CASCADE, null=True)
    object_id = models.PositiveIntegerField()
    content_obj = GenericForeignKey('content_type', 'object_id')

    yorum_tarihi = models.DateTimeField(auto_now_add=True, null=True)
    icerik = models.TextField(verbose_name='Yorum',
                              max_length=1000, blank=False, null=True)

    def __str__(self):
        username = self.user.username
        text = "{0} {1}".format(username, self.content_type.model)
        return text

    class Meta:
        verbose_name_plural = "İç İçe Yorumlar"

    @classmethod
    def add_comment(cls, nesne, model_type, user, icerik):
        content_type = ContentType.objects.get_for_model(nesne.__class__)
        cls.objects.create(user=user, icerik=icerik,
                           content_type=content_type, object_id=nesne.pk)
        if model_type == 'comment':
            nesne.is_parent = True
            nesne.save()

    def get_child_comments(self):
        if self.is_parent:
            content_type = ContentType.objects.get_for_model(self.__class__)
            all_child_comment = NewComment.objects.filter(
                content_type=content_type, object_id=self.pk)
            return all_child_comment
        return None


class FavoriteBlog(models.Model):
    user = models.ForeignKey(User, null=True, default=1,
                             related_name='favorite_blog', on_delete=models.CASCADE)
    blog = models.ForeignKey(
        Blog, null=True, on_delete=models.CASCADE, related_name="favorite_blog")

    class Meta:
        verbose_name_plural = 'Favorilere Eklenen Gönderiler'

    def __str__(self):
        return '%s %s' % (self.user, self.blog)
