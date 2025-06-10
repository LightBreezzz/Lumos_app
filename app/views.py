from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Activity, Category, Subcategory, Goal
from .forms import ActivityForm, RegistrationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils.timezone import localtime


@login_required
def home(request):
    return render(request, 'app/index.html', {'user': request.user})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматически авторизуем пользователя
            return redirect('index')  # Перенаправляем на главную страницу
    else:
        form = RegistrationForm()
    return render(request, 'app/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Перенаправляем на главную страницу
    else:
        form = AuthenticationForm()  # Создаем пустую форму для GET-запросов

    return render(request, 'app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@csrf_exempt
def chart_data(request):
    today = datetime.now().date()
    activitys = Activity.objects.filter(
        user=request.user,
        start_time__date=today
    ).order_by('start_time')

    # Преобразование данных в формат для Chart.js
    data = []
    for activity in activitys:
        start_time = localtime(activity.start_time).strftime('%H:%M')
        end_time = localtime(activity.end_time).strftime('%H:%M')
        category_color = activity.subcategory.category.color if activity.subcategory else "#CCCCCC"  # Цвет по умолчанию
        data.append({
            'name': activity.name,
            'start_time': start_time,
            'end_time': end_time,
            'color': category_color  # Можно задавать разные цвета
        })

    return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def add_activity(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()
            return JsonResponse({
                'success': True,
                'name': activity.name,
                'start_time': activity.start_time.strftime('%H:%M'),
                'end_time': activity.end_time.strftime('%H:%M')
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def add_subcategory(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category_id')
        if name and category_id:
            category = Category.objects.get(id=category_id)
            subcategory, created = Subcategory.objects.get_or_create(name=name, category=category)
            return JsonResponse({'success': True, 'id': subcategory.id, 'name': subcategory.name})
        return JsonResponse({'success': False, 'error': 'Name and category_id are required'})


@csrf_exempt
def add_goal(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        user_id = request.POST.get('user_id')
        if name and user_id:
            user = CustomUser.objects.get(id=user_id)
            goal, created = Goal.objects.get_or_create(name=name, user=user)
            return JsonResponse({'success': True, 'id': goal.id, 'name': goal.name})
        return JsonResponse({'success': False, 'error': 'Name and user_id are required'})


@login_required
def add_activity(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user  # Привязываем действие к текущему пользователю
            activity.save()
            return redirect('index')  # Перенаправление после успешного добавления
    else:
        form = ActivityForm()
    return render(request, 'app/index.html', {'form': form})


@login_required
def index(request):
    # Получаем задачи пользователя за текущий день
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    today = datetime.now().date()
    activitys = Activity.objects.filter(
        user=request.user,
        start_time__date=today
    ).order_by('start_time')

    # Генерация данных для графика
    labels = [activity.start_time.strftime('%H:%M') for activity in activitys]
    data = [(activity.end_time - activity.start_time).seconds / 3600 for activity in activitys]

    context = {
        'categories': categories,
        'activitys': activitys,
        'subcategories': subcategories,
    }
    return render(request, 'app/index.html', context)
