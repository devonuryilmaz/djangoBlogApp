from django.urls import path
from .views import register,user_login,user_logout, user_profile, user_settings, about_user,user_password_change

urlpatterns = [
    path('register/', register, name="register"),
    path('login/', user_login, name="login"),
    path('logout/', user_logout, name="logout"),
    path('<str:username>', user_profile, name="user-profile"),
    path('settings/', user_settings, name="user-settings"),
    path('<str:username>/about/', about_user, name="about-user"),
    path('password-change/', user_password_change, name="user-password-change")

]

 