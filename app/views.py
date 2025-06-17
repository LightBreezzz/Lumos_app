from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Activity, Category, Subcategory, Goal
from .forms import ActivityForm, RegistrationForm, GoalForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils.timezone import localtime
from django.utils.dateparse import parse_date
from django import template
from django.db.models.functions import TruncDate
from collections import defaultdict

register = template.Library()

@register.filter
def duration(td):
    if not td:
        return "0 ч"
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    if hours > 0:
        return f"{hours} ч {minutes} мин"
    return f"{minutes} мин"

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
        start_time = localtime(activity.start_time).strftime('%Y-%m-%dT%H:%M:%S')
        end_time = localtime(activity.end_time).strftime('%Y-%m-%dT%H:%M:%S')
        if activity.subcategory and activity.subcategory.category:
            category_color = activity.subcategory.category.color
        else:
            category_color = "#CCCCCC"
        
        print(f"Activity: {activity.name}, Subcategory: {getattr(activity.subcategory, 'name', 'None')}, Category Color: {category_color}")

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

            new_subcategory_name = request.POST.get('new_subcategory_name')
            category_id = request.POST.get('category')
            if new_subcategory_name and category_id:
                category = Category.objects.get(id=category_id)
                subcategory, _ = Subcategory.objects.get_or_create(
                    name=new_subcategory_name,
                    category=category,
                    user=request.user
                )
                activity.subcategory = subcategory
            else:
                activity.subcategory = form.cleaned_data.get('subcategory')

            activity.save()

            # Если AJAX — возвращаем JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'name': activity.name,
                    'start_time': activity.start_time.strftime('%H:%M') if activity.start_time else '',
                    'end_time': activity.end_time.strftime('%H:%M') if activity.end_time else ''
                })
            # Иначе — обычный редирект
            return redirect('index')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ActivityForm()
    # GET-запрос — просто рендерим страницу
    return render(request, 'app/index.html', {'form': form})


def get_categories(request):
    categories = list(Category.objects.values('id', 'name', 'color'))
    return JsonResponse(categories, safe=False)


@csrf_exempt
def add_subcategory(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category_id')
        if name and category_id:
            try:
                category = Category.objects.get(id=category_id)
                subcategory, created = Subcategory.objects.get_or_create(name=name, category=category)
                return JsonResponse({'success': True, 'id': subcategory.id, 'name': subcategory.name})
            except Category.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Category does not exist'})
        return JsonResponse({'success': False, 'error': 'Name and category_id are required'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


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
def index(request):
    # Получаем задачи пользователя за текущий день
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    today = datetime.now().date()
    activitys = Activity.objects.filter(
        user=request.user,
        start_time__date=today
    ).order_by('start_time')
    goals = Goal.objects.filter(user=request.user)
    context = {
        'categories': categories,
        'activitys': activitys,
        'subcategories': subcategories,
        'goals': goals,
    }
    return render(request, 'app/index.html', context)


@login_required
def categories_stats(request):
    categories = Category.objects.all()
    return render(request, 'app/categories_stats.html', {'categories': categories})


@login_required
@csrf_exempt
def api_categories_stats(request):
    user = request.user
    period = request.GET.get('period', 'all')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    qs = Activity.objects.filter(user=user)
    if period == 'today':
        qs = qs.filter(start_time__date=datetime.now().date())
    elif period == 'week':
        week_ago = datetime.now().date() - timedelta(days=6)
        qs = qs.filter(start_time__date__gte=week_ago)
    elif period == 'month':
        month_ago = datetime.now().date() - timedelta(days=29)
        qs = qs.filter(start_time__date__gte=month_ago)
    elif period == 'custom' and start_date and end_date:
        qs = qs.filter(start_time__date__gte=parse_date(start_date), start_time__date__lte=parse_date(end_date))
    # else: all time

    # Группируем по категориям, считаем суммарное время (в секундах)
    data = {}
    for activity in qs:
        if activity.category:
            cat = activity.category
            duration = 0
            if activity.start_time and activity.end_time:
                duration = int((activity.end_time - activity.start_time).total_seconds())
            if cat.id not in data:
                data[cat.id] = {
                    'label': cat.name,
                    'color': cat.color,
                    'value': 0
                }
            data[cat.id]['value'] += duration
    # Формируем списки для Chart.js
    labels = [v['label'] for v in data.values()]
    values = [round(v['value']/3600, 2) for v in data.values()]  # часы
    colors = [v['color'] for v in data.values()]
    ids = list(data.keys())
    return JsonResponse({'labels': labels, 'data': values, 'colors': colors, 'ids': ids})


@login_required
@csrf_exempt
def api_subcategories_stats(request):
    user = request.user
    category_id = request.GET.get('category_id')
    period = request.GET.get('period', 'all')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    qs = Activity.objects.filter(user=user, category_id=category_id)
    if period == 'today':
        qs = qs.filter(start_time__date=datetime.now().date())
    elif period == 'week':
        week_ago = datetime.now().date() - timedelta(days=6)
        qs = qs.filter(start_time__date__gte=week_ago)
    elif period == 'month':
        month_ago = datetime.now().date() - timedelta(days=29)
        qs = qs.filter(start_time__date__gte=month_ago)
    elif period == 'custom' and start_date and end_date:
        qs = qs.filter(start_time__date__gte=parse_date(start_date), start_time__date__lte=parse_date(end_date))
    # else: all time

    data = {}
    for activity in qs:
        if activity.subcategory:
            subcat = activity.subcategory
            duration = 0
            if activity.start_time and activity.end_time:
                duration = int((activity.end_time - activity.start_time).total_seconds())
            if subcat.id not in data:
                data[subcat.id] = {
                    'label': subcat.name,
                    'color': subcat.category.color,
                    'value': 0
                }
            data[subcat.id]['value'] += duration
    labels = [v['label'] for v in data.values()]
    values = [round(v['value']/3600, 2) for v in data.values()]
    colors = [v['color'] for v in data.values()]
    return JsonResponse({'labels': labels, 'data': values, 'colors': colors})


@login_required
def goals_list(request):
    goals = Goal.objects.filter(user=request.user).order_by('-created_at')
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    return render(request, 'app/goals_list.html', {
        'goals': goals,
        'categories': categories,
        'subcategories': subcategories,
    })


@login_required
def goal_create(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': goal.id})
            return redirect('goals_list')
    else:
        form = GoalForm()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'app/goal_form.html', {'form': form, 'is_edit': False})


@login_required
def goal_edit(request, pk):
    goal = Goal.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': goal.id})
            return redirect('goals_list')
    else:
        form = GoalForm(instance=goal)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'app/goal_form.html', {'form': form, 'is_edit': True, 'goal': goal})


@login_required
def goal_json(request, pk):
    try:
        goal = Goal.objects.get(pk=pk, user=request.user)
    except Goal.DoesNotExist:
        raise Http404()
    return JsonResponse({
        'category': goal.category.id if goal.category else '',
        'subcategory': goal.subcategory.id if goal.subcategory else '',
        'description': goal.description or '',
        'target_value': goal.target_value or '',
        'period': goal.period,
        'start_date': goal.start_date.isoformat() if goal.start_date else '',
        'end_date': goal.end_date.isoformat() if goal.end_date else '',
        'status': goal.status,
        'name': goal.name or '',
    })


@login_required
def api_goals_progress(request):
    user = request.user
    period = request.GET.get('range', 'month')
    goal_id = request.GET.get('goal_id')
    today = datetime.now().date()
    if period == 'week':
        start = today - timedelta(days=6)
    elif period == 'month':
        start = today - timedelta(days=29)
    else:
        start = None
    goals = Goal.objects.filter(user=user)
    if goal_id:
        goals = goals.filter(id=goal_id)
    colors = ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40", "#8BC34A", "#E91E63"]
    result = []
    for idx, goal in enumerate(goals):
        qs = goal.activities.all()
        # Определяем дату старта графика
        graph_start = None
        if start:
            graph_start = max(start, goal.start_date)
        else:
            graph_start = goal.start_date
        if graph_start:
            qs = qs.filter(start_time__date__gte=graph_start, start_time__date__lte=today)
        qs = qs.annotate(day=TruncDate('start_time')).values('day')
        day_map = defaultdict(float)
        for row in qs:
            day = row['day']
            acts = goal.activities.filter(start_time__date=day)
            for act in acts:
                if act.start_time and act.end_time:
                    day_map[day] += (act.end_time - act.start_time).total_seconds() / 3600
        days = [(graph_start + timedelta(days=i)) for i in range((today - graph_start).days + 1)] if graph_start else list(day_map.keys())
        data = [{"date": d.isoformat(), "hours": round(day_map.get(d, 0), 2)} for d in days]
        result.append({
            "goal_id": goal.id,
            "goal_name": goal.name,
            "color": colors[idx % len(colors)],
            "target": goal.target_value,
            "period": goal.period,
            "data": data
        })
    return JsonResponse(result, safe=False)
