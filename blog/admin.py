from django.contrib import admin
from .models import Blog, Kategori, Yorum, FavoriteBlog, NewComment

admin.site.register(Blog)
admin.site.register(Kategori)
admin.site.register(Yorum)
admin.site.register(FavoriteBlog)
admin.site.register(NewComment)
