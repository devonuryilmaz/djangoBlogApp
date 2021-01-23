from django.shortcuts import render, HttpResponse, Http404, get_object_or_404, reverse, redirect, HttpResponseRedirect
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from .models import Blog, FavoriteBlog, NewComment
from .forms import iletisimForm, blogForm, PostSorguForm, YorumForm
from .decorators import is_post
from following.models import Following


@login_required
def post_list(request):
    # if not request.user.is_authenticated:
    #     msg = '<b>Lütfen giriş yapınız!</strong>'
    #     messages.warning(request, msg, extra_tags='warning')
    #     return HttpResponseRedirect(reverse('login'))
    # posts = Blog.objects.all().order_by('-id')
    posts = Blog.objects.all()
    page = request.GET.get('page', 1)
    form = PostSorguForm(data=request.GET or None)
    if form.is_valid():
        taslak_yayin = form.cleaned_data.get('taslak_yayin', None)
        search = form.cleaned_data.get('search')
        if search:
            posts = posts.filter(
                Q(icerik__icontains=search) | Q(title__icontains=search) | Q(kategoriler__isim__icontains=search)).distinct()
        if taslak_yayin and taslak_yayin != 'hepsi':
            posts = posts.filter(yayin_taslak=taslak_yayin)
            #posts = Blog.get_taslak_or_yayin(taslak_yayin)

    paginator = Paginator(posts, per_page=3)
    try:
        posts = paginator.page(page)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)

    context = {'posts': posts, 'form': form}
    return render(request, 'blog/post-list.html', context=context)


@login_required(login_url=reverse_lazy('login'))
def post_update(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if request.user != blog.user:
        return HttpResponseForbidden()
    form = blogForm(instance=blog, data=request.POST or None,
                    files=request.FILES or None)
    context = {'form': form, 'blog': blog}
    if form.is_valid():
        form.save()
        msg = '<strong> %s </strong> isimli gönderi başarı ile güncellendi.' % (
            blog.title)
        messages.success(request, msg, extra_tags='warning')
        return HttpResponseRedirect(blog.get_absolute_url())
    return render(request, 'blog/post-update.html', context=context)


@login_required(login_url=reverse_lazy('login'))
def post_delete(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if request.user != blog.user:
        return HttpResponseForbidden()
    blog.delete()
    msg = '<strong> %s </strong> isimli gönderi başarı ile silindi.' % (
        blog.title)
    messages.success(request, msg, extra_tags='danger')
    return HttpResponseRedirect(reverse('post-list'))


@login_required(login_url=reverse_lazy('login'))
def post_add(request):
    # if not request.user.is_authenticated:
    #     msg = '<b>Lütfen giriş yapınız!</strong>'
    #     messages.warning(request, msg, extra_tags='warning')
    #     return HttpResponseRedirect(reverse('login'))
    form = blogForm()
    if request.method == 'POST':
        form = blogForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.user = request.user
            blog.save()
            msg = 'Tebrikler <strong> %s </strong> isimli gönderi başarı ile oluşturuldu.' % (
                blog.title)
            messages.success(request, msg, extra_tags='success')
            # reverse('post-detail',kwargs={'pk': blog.pk})
            return HttpResponseRedirect(blog.get_absolute_url())
    return render(request, 'blog/post-create.html', context={'form': form})


@login_required(login_url=reverse_lazy('login'))
def post_detail(request, slug):
    # try:
    #     blog = Blog.objects.get(pk=pk)
    # except Blog.DoesNotExist:
    #     raise Http404
    form = YorumForm()
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, 'blog/post-detail.html', context={'blog': blog, 'form': form})


@login_required(login_url=reverse_lazy('login'))
@is_post
def add_comment(request, slug):
    if request.method == "GET":
        return HttpResponseBadRequest()
    blog = get_object_or_404(Blog, slug=slug)
    form = YorumForm(data=request.POST)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.blog = blog
        new_comment.user = request.user
        new_comment.save()
        messages.success(request, 'Tebrikler yorumunuz gönderildi.')
        return HttpResponseRedirect(blog.get_absolute_url())


def new_add_comment(request, pk, model_type):
    data = {'is_valid': True, 'blog_comment_html': '', 'model_type': model_type}
    nesne = None
    all_comment = None
    form = YorumForm(data=request.POST)

    if model_type == 'blog':
        nesne = get_object_or_404(Blog, pk=pk)
    elif model_type == 'comment':
        nesne = get_object_or_404(NewComment, pk=pk)
    else:
        raise Http404

    if form.is_valid():
        icerik = form.cleaned_data.get('icerik')
        NewComment.add_comment(nesne, model_type, request.user, icerik)

    if model_type == 'comment':
        nesne = nesne.content_obj

    comment_html = render_to_string('blog/include/comment/comment-list-partial.html', context={
        'blog': nesne
    })
    data.update({'blog_comment_html': comment_html})

    return JsonResponse(data=data)


def get_child_comment_form(request):
    data = {'form_html': ''}
    pk = request.GET.get('comment_pk')
    comment = get_object_or_404(NewComment, pk=pk)
    form = YorumForm()
    form_html = render_to_string('blog/include/comment/child-comment-form.html', context={
        'form': form, 'comment': comment
    }, request=request)

    data.update({'form_html': form_html})

    return JsonResponse(data)


@login_required(login_url=reverse_lazy('login'))
def add_or_remove_favorite(request, slug):
    data = {'status': 'deleted', 'count': 0}
    blog = get_object_or_404(Blog, slug=slug)
    favori_blog = FavoriteBlog.objects.filter(blog=blog, user=request.user)

    if favori_blog.exists():
        favori_blog.delete()
    else:
        favori_blog.create(blog=blog, user=request.user)
        data.update({'status': 'added'})

    count = blog.get_favorite_count()
    data.update({'count': count})

    return post_detail(request, slug)


@login_required(login_url=reverse_lazy('login'))
def post_list_favorite_user(request, slug):
    page = request.GET.get('page', 1)
    blog = get_object_or_404(Blog, slug=slug)
    users = blog.get_added_favorite_users_object()
    my_followed_users = Following.takip_edilen_kullanici_adlari(
        user=request.user)
    paginator = Paginator(users, 1)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    html = render_to_string('blog/include/favorite-include/favorite-user-list.html',
                            context={'users': users, 'my_followed_users': my_followed_users}, request=request)

    page_html = render_to_string('blog/include/favorite-include/buttons/show_more_button.html',
                                 context={'post': blog, 'users': users}, request=request)

    return JsonResponse(data={'html': html, 'page_html': page_html})
