from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Category


@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    default_categories = [
        "Здоровье", "Финансы", "Карьера", "Саморазвитие",
        "Духовность", "Отдых", "Отношения", "Семья"
    ]
    for category_name in default_categories:
        Category.objects.get_or_create(name=category_name)