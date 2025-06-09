from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


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
    
    def clean(self):
        # Проверка уникальности email и телефона
        if CustomUser.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError("Пользователь с такой почтой уже существует.")
        if CustomUser.objects.filter(phone=self.phone).exclude(pk=self.pk).exists():
            raise ValidationError("Пользователь с таким номером телефона уже существует.")
    

class Community(models.Model):
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="communities",
        verbose_name=_("Создано пользователем")
    )

    # Основные поля сообщества
    name = models.CharField(
        max_length=255,
        verbose_name=_("Название сообщества")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Описание сообщества")
    )

    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Сообщество")
        verbose_name_plural = _("Сообщества")
        ordering = ["name"]  # Сортировка по названию

    def __str__(self):
        return self.name


class CommunityMember(models.Model):
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name=_("Сообщество")
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="community_memberships",
        verbose_name=_("Пользователь")
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата присоединения"),
        help_text=_("Дата и время, когда пользователь присоединился к сообществу")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Членство в сообществе")
        verbose_name_plural = _("Членства в сообществах")
        unique_together = ('community', 'user')  # Гарантирует уникальность пары (сообщество, пользователь)

    def __str__(self):
        return f"{self.user.username} в {self.community.name}"
    

class Post(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Пользователь")
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Сообщество")
    )

    # Основные поля поста
    content = models.TextField(
        verbose_name=_("Содержание поста"),
        help_text=_("Текстовое содержание поста")
    )

    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Пост")
        verbose_name_plural = _("Посты")
        ordering = ["-created_at"]  # Сортировка по дате создания (от новых к старым)

    def __str__(self):
        return f"Пост от {self.user.username} в {self.community.name}"
    

class Notification(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Пользователь")
    )

    # Основные поля уведомления
    message = models.TextField(
        verbose_name=_("Сообщение"),
        help_text=_("Текст уведомления")
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_("Прочитано"),
        help_text=_("Флаг, указывающий, было ли уведомление прочитано")
    )

    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Уведомление")
        verbose_name_plural = _("Уведомления")
        ordering = ["-created_at"]  # Сортировка по дате создания (от новых к старым)

    def __str__(self):
        return f"Уведомление для {self.user.username}: {self.message[:50]}"

    def mark_as_read(self):
        """
        Метод для отметки уведомления как прочитанного.
        """
        self.is_read = True
        self.save()

    def mark_as_unread(self):
        """
        Метод для отметки уведомления как непрочитанного.
        """
        self.is_read = False
        self.save()


CATEGORY_CHOICES = [
    ('Health', 'Здоровье'),
    ('Finance', 'Финансы'),
    ('Career', 'Карьера'),
    ('Self-development', 'Саморазвитие'),
    ('Spirituality', 'Духовность'),
    ('Reset', 'Отдых'),
    ('Relationship', 'Отношения'),
    ('Family', 'Семья'),
]


class Category(models.Model):
    name = models.CharField(
        max_length=255,
        choices=CATEGORY_CHOICES,
        unique=True,
        verbose_name=_("Название категории")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Описание категории")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ["name"]  # Сортировка по названию

    def __str__(self):
        return self.name
    

class Subcategory(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name=_("Категория")
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name=_("Пользователь")
    )

    # Основные поля подкатегории
    name = models.CharField(
        max_length=255,
        verbose_name=_("Название подкатегории")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Описание подкатегории")
    )

    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Подкатегория")
        verbose_name_plural = _("Подкатегории")
        ordering = ["name"]  # Сортировка по названию

    def __str__(self):
        return self.name


class Achievement(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="achievements",
        verbose_name=_("Пользователь")
    )

    # Основные поля достижения
    name = models.CharField(
        max_length=255,
        verbose_name=_("Название достижения")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Описание достижения")
    )
    unlocked_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Дата разблокировки"),
        help_text=_("Дата и время, когда достижение было получено")
    )

    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Достижение")
        verbose_name_plural = _("Достижения")
        ordering = ["-unlocked_at"]  # Сортировка по дате разблокировки

    def __str__(self):
        return self.name


class Goal(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="goals",
        verbose_name=_("Пользователь")
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="goals",
        verbose_name=_("Категория")
    )

    # Связь с подкатегорией (Subcategory)
    subcategory = models.ForeignKey(
        Subcategory,  # Предполагается, что у вас есть модель Subcategory
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="goals",
        verbose_name=_("Подкатегория")
    )

    # Связь с достижением (Achievement)
    achievement = models.ForeignKey(
        Achievement,  # Предполагается, что у вас есть модель Achievement
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="goals",
        verbose_name=_("Достижение")
    )

    # Основные поля цели
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Описание цели")
    )
    target_value = models.FloatField(
        verbose_name=_("Целевое значение"),
        help_text=_("Количество повторений, сумма денег или время выполнения")
    )
    start_date = models.DateField(
        verbose_name=_("Дата начала"),
        help_text=_("Дата начала выполнения цели")
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Дата окончания"),
        help_text=_("Дата завершения выполнения цели")
    )
    status = models.CharField(
        max_length=50,
        default="active",
        choices=[
            ("active", _("Активна")),
            ("completed", _("Завершена")),
            ("paused", _("Приостановлена")),
            ("failed", _("Не выполнена"))
        ],
        verbose_name=_("Статус цели")
    )

    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Цель")
        verbose_name_plural = _("Цели")
        ordering = ["-created_at"]  # Сортировка по дате создания

    def __str__(self):
        return f"{self.description} ({self.status})"


class Activity(models.Model):
    name = models.CharField(
        max_length=255,
        null=True,
        verbose_name=_("Название действия")
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name=_("Пользователь")
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="activities",
        verbose_name=_("Категория")
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
        verbose_name=_("Подкатегория")
    )
    goal = models.ForeignKey(
        Goal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
        verbose_name=_("Цель")
    )
    description = models.TextField(
        _("Описание"),
        blank=True,
        null=True,
        help_text=_("Текстовое описание действий")
    )
    value = models.FloatField(
        _("Значение"),
        blank=True,
        null=True,
        help_text=_("Числовое значение, связанное с действием")
    )
    start_time = models.DateTimeField(
        null=True,
        blank=True,
    )  # Новое поле
    end_time = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("Дата обновления"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Действие")
        verbose_name_plural = _("Действия")
        ordering = ["start_time"]  # Сортировка по времени действия (от новых к старым)

    def __str__(self):
        return f"{self.user.username} - {self.description[:50]}" if self.description else f"{self.user.username}"


class Habit(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name=("Пользователь")
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="habits",
        verbose_name=("Подкатегория")
    )
    activiti = models.ManyToManyField(
        Activity,
        related_name="habits",
        verbose_name="Связанные привычки"
    )
    goal = models.ForeignKey(
        Goal,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="habits",
        verbose_name=("Цель")
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="habits",
        verbose_name=("Достижение")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=("Название привычки")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=("Описание привычки")
    )
    frequency = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=("Частота выполнения"),
        help_text=("Ежедневно, раз в неделю и т.д.")
    )
    target_value = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_("Целевое значение"),
        help_text=_("Например: количество повторений или время выполнения")
    )
    start_date = models.DateField(
        verbose_name=_("Дата начала"),
        help_text=_("Дата начала выполнения привычки")
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Дата окончания"),
        help_text=_("Дата завершения выполнения привычки")
    )
    status = models.CharField(
        max_length=50,
        default="active",
        choices=[
            ("active", _("Активна")),
            ("completed", _("Завершена")),
            ("paused", _("Приостановлена")),
            ("failed", _("Не выполнена"))
        ],
        verbose_name=_("Статус привычки")
    )

    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Привычка")
        verbose_name_plural = _("Привычки")
        ordering = ["-created_at"]  # Сортировка по дате создания

    def __str__(self):
        return self.name


