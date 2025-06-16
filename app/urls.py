from django.urls import path
from . import views
# from django.contrib.auth.views import LogoutView


urlpatterns = [
    path("", views.index, name="index"),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/chart-data/', views.chart_data, name='chart_data'),
    path('add-activity/', views.add_activity, name='add_activity'),
    path('api/categories/', views.get_categories, name='get_categories'),
    path('add_subcategory/', views.add_subcategory, name='add_subcategory'),
    path('add_goal/', views.add_goal, name='add_goal'),
    path('categories/', views.categories_stats, name='categories_stats'),
    path('api/categories-stats/', views.api_categories_stats, name='api_categories_stats'),
    path('api/subcategories-stats/', views.api_subcategories_stats, name='api_subcategories_stats'),
    path('goals/', views.goals_list, name='goals_list'),
    path('goals/add/', views.goal_create, name='goal_create'),
    path('goals/<int:pk>/edit/', views.goal_edit, name='goal_edit'),
    path('goals/<int:pk>/json/', views.goal_json, name='goal_json'),
    path('api/goals-progress/', views.api_goals_progress, name='api_goals_progress'),
]