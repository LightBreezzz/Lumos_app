document.addEventListener('DOMContentLoaded', function () {
    // Получаем элементы модального окна
    const modal = document.getElementById('addActivityModal');
    const openModalBtn = document.getElementById('openModalBtn');
    const closeBtn = document.querySelector('.close-btn');
    const categorySelect = document.getElementById('category');

    // Форма для добавления активности
    const activityForm = document.getElementById('activityForm');    

    // Поля для добавления новых подкатегорий и целей
    const newSubcategoryInput = document.getElementById('newSubcategory');
    const newGoalInput = document.getElementById('newGoal');

    // Goal modal logic
    const goalModal = document.getElementById('goalModal');
    const addGoalBtn = document.getElementById('addGoalBtn');
    const closeGoalBtn = document.querySelector('.close-goal-btn');
    const goalForm = document.getElementById('goalForm');
    const goalModalTitle = document.getElementById('goalModalTitle');
    const goalPeriod = document.getElementById('goal_period');
    const goalHours = document.getElementById('goal_hours');
    const goalMinutes = document.getElementById('goal_minutes');
    const goalTargetValue = document.getElementById('goal_target_value');
    const goalName = document.getElementById('goal_name');

    // --- График целей ---
    const goalsLineChartCanvas = document.getElementById('goalsLineChart');
    const goalsRangeSelect = document.getElementById('goalsRangeSelect');
    let goalsLineChartInstance = null;

    function fetchAndRenderGoalsChart() {
        if (!goalsLineChartCanvas) return;
        const range = goalsRangeSelect ? goalsRangeSelect.value : 'month';
        fetch(`/api/goals-progress/?range=${range}`)
            .then(r => r.json())
            .then(data => {
                const labels = data.length ? data[0].data.map(d => d.date) : [];
                const datasets = data.map(goal => ({
                    label: goal.goal_name,
                    data: goal.data.map(d => d.hours),
                    borderColor: goal.color,
                    backgroundColor: goal.color + '33',
                    fill: false,
                    tension: 0.2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    borderWidth: 2,
                    hidden: false,
                }));
                // Добавляем горизонтальную линию-таргет для каждой цели
                const targetLines = data.map(goal => ({
                    label: `Таргет: ${goal.goal_name}`,
                    data: Array(labels.length).fill(goal.target),
                    borderColor: goal.color,
                    borderDash: [6, 6],
                    pointRadius: 0,
                    borderWidth: 1,
                    fill: false,
                    hidden: true,
                }));
                if (goalsLineChartInstance) goalsLineChartInstance.destroy();
                goalsLineChartInstance = new Chart(goalsLineChartCanvas, {
                    type: 'line',
                    data: { labels, datasets: [...datasets, ...targetLines] },
                    options: {
                        plugins: {
                            legend: { display: true, position: 'bottom' },
                            tooltip: {
                                callbacks: {
                                    label: function(ctx) {
                                        return ctx.dataset.label + ': ' + formatHours(ctx.parsed.y);
                                    }
                                }
                            }
                        },
                        scales: {
                            x: { title: { display: true, text: 'Дата' } },
                            y: {
                                title: { display: true, text: 'Часы' },
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1,
                                    callback: function(val) { return val; }
                                },
                                grid: { drawTicks: true, color: '#eee' }
                            }
                        }
                    }
                });
            });
    }
    if (goalsLineChartCanvas) {
        fetchAndRenderGoalsChart();
        if (goalsRangeSelect) {
            goalsRangeSelect.addEventListener('change', fetchAndRenderGoalsChart);
        }
    }
    // --- Конец графика целей ---

    // Открываем модальное окно
    if (openModalBtn && modal) {
        openModalBtn.addEventListener('click', function () {
            modal.style.display = 'flex';
        });
    }

    // Закрываем модальное окно
    if (closeBtn && modal) {
        closeBtn.addEventListener('click', function () {
            modal.style.display = 'none';
        });
    }

    // Закрываем модальное окно при клике вне его области
    if (modal) {
        window.addEventListener('click', function (event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    // Добавление новой категории
    function loadCategories() {
        fetch('/api/categories/') // Убедитесь, что этот URL существует
            .then(response => response.json())
            .then(categories => {
                categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category.id;
                    option.text = category.name;
                    option.style.backgroundColor = category.color; // Добавляем цвет
                    categorySelect.appendChild(option);
                });
            })
            .catch(error => console.error('Ошибка загрузки категорий:', error));
    }
    
    // Добавление новой подкатегории
    if (newSubcategoryInput) {
        newSubcategoryInput.addEventListener('blur', function () {
            const subcategoryName = newSubcategoryInput.value.trim();
            const categorySelect = document.getElementById('category');
            const categoryId = categorySelect ? categorySelect.value : null;

            if (subcategoryName && categoryId) {
                fetch('/add_subcategory/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: `name=${encodeURIComponent(subcategoryName)}&category_id=${categoryId}`,
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const subcategorySelect = document.getElementById('subcategory');
                        const option = document.createElement('option');
                        option.value = data.id;
                        option.text = data.name;
                        subcategorySelect.appendChild(option);
                        subcategorySelect.value = data.id; // Выбираем новую подкатегорию
                    }
                });
            }
        });
    }

    // Добавление новой цели
    if (newGoalInput) {
        newGoalInput.addEventListener('blur', function () {
            const goalName = newGoalInput.value.trim();
            const userId = document.body.dataset.userId; // Передаем ID текущего пользователя из Django

            if (goalName && userId) {
                fetch('/add_goal/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: `name=${encodeURIComponent(goalName)}&user_id=${userId}`,
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const goalSelect = document.getElementById('goal');
                        const option = document.createElement('option');
                        option.value = data.id;
                        option.text = data.name;
                        goalSelect.appendChild(option);
                        goalSelect.value = data.id; // Выбираем новую цель
                    }
                });
            }
        });
    }

    // Обработка отправки формы для добавления активности
    if (activityForm) {
        activityForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(activityForm);
            
            // Добавляем новую подкатегорию, если она введена
            const newSubcategory = document.getElementById('newSubcategory') ? document.getElementById('newSubcategory').value : '';
            if (newSubcategory) {
                formData.append('new_subcategory_name', newSubcategory);
            }

            fetch('/add-activity/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Добавляем новое действие в список
                    const activityList = document.querySelector('.task-list ul');
                    const newItem = document.createElement('li');
                    newItem.className = 'task-item';
                    newItem.innerHTML = `
                        <h3>${data.name}</h3>
                        <span class="time-range">${data.start_time} - ${data.end_time}</span>
                    `;
                    activityList.appendChild(newItem);

                    // Закрываем модальное окно
                    if (modal) modal.style.display = 'none';

                    // Очищаем форму
                    activityForm.reset();

                    // Обновляем график, если функция есть
                    if (typeof renderTimeline === 'function') {
                        renderTimeline();
                    }
                } else {
                    alert('Ошибка при добавлении активности.');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
        });
    }

    // Фильтрация подкатегорий по выбранной категории
    if (categorySelect) {
        categorySelect.addEventListener('change', function () {
            const selectedCategoryId = this.value;
            const subcategorySelect = document.getElementById('subcategory');
            if (!subcategorySelect) return;
            Array.from(subcategorySelect.options).forEach(option => {
                if (!option.value) {
                    option.style.display = '';
                    return;
                }
                if (option.getAttribute('data-category') === selectedCategoryId) {
                    option.style.display = '';
                } else {
                    option.style.display = 'none';
                }
            });
            // Сбросить выбранную подкатегорию, если она не подходит
            subcategorySelect.value = '';
        });
    }

    // Функция для получения CSRF-токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    if (addGoalBtn && goalModal) {
        addGoalBtn.addEventListener('click', function (e) {
            e.preventDefault();
            goalModalTitle.textContent = 'Создать цель';
            goalForm.reset();
            goalModal.style.display = 'flex';
            goalForm.dataset.editing = '';
        });
    }
    if (closeGoalBtn && goalModal) {
        closeGoalBtn.addEventListener('click', function () {
            goalModal.style.display = 'none';
        });
    }
    window.addEventListener('click', function (event) {
        if (event.target === goalModal) {
            goalModal.style.display = 'none';
        }
    });

    // Edit goal buttons
    document.querySelectorAll('.goal-item').forEach(function(item) {
        item.addEventListener('click', function(e) {
            // Не срабатывает, если клик по ✏️
            if (e.target.classList.contains('btn-edit-goal')) return;
            const goalId = item.dataset.goalId;
            fetch(`/goals/${goalId}/json/`)
                .then(response => response.json())
                .then(data => {
                    goalModalTitle.textContent = 'Редактировать цель';
                    goalForm.dataset.editing = goalId;
                    goalForm.category.value = data.category;
                    goalForm.subcategory.value = data.subcategory || '';
                    goalForm.description.value = data.description || '';
                    goalForm.target_value.value = data.target_value || '';
                    goalForm.period.value = data.period || 'day';
                    goalForm.name.value = data.name || '';
                    goalForm.start_date.value = data.start_date || '';
                    goalForm.end_date.value = data.end_date || '';
                    goalForm.status.value = data.status || 'active';
                    // часы/минуты
                    if (data.target_value) {
                        const val = parseFloat(data.target_value);
                        const h = Math.floor(val);
                        const m = Math.round((val - h) * 60);
                        goalHours.value = h;
                        goalMinutes.value = m;
                        updateGoalTargetValue();
                    }
                    goalModal.style.display = 'flex';
                });
        });
    });

    document.querySelectorAll('.btn-edit-goal').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const goalId = btn.dataset.goalId;
            fetch(`/goals/${goalId}/json/`)
                .then(response => response.json())
                .then(data => {
                    goalModalTitle.textContent = 'Редактировать цель';
                    goalForm.dataset.editing = goalId;
                    goalForm.category.value = data.category;
                    goalForm.subcategory.value = data.subcategory || '';
                    goalForm.description.value = data.description || '';
                    goalForm.target_value.value = data.target_value || '';
                    goalForm.period.value = data.period || 'day';
                    goalForm.name.value = data.name || '';
                    goalForm.start_date.value = data.start_date || '';
                    goalForm.end_date.value = data.end_date || '';
                    goalForm.status.value = data.status || 'active';
                    if (data.target_value) {
                        const val = parseFloat(data.target_value);
                        const h = Math.floor(val);
                        const m = Math.round((val - h) * 60);
                        goalHours.value = h;
                        goalMinutes.value = m;
                        updateGoalTargetValue();
                    }
                    goalModal.style.display = 'flex';
                });
        });
    });

    const goalSelect = document.getElementById('goal');
    if (goalSelect) {
        goalSelect.addEventListener('change', function () {
            if (goalSelect.value === '__new__') {
                // Открыть модалку создания цели поверх addActivityModal
                goalModalTitle.textContent = 'Создать цель';
                goalForm.reset();
                goalModal.style.display = 'flex';
                goalForm.dataset.editing = '';
                // Не скрываем addActivityModal!
            }
        });
    }
    if (goalForm) {
        goalForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(goalForm);
            let url = '/goals/add/';
            if (goalForm.dataset.editing) {
                url = `/goals/${goalForm.dataset.editing}/edit/`;
            }
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data && data.success) {
                    // Если модалка вызвана из формы активности — добавить новую цель в select и выбрать
                    if (goalSelect && !goalForm.dataset.editing) {
                        const option = document.createElement('option');
                        option.value = data.id;
                        option.text = goalName.value;
                        goalSelect.appendChild(option);
                        goalSelect.value = data.id;
                    }
                    goalModal.style.display = 'none';
                }
            });
        });
    }

    function updateGoalTargetValue() {
        const hours = parseInt(goalHours.value, 10) || 0;
        const minutes = parseInt(goalMinutes.value, 10) || 0;
        goalTargetValue.value = (hours + minutes / 60).toFixed(2);
    }
    if (goalHours && goalMinutes && goalTargetValue) {
        goalHours.addEventListener('change', updateGoalTargetValue);
        goalMinutes.addEventListener('change', updateGoalTargetValue);
        updateGoalTargetValue();
    }

    function formatHours(val) {
        if (val < 1 && val > 0) {
            return Math.round(val * 60) + ' мин';
        }
        return val + ' ч';
    }
});