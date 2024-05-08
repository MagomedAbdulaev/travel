from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import AbstractUser
from travel.settings import AUTH_USER_MODEL
from django.utils.safestring import mark_safe


class Tags(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название тега')
    location = models.ManyToManyField('Location', verbose_name='Локация для тега')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]


class Location(models.Model):
    name = models.CharField(max_length=25, verbose_name='Название локации')
    slug = models.SlugField(max_length=40, unique=True, verbose_name='Слаг локации')
    short_description = models.CharField(max_length=110, verbose_name='Краткое описание')
    image = models.ImageField(upload_to="images/%Y/%m/%d", verbose_name='Изображение локации', help_text='Маленькая картинка,когда не открыл еще страницу с локацией')
    left_description = CKEditor5Field('Описание левой части', config_name='default')
    right_description = CKEditor5Field('Описание правой части', config_name='default')
    left_image = models.ImageField(upload_to="images/%Y/%m/%d", verbose_name='Изображение для левой части')
    right_image = models.ImageField(upload_to="images/%Y/%m/%d", verbose_name='Изображение для правой части')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('travel_site:location_detail', kwargs={"location_detail_slug": self.slug})

    def clean(self):
        super().clean()
        if self.pk:  # Проверяем, что объект уже сохранен в базе данных (имеет первичный ключ)
            original = self.__class__.objects.get(pk=self.pk)  # Получаем исходный объект из базы данных
            if self.name != original.name:
                while Location.objects.filter(slug=self.slug).exists():
                    last_letter_slug = self.slug[-1]
                    try:
                        last_letter_slug_int = int(last_letter_slug)
                        last_letter_slug_int += 1
                        self.slug = self.slug[:-1] + str(last_letter_slug_int)
                    except ValueError:
                        self.slug += '2'
        else:
            while Location.objects.filter(slug=self.slug).exists():
                last_letter_slug = self.slug[-1]
                try:
                    last_letter_slug_int = int(last_letter_slug)
                    last_letter_slug_int += 1
                    self.slug = self.slug[:-1] + str(last_letter_slug_int)
                except ValueError:
                    self.slug += '2'

    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""

    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Локации"
        ordering = ["name"]


class Day(models.Model):
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, related_name="tour_day", verbose_name='Тур')
    number_day = models.PositiveSmallIntegerField(verbose_name='Номер дня')
    description = models.TextField(max_length=250, verbose_name='Описание')

    def __str__(self):
        return self.tour.name

    class Meta:
        verbose_name = "День"
        verbose_name_plural = "Дни"


class Tour(models.Model):
    name = models.CharField(max_length=25, verbose_name='Название тура')
    slug = models.SlugField(max_length=40, unique=True, verbose_name='Слаг тура')
    start_date = models.DateField(default=timezone.now, verbose_name='Дата начала тура')
    STATUSES = (
        ('Легкая', 'Легкая'),
        ('Средняя', 'Средняя'),
        ('Высокая', 'Высокая'),
    )
    TYPES = (
        ('Поход', 'Поход'),
        ('Экскурсия', 'Экскурсия'),
    )
    complexity = models.CharField(max_length=15, default='Высокая', verbose_name='Сложность тура', choices=STATUSES)
    quantity = models.PositiveSmallIntegerField(verbose_name='Количество человек в туре')
    available_seats = models.CharField(default=quantity, max_length=15, verbose_name='Количество свободных мест')
    price = models.PositiveIntegerField(verbose_name='Цена тура')
    type_tour = models.CharField(max_length=15, default='Поход', verbose_name='Тип тура', choices=TYPES)
    short_description = models.CharField(max_length=100, verbose_name='Краткое описание')
    description = CKEditor5Field('Описание тура', config_name='default')
    location = models.ForeignKey('Location', on_delete=models.CASCADE, verbose_name='Локация для тура')

    def get_absolute_url(self):
        return reverse('travel_site:tour_detail', kwargs={"tour_detail_slug": self.slug})

    def __str__(self):
        return f'{self.name} с {self.start_date}'

    def clean(self):
        super().clean()
        if self.pk:  # Проверяем, что объект уже сохранен в базе данных (имеет первичный ключ)
            original = self.__class__.objects.get(pk=self.pk)  # Получаем исходный объект из базы данных
            if self.name != original.name:
                while Tour.objects.filter(slug=self.slug).exists():
                    last_letter_slug = self.slug[-1]
                    try:
                        last_letter_slug_int = int(last_letter_slug)
                        last_letter_slug_int += 1
                        self.slug = self.slug[:-1] + str(last_letter_slug_int)
                    except ValueError:
                        self.slug += '2'
        else:
            while Tour.objects.filter(slug=self.slug).exists():
                last_letter_slug = self.slug[-1]
                try:
                    last_letter_slug_int = int(last_letter_slug)
                    last_letter_slug_int += 1
                    self.slug = self.slug[:-1] + str(last_letter_slug_int)
                except ValueError:
                    self.slug += '2'

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"
        ordering = ["name"]


class Blog(models.Model):
    name = models.CharField(max_length=55, verbose_name='Название блога')
    slug = models.SlugField(max_length=75, unique=True, verbose_name='Слаг блога')
    short_description = models.TextField(max_length=250, verbose_name='Краткое описание блога')
    image = models.ImageField(upload_to="images/%Y/%m/%d", verbose_name='Изображение блога')
    description = CKEditor5Field('Описание блога', config_name='extends')
    author = models.CharField(max_length=50, verbose_name='Имя и фамилия автора')
    role = models.CharField(max_length=30, blank=True, help_text='Например: Путешественник', verbose_name='Занятие по жизни автора')
    experience = models.CharField(max_length=30, blank=True, help_text='Например: Опыт в горах 8 лет или что-то такое', verbose_name='Опыт автора')
    telegram = models.CharField(max_length=70, default='https://t.me/', blank=True, verbose_name='Ссылка на телеграм')
    vkontakte = models.CharField(max_length=70, default='https://vk.com/', blank=True, verbose_name='Ссылка на ВК')
    created_at = models.DateField(default=timezone.now, verbose_name='Дата создания')

    def __str__(self):
        return f'{self.name}'

    def clean(self):
        super().clean()
        if self.pk:  # Проверяем, что объект уже сохранен в базе данных (имеет первичный ключ)
            original = self.__class__.objects.get(pk=self.pk)  # Получаем исходный объект из базы данных
            if self.name != original.name:
                while Tour.objects.filter(slug=self.slug).exists():
                    last_letter_slug = self.slug[-1]
                    try:
                        last_letter_slug_int = int(last_letter_slug)
                        last_letter_slug_int += 1
                        self.slug = self.slug[:-1] + str(last_letter_slug_int)
                    except ValueError:
                        self.slug += '2'
        else:
            while Tour.objects.filter(slug=self.slug).exists():
                last_letter_slug = self.slug[-1]
                try:
                    last_letter_slug_int = int(last_letter_slug)
                    last_letter_slug_int += 1
                    self.slug = self.slug[:-1] + str(last_letter_slug_int)
                except ValueError:
                    self.slug += '2'

    def get_absolute_url(self):
        return reverse('travel_site:blog_detail', kwargs={"blog_detail_slug": self.slug})

    class Meta:
        verbose_name = "Блог"
        verbose_name_plural = "Блоги"
        ordering = ["name"]


class ProductRent(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название продукта')
    short_description = models.CharField(max_length=50, verbose_name='Краткое описание продукта')
    image = models.ImageField(upload_to="images/%Y/%m/%d", verbose_name='Изображение продукта')
    price = models.PositiveIntegerField(verbose_name='Цена продукта')
    light = models.BooleanField(default=False, verbose_name='Этот продукт входит в набор light')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Продукт в прокат"
        verbose_name_plural = "Продукты в прокат"
        ordering = ["name"]


class Feedback(models.Model):
    name = models.CharField(max_length=40, blank=True, verbose_name='Название отзыва')
    description = models.TextField(max_length=600, verbose_name='Описание отзыва')
    is_displayed = models.BooleanField(default=True, verbose_name="Отображается ли отзыв")

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["name"]


class Question(models.Model):
    name = models.CharField(max_length=80, verbose_name='Вопрос')
    description = models.TextField(max_length=1000, verbose_name='Описание вопроса')
    is_displayed = models.BooleanField(default=True, verbose_name="Отображается ли вопрос")

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["name"]


class Slide(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название слайда')
    image = models.ImageField(upload_to="images/%Y/%m/%d", verbose_name="Изображение слайда")
    is_displayed = models.BooleanField(default=True, verbose_name="Отображается ли слайд")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Слайд на странице 'Я еду с группой'"
        verbose_name_plural = "Слайды на странице 'Я еду с группой'"
        ordering = ['name']


class Person(models.Model):
    name = models.CharField(max_length=30, verbose_name='Имя участника')
    surname = models.CharField(max_length=30, verbose_name='Фамилия участника')
    role = models.CharField(max_length=30, blank=True, help_text='Например: Путешественник',
                            verbose_name='Должность участника')
    experience = models.CharField(max_length=30, blank=True, help_text='Например: Опыт в горах 8 лет или что-то такое',
                                  verbose_name='Опыт участника')
    description = models.TextField(max_length=1500, verbose_name='О гиде')
    image = models.ImageField(upload_to="images/%Y/%m/%d", verbose_name='Фото')

    def __str__(self):
        return self.name + " " + self.surname + " " + self.role

    class Meta:
        verbose_name = "Гид"
        verbose_name_plural = "Гиды"
        ordering = ['name']


class User(AbstractUser):
    phone = models.CharField(max_length=12, unique=True, verbose_name="Номер телефона")
    email = models.EmailField(max_length=80, unique=True, verbose_name="Почта")
    date_birth = models.DateField(verbose_name="Дата рождения", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.username:  # Проверяем, что username пустой
            self.username = str(self.phone)  # Устанавливаем username равным значению phone
        super().save(*args, **kwargs)  # Вызываем метод save() родительского класса


class Order(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, verbose_name="Пользователь:", blank=True, null=True, default=None)
    phone = models.CharField(max_length=12, verbose_name="Номер телефона", blank=True)
    email = models.EmailField(max_length=80, verbose_name="Почта", blank=True)
    date_birth = models.DateField(verbose_name="Дата рождения", blank=True, null=True)
    name = models.CharField(max_length=60, verbose_name="Имя фамилия", blank=True)
    date_created = models.DateTimeField(default=timezone.now, verbose_name="Дата проведения заказа")
    STATUSES = (
        (0, 'Создан'),
        (1, 'Оплачено'),
    )
    status = models.PositiveSmallIntegerField(default=0, verbose_name="Статус заказа:", choices=STATUSES)
    cart = models.JSONField(default=dict, verbose_name="Товары добавленные в заказ")
    price = models.CharField(default=0, max_length=20, verbose_name="Цена заказа(цена корзины)")
    products = models.TextField(default='', max_length=1000, verbose_name="Продукты")

    def __str__(self):
        return f'Заказ номер {self.id}, {self.name}, цена:{self.price}'

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-date_created"]
