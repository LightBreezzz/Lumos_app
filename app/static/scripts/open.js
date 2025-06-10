document.addEventListener('DOMContentLoaded', function () {
    // Получаем элементы модального окна
    const modal = document.getElementById('addActivityModal');
    const openModalBtn = document.getElementById('openModalBtn');
    const closeBtn = document.querySelector('.close-btn');

    // Форма для добавления активности
    const activityForm = document.getElementById('ActivityForm');

    // Поля для добавления новых категорий, подкатегорий и целей
    const newCategoryInput = document.getElementById('newCategory');
    const newSubcategoryInput = document.getElementById('newSubcategory');
    const newGoalInput = document.getElementById('newGoal');

    // Открываем модальное окно
    openModalBtn.addEventListener('click', function () {
        modal.style.display = 'flex';
    });

    // Закрываем модальное окно
    closeBtn.addEventListener('click', function () {
        modal.style.display = 'none';
    });

    // Закрываем модальное окно при клике вне его области
    window.addEventListener('click', function (event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Добавление новой категории
    newCategoryInput.addEventListener('blur', function () {
        const categoryName = newCategoryInput.value.trim();
        if (categoryName) {
            fetch('/add_category/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: `name=${encodeURIComponent(categoryName)}`,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const categorySelect = document.getElementById('category');
                    const option = document.createElement('option');
                    option.value = data.id;
                    option.text = data.name;
                    categorySelect.appendChild(option);
                    categorySelect.value = data.id; // Выбираем новую категорию
                }
            });
        }
    });

    // Добавление новой подкатегории
    newSubcategoryInput.addEventListener('blur', function () {
        const subcategoryName = newSubcategoryInput.value.trim();
        const categorySelect = document.getElementById('category');
        const categoryId = categorySelect.value;

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

    // Добавление новой цели
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

    // Обработка отправки формы для добавления активности
    activityForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(activityForm);

        fetch("{% url 'add_activity' %}", {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Активность успешно добавлена!');
                activityForm.reset();
                modal.style.display = 'none';
            } else {
                alert('Ошибка при добавлении активности.');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    });
});