from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Category


@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    default_categories = [
        {"name": "Здоровье", "color": "#FF6384"},  # Розовый
        {"name": "Финансы", "color": "#36A2EB"},  # Синий
        {"name": "Карьера", "color": "#FFCE56"},  # Желтый
        {"name": "Саморазвитие", "color": "#4BC0C0"},  # Бирюзовый
        {"name": "Духовность", "color": "#9966FF"},  # Фиолетовый
        {"name": "Отдых", "color": "#FF9F40"},  # Оранжевый
        {"name": "Отношения", "color": "#E3ACF4"},  # Серый
        {"name": "Семья", "color": "#FFCD70"},  # Золотой
    ]
    for category_data in default_categories:
        Category.objects.get_or_create(
            name=category_data["name"],
            defaults={"color": category_data["color"]}
        )