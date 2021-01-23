from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, Http404
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Following

# Create your views here.


def kullanici_modal_takip_et_cikar(request):
    response = sub_kullanici_takip_et_cikar(request)
    follow_type = request.GET.get('follow_type')
    owner = request.GET.get('owner')
    print(owner)
    data = response.get('data')
    # followed = response.get('followed')
    takip_edilenler = Following.takip_edilen_kullanici_adlari(
        user=request.user)
    # Following.takip_edilen_kullanici_adlari(    user=request.user)

    if request.user.username == owner:
        takipci_ve_takip_edilen = Following.get_takipci_sayisi(request.user)
        context = {'user': request.user, 'takipciler': takipci_ve_takip_edilen['takipciler'],
                   'takip_edilenler': takipci_ve_takip_edilen['takip_edilenler']}

        html_takip_sayisi = render_to_string(
            'auths/profile/include/following/following_partion.html', context=context, request=request)

        if follow_type == "takip_edilenler":
            following = Following.takip_edilen_listesi(user=request.user)
            following = followers_and_followed_paginate(
                queryset=following, page=1)
            html = render_to_string('following/profile/include/following_followed_list.html', context={
                'following': following, 'my_followeds': takip_edilenler, 'follow_type': follow_type
            }, request=request)
            html_paginate = render_to_string('following/profile/include/button_include/show_more_button.html', context={
                'username': request.user.username, 'following': following, 'follow_type': follow_type})
            data.update({'html': html, 'html_paginate': html_paginate})

        data.update({'follow_type': follow_type,
                     'html_takip_sayisi': html_takip_sayisi, 'owner': True})
    else:
        data.update({'owner': False})
    return JsonResponse(data=data)


def kullanici_takip_et_cikar(request):

    resp = sub_kullanici_takip_et_cikar(request)
    data = resp.get('data')
    followed = resp.get('followed')

    takipci_ve_takip_edilen = Following.get_takipci_sayisi(followed)
    context = {'user': followed, 'takipciler': takipci_ve_takip_edilen['takipciler'],
               'takip_edilenler': takipci_ve_takip_edilen['takip_edilenler']}

    html = render_to_string(
        'auths/profile/include/following/following_partion.html', context=context, request=request)

    data.update({'html': html})
    return JsonResponse(data=data)


def sub_kullanici_takip_et_cikar(request):
    if not request.is_ajax():
        return HttpResponseBadRequest()

    data = {'takip_durum': True, 'html': '',
            'is_valid': True, 'msg': '<b>Takibi Bırak</b>'}
    follower_username = request.GET.get('follower_username', None)
    followed_username = request.GET.get('followed_username', None)

    follower = get_object_or_404(User, username=follower_username)
    followed = get_object_or_404(User, username=followed_username)

    takip_ediyor_mu = Following.kullanici_takip_kontrol(
        follower=follower, followed=followed)

    if not takip_ediyor_mu:
        Following.kullanici_takip_et(follower=follower, followed=followed)

    else:
        Following.kullanici_takibi_birak(follower=follower, followed=followed)
        data.update({'msg': '<b>Takip Et</b>', 'takip_durum': False})

    return {'data': data, 'followed': followed}


def takipci_takip_edilen_listesi(request, follow_type):
    data = {'is_valid': True, 'html': ''}
    username = request.GET.get('username', None)
    page = request.GET.get('page', 1)
    if not username:
        raise Http404
    user = get_object_or_404(User, username=username)
    my_followeds = Following.takip_edilen_kullanici_adlari(request.user)
    if follow_type == 'takipciler':
        takipciler = Following.takipci_listesi(user)
        takipciler = followers_and_followed_paginate(
            queryset=takipciler, page=page)
        html = render_to_string('following/profile/include/following_followed_list.html',
                                context={'following': takipciler, 'my_followeds': my_followeds, 'follow_type': follow_type}, request=request)
        html_paginate = render_to_string('following/profile/include/button_include/show_more_button.html', context={
            'username': user.username, 'following': takipciler, 'follow_type': follow_type})

    elif follow_type == 'takip_edilenler':
        takip_edilenler = Following.takip_edilen_listesi(user)
        takip_edilenler = followers_and_followed_paginate(
            queryset=takip_edilenler, page=page)
        html = render_to_string('following/profile/include/following_followed_list.html',
                                context={'following': takip_edilenler, 'my_followeds': my_followeds, 'follow_type': follow_type}, request=request)
        html_paginate = render_to_string('following/profile/include/button_include/show_more_button.html', context={
            'username': user.username, 'following': takip_edilenler, 'follow_type': follow_type})
    else:
        raise Http404

    data.update({'html': html, 'html_paginate': html_paginate})

    return JsonResponse(data=data)


def followers_and_followed_paginate(queryset, page):
    paginator = Paginator(queryset, 1)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    return queryset


def kullanici_takip_et_cikar_for_post(request):
    response = sub_kullanici_takip_et_cikar(request)
    data = {'html': ''}
    takip_edilen_kullanici = response.get('followed')
    takip_durum = response.get('takip_durum')
    my_followed_users = Following.takip_edilen_kullanici_adlari(request.user)

    html = render_to_string('blog/include/favorite-include/favorite-user-obj.html',
                            context={'user': takip_edilen_kullanici, 'my_followed_users': my_followed_users}, request=request)

    data.update({'html': html})

    return JsonResponse(data=data)
