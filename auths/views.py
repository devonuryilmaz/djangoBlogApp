from django.shortcuts import render, reverse, HttpResponseRedirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .forms import RegisterForm, LoginForm, UserProfileUpdateForm, PasswordChangeForm2
from blog.decorators import anonymous_required
from .models import UserProfile
from blog.models import Blog
from following.models import Following
# Create your views here.


@anonymous_required
def register(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect(reverse('post-list'))
    form = RegisterForm(data=request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                messages.success(
                    request, '<b>Tebrikler kaydınız başarı ile gerçekleşti</b>', extra_tags='success')
                return HttpResponseRedirect(user.userprofile.get_user_profile_url())
    return render(request, 'auths/register.html', context={'form': form})


@anonymous_required
def user_login(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect(reverse('post-list'))
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                msg = "<b>Merhaba %s sisteme Hoşgeldiniz</b>" % (username)
                messages.success(request, msg, extra_tags='success')
                return HttpResponseRedirect(reverse('post-list'))
    return render(request, 'auths/login.html', context={'form': form})


def user_logout(request):
    username = request.user.username
    logout(request)
    msg = "<b>%s başarıyla çıkış yaptınız</b>" % (username)
    messages.success(request, msg, extra_tags="success")
    return HttpResponseRedirect(reverse('login'))


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    blog_list = Blog.objects.filter(user=user)
    takip_ediyor_mu = False
    takipci_takip_edilen = Following.get_takipci_sayisi(user)
    takipciler = takipci_takip_edilen['takipciler']
    takip_edilenler = takipci_takip_edilen['takip_edilenler']
    if user != request.user:
        takip_ediyor_mu = Following.kullanici_takip_kontrol(
            follower=request.user, followed=user)
    return render(request, 'auths/profile/user_profile.html',
                  context={'takipciler': takipciler, 'takip_edilenler': takip_edilenler, 'takip_ediyor_mu': takip_ediyor_mu,
                           'user': user, 'blog_list': blog_list, 'page': 'user-profile'})


def user_settings(request):
    bio = request.user.userprofile.bio
    sex = request.user.userprofile.sex
    profile_photo = request.user.userprofile.profile_photo
    dogum_tarihi = request.user.userprofile.born_time
    initial = {'sex': sex, 'bio': bio,
               'profile_photo': profile_photo, 'dogum_tarihi': dogum_tarihi}

    form = UserProfileUpdateForm(initial=initial, instance=request.user,
                                 data=request.POST or None, files=request.FILES or None)

    takipci_takip_edilen = Following.get_takipci_sayisi(request.user)
    takipciler = takipci_takip_edilen['takipciler']
    takip_edilenler = takipci_takip_edilen['takip_edilenler']

    if request.method == "POST":
        if form.is_valid():
            user = form.save(commit=True)
            bio = form.cleaned_data.get('bio', None)
            sex = form.cleaned_data.get('sex', None)
            profile_photo = form.cleaned_data.get('profile_photo', None)
            dogum_tarihi = form.cleaned_data.get('dogum_tarihi', None)

            user.userprofile.sex = sex
            user.userprofile.profile_photo = profile_photo
            user.userprofile.bio = bio
            user.userprofile.born_time = dogum_tarihi
            user.userprofile.save()
            messages.success(
                request, "Tebrikler kullanıcı bilgileriniz başarıyla güncellendi.", extra_tags='success')
            return HttpResponseRedirect(reverse('user-profile', kwargs={'username': user.username}))
        else:
            messages.warning(
                request, message="Lütfen verileri doğru giriniz.", extra_tags="danger")
    return render(request, 'auths/profile/settings.html',
                  context={'takipciler': takipciler, 'takip_edilenler': takip_edilenler,
                           'form': form, 'page': 'settings'})


def about_user(request, username):
    user = get_object_or_404(User, username=username)
    takip_ediyor_mu = False
    takipci_takip_edilen = Following.get_takipci_sayisi(user)
    takipciler = takipci_takip_edilen['takipciler']
    takip_edilenler = takipci_takip_edilen['takip_edilenler']
    if user != request.user:
        takip_ediyor_mu = Following.kullanici_takip_kontrol(
            follower=request.user, followed=user)
    return render(request, "auths/profile/about_me.html",
                  context={'takipciler': takipciler, 'takip_edilenler': takip_edilenler, 'takip_ediyor_mu': takip_ediyor_mu,
                           'user': user, 'page': 'about'})


def user_password_change(request):
    # form = PasswordChangeForm(user=request.user, data=request.POST or None) Manuel Oluşturduğumuz
    form = PasswordChangeForm2(user=request.user, data=request.POST or None)
    takipci_takip_edilen = Following.get_takipci_sayisi(request.user)
    takipciler = takipci_takip_edilen['takipciler']
    takip_edilenler = takipci_takip_edilen['takip_edilenler']
    if form.is_valid():
        # new_password = form.cleaned_data.get('new_password')
        # request.user.set_password(new_password)
        # request.user.save()
        # update_session_auth_hash(request, request.user)
        user = form.save(commit=True)
        update_session_auth_hash(request, user)
        messages.success(
            request, "Tebrikler şifreniz değiştirilmiştir.", extra_tags="success")
        return HttpResponseRedirect(reverse('user-profile', kwargs={'username': request.user.username}))
    return render(request, "auths/profile/change_password.html",
                  context={'takipciler': takipciler, 'takip_edilenler': takip_edilenler,
                           'form': form, 'page': 'password-change'})
