from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views  # Импортируем вьюхи напрямую из папки core

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('map/', views.map_view, name='map_view'),
    path('route_search/', views.route_search, name='route_search'),
    # Теперь прописываем пути напрямую, так как файла core/urls.py нет
    path('', views.home, name='home'),
    path('news/', views.all_news, name='all_news'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('routes/', views.all_routes, name='all_routes'),
    path('routes/<int:pk>/', views.route_detail, name='route_detail'),
    path('profile/', views.profile, name='profile'),
    path('map/', views.map_view, name='map_view'),
    path('toggle_favorite/<int:route_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]

# Раздача картинок
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
