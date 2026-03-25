from django.db import models
from django.contrib.auth.models import User


class News(models.Model):
    # Категории для пометок на карточках
    CATEGORY_CHOICES = [
        ('news', 'Новости'),
        ('event', 'Афиша'),
        ('party', 'Мероприятие'),
        ('info', 'Инфо'),
    ]

    title = models.CharField('Заголовок', max_length=200)
    location = models.CharField('Место проведения', max_length=255, default='Дубна, Россия')
    # Новое поле для категорий (пометки на карточках)
    category = models.CharField(
        'Категория',
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='news'
    )
    text = models.TextField('Текст новости')
    date_pub = models.DateTimeField('Дата', auto_now_add=True)
    image = models.ImageField('Картинка', upload_to='news/', blank=True)

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"


class Route(models.Model):
    name = models.CharField('Название маршрута', max_length=200)
    image = models.ImageField('Обложка', upload_to='routes/', blank=True)
    description = models.TextField('Описание')
    steps = models.TextField('Этапы (с новой строки)')
    # НОВЫЕ ПОЛЯ ДЛЯ КАРТЫ (центр Дубны по умолчанию)
    lat = models.FloatField('Широта', default=56.7320)
    lon = models.FloatField('Долгота', default=37.1670)

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты'

    def get_steps_list(self):
        return [step.strip() for step in self.steps.split('\n') if step.strip()]

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'route')  # Защита от дублей в избранном
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f"{self.user.username} -> {self.route.name}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField('Аватарка', upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Профиль {self.user.username}"