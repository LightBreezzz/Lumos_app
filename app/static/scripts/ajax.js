// $(document).ready(function () {
//     $('#activityForm').on('submit', function (e) {
//         e.preventDefault(); // Предотвращаем стандартную отправку формы

//         const formData = $(this).serialize();

//         $.ajax({
//             url: "{% url 'add_activity' %}",
//             method: 'POST',
//             data: formData,
//             success: function (response) {
//                 if (response.success) {
//                     // Добавляем новое действие в список
//                     $('#activityList').append(
//                         `<li class="list-group-item">${response.name} (${response.start_time} - ${response.end_time})</li>`
//                     );

//                     // Закрываем модальное окно
//                     $('#addActivityModal').hide();

//                     // Очищаем форму
//                     $('#activityForm')[0].reset();
//                 } else {
//                     alert('Ошибка при добавлении активности.');
//                 }
//             },
//             error: function (error) {
//                 console.error('Ошибка:', error);
//                 alert('Произошла ошибка при отправке данных.');
//             }
//         });
//     });
// });

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('ActivityForm');
    const modal = document.getElementById('addActivityModal');

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(form);

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
                modal.style.display = 'none';

                // Очищаем форму
                form.reset();
            } else {
                alert('Ошибка при добавлении активности.');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    });

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
});