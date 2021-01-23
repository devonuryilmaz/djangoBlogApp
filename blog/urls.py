from django.urls import path, re_path

from .views import post_list, post_delete, post_update, post_add, post_detail, add_comment, add_or_remove_favorite, post_list_favorite_user, new_add_comment, get_child_comment_form

urlpatterns = [
    path('', post_list, name="post-list"),
    path('create/', post_add, name="post-create"),
    re_path(r'^delete/(?P<slug>[-\w]+)/$', post_delete, name="post-delete"),
    re_path(r'^update/(?P<slug>[-\w]+)/$', post_update, name="post-update"),
    re_path(r'^detail/(?P<slug>[-\w]+)/$', post_detail, name="post-detail"),
    re_path(r'^add-comment/(?P<slug>[-\w]+)/$',
            add_comment, name="add-comment"),
    path("add-new-comment/<int:pk>/<str:model_type>/",
         new_add_comment, name="add-new-comment"),
    re_path(r'^favorite/(?P<slug>[-\w]+)/$',
            add_or_remove_favorite, name="favorite"),
    path("post-favorite-users/<str:slug>/",
         post_list_favorite_user, name="post_list_favorite_user"),
    path("get_child_comment_form/", get_child_comment_form,
         name="get_child_comment_form"),
]
