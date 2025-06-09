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
]