from django.contrib import admin
from .models import News, Route

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_pub')

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    # Оставляем только те поля, которые реально есть в модели Route
    list_display = ('name',)
