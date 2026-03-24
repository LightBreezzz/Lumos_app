from django.contrib import admin
from .models import (
    CustomUser,
    Habit,
    Goal,
    Activity,
    Category,
    Subcategory,
    Achievement,
    Community,
    CommunityMember,
    Post,
    Notification
)

# Регистрация всех моделей
admin.site.register(CustomUser)
admin.site.register(Habit)
admin.site.register(Goal)
admin.site.register(Activity)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Achievement)
admin.site.register(Community)
admin.site.register(CommunityMember)
admin.site.register(Post)
admin.site.register(Notification)