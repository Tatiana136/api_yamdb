from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from datetime import datetime

MAX_LENGHT = 30
MAX_LEN = 256
MAX = 150


class UserRole:
    """Модель пользователя."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX,
        null=True,
        unique=True
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=120,
        blank=True,
        null=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX,
        blank=True,
    )
    bio = models.CharField(
        verbose_name='О себе',
        max_length=300,
        null=True,
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=20,
        choices=UserRole.CHOICES,
        default=UserRole.USER,
    )

    class Meta:

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff or self.role == UserRole.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR


class Category(models.Model):
    """Модель для категорий."""

    name = models.CharField(
        max_length=MAX_LEN,
        verbose_name='Категория',
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Идентификатор',
        unique=True
    )

    class Meta:

        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_LENGHT]


class Genre(models.Model):
    """Модель для жанров."""

    name = models.CharField(
        max_length=MAX_LEN,
        verbose_name='Жанр',
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Идентификатор',
        unique=True,
    )

    class Meta:

        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_LENGHT]


class Title(models.Model):
    """Модель для произведений."""

    name = models.CharField(
        max_length=MAX,
        verbose_name='Произведение',
    )
    year = models.PositiveIntegerField(
        verbose_name='Год издания',
        validators=[
            MinValueValidator(
                0,
                message='Значение года не может быть меньше нуля'
            ),
            MaxValueValidator(
                int(datetime.now().year),
                message='Значение года не может быть больше текущего'
            )
        ],
        db_index=True
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанр'

    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        related_name='titles',
        null=True
    )

    class Meta:

        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name')

    def __str__(self):
        return self.name[:MAX_LENGHT]


class GenreTitle(models.Model):
    """Модель жанров."""

    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    title = models.ForeignKey('Title', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    """Модель для отзывов."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        max_length=MAX_LEN,
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Aвтор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(10, 'Оценка не может быть больше 10'),
            MinValueValidator(1, 'Оценка не может быть меньше 1'),
        ]
    )

    class Meta:

        ordering = ['-pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            ),
        )

    def __str__(self):
        return self.text[:MAX_LENGHT]


class Comment(models.Model):
    """Модель для комментариев."""

    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Aвтор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:MAX_LENGHT]
