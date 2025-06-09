$(document).ready(function () {
    $('#activityForm').on('submit', function (e) {
        e.preventDefault(); // Предотвращаем стандартную отправку формы

        const formData = $(this).serialize();

        $.ajax({
            url: "{% url 'add_activity' %}",
            method: 'POST',
            data: formData,
            success: function (response) {
                if (response.success) {
                    // Добавляем новое действие в список
                    $('#activityList').append(
                        `<li class="list-group-item">${response.name} (${response.start_time} - ${response.end_time})</li>`
                    );

                    // Закрываем модальное окно
                    $('#addActivityModal').hide();

                    // Очищаем форму
                    $('#activityForm')[0].reset();
                } else {
                    alert('Ошибка при добавлении активности.');
                }
            },
            error: function (error) {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при отправке данных.');
            }
        });
    });
});