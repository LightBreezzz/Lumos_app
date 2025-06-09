document.addEventListener('DOMContentLoaded', function () {
    // Получаем элементы
    const modal = document.getElementById('addActivityModal');
    const openModalBtn = document.getElementById('openModalBtn');
    const closeBtn = document.querySelector('.close-btn');

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
});