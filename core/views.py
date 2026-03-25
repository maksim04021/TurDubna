from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os
from django.http import JsonResponse
from django.db.models import Q
# Импорт моделей
from .models import News, Route, Favorite, Profile


# --- СИГНАЛЫ ДЛЯ ПРОФИЛЯ ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


# --- ГЛАВНАЯ И СПИСКИ ---
def home(request):
    news = News.objects.all().order_by('-date_pub')[:4]
    routes = Route.objects.all().order_by('-id')[:6]
    user_fav_ids = []
    if request.user.is_authenticated:
        user_fav_ids = Favorite.objects.filter(user=request.user).values_list('route_id', flat=True)
    return render(request, 'index.html', {
        'news': news,
        'routes': routes,
        'user_fav_ids': list(user_fav_ids)
    })


def all_routes(request):
    routes = Route.objects.all().order_by('-id')
    user_fav_ids = []
    if request.user.is_authenticated:
        user_fav_ids = Favorite.objects.filter(user=request.user).values_list('route_id', flat=True)
    return render(request, 'all_routes.html', {
        'routes': routes,
        'user_fav_ids': list(user_fav_ids)
    })


def all_news(request):
    news = News.objects.all().order_by('-date_pub')
    return render(request, 'all_news.html', {'news': news})


# --- ДЕТАЛЬНЫЕ СТРАНИЦЫ ---
def news_detail(request, pk):
    item = get_object_or_404(News, pk=pk)
    return render(request, 'news_detail.html', {'item': item})


def route_detail(request, pk):
    route = get_object_or_404(Route, pk=pk)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, route=route).exists()
    return render(request, 'route_detail.html', {
        'route': route,
        'is_favorite': is_favorite
    })


# --- ЛИЧНЫЙ КАБИНЕТ ---
@login_required
def profile(request):
    # 1. Безопасно получаем или создаем профиль (для аватарок)
    profile_obj, created = Profile.objects.get_or_create(user=request.user)

    # 2. Считаем ОБЩЕЕ количество маршрутов в базе данных
    total_routes_count = Route.objects.count()

    # 3. Получаем список избранного текущего пользователя
    favorites = Favorite.objects.filter(user=request.user).select_related('route').order_by('-id')
    fav_count = favorites.count()

    # 4. Рассчитываем процент прогресса
    progress_percent = 0
    if total_routes_count > 0:
        progress_percent = int((fav_count / total_routes_count) * 100)

    # 5. Передаем ВСЕ переменные в шаблон
    return render(request, 'profile.html', {
        'favorites': favorites,
        'fav_count': fav_count,
        'total_routes_count': total_routes_count,  # Тот самый счетчик
        'progress_percent': progress_percent,
    })


@login_required
def update_profile(request):
    if request.method == 'POST':
        u = request.user
        p, created = Profile.objects.get_or_create(user=u)
        u.email = request.POST.get('email', u.email)
        u.first_name = request.POST.get('first_name', u.first_name)
        u.last_name = request.POST.get('last_name', u.last_name)
        if 'avatar' in request.FILES:
            p.avatar = request.FILES['avatar']
            p.save()
        u.save()
    return redirect('profile')


# --- ИЗБРАННОЕ И КАРТА ---
@login_required
def toggle_favorite(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, route=route)
    if not created:
        fav.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})


def map_view(request):
    routes = Route.objects.all()
    return render(request, 'map.html', {'routes': routes})


def route_search(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    # Ищем маршруты по названию
    routes = Route.objects.filter(name__icontains=query)[:5]
    results = [{'id': r.id, 'name': r.name} for r in routes]
    return JsonResponse({'results': results})


# --- АВТОРИЗАЦИЯ ---

# НОВАЯ ФУНКЦИЯ ДЛЯ ВХОДА
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    return redirect('home')


@receiver(pre_save, sender=Profile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_file = sender.objects.get(pk=instance.pk).avatar
    except sender.DoesNotExist:
        return False

    new_file = instance.avatar
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)
