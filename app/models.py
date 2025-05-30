from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    phone = models.CharField(
        ("Телефон"),
        max_length=20,
        blank=True,
        null=True,
        help_text="Номер телефона пользователя"
    )
    avatar = models.ImageField(
        ("Аватар"),
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="Изображение аватара пользователя"
    )
    telegram_id = models.CharField(
        ("Telegram ID"),
        max_length=255,
        blank=True,
        null=True,
        help_text="ID пользователя в Telegram"
    )
    created_at = models.DateTimeField(
        ("Дата создания"),
        auto_now_add=True,
        help_text="Дата и время создания пользователя"
    )
    update_at = models.DateTimeField(
        ("Дата обновления"),
        auto_now=True,
        help_text="Дата и время последнего обновления пользователя"
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
    
    def __str__(self):
        return self.username
    

class Activities(models.Model):
    user = models.ForeignKey(
        "CustomUser",
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name=("Пользователь")
    )
    subcategory = models.ForeignKey(
        "SubCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
        verbose_name=("Подкаталог")
    )
    habit = models.ForeignKey(
        "Habit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
        verbose_name=("Привычка")
    )
    goal = models.ForeignKey(
        "Goals",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
        verbose_name=("Цель")
    )
    description = models.TextField(
        ("Описание"),
        blank=True,
        null=True,
        help_text="Текстовое описание действий"
    )
    timestamp = models.DateTimeField(
        ("Время действий"),
        help_text="Дата и время выполнения действия"
    )
    duration = models.PositiveBigIntegerField(
        ("Продолжительность"),
        blank=True,
        null=True,
        help_text="Продолжительность действия в минутах"
    )
    value = models.FloatField(
        ("Значение"),
        blank=True,
        null=True,
        help_text="Числовое значение, связанное с действием"
    )
    created_at = models.DateTimeField(
        ("Дата создания"),
        auto_now_add=True,
        help_text="Дата и время создания пользователя"
    )
    update_at = models.DateTimeField(
        ("Дата обновления"),
        auto_now=True,
        help_text="Дата и время последнего обновления пользователя"
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
    
    def __str__(self):
        return self.username
