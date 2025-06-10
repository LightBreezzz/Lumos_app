document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/chart-data/')
        .then(response => response.json())
        .then(apiData => {
            console.log('Данные из API:', apiData);

            // Преобразуем данные для Vis.js
            const transformedData = transformDataForVis(apiData);

            // Создаем DataSet для Vis.js
            const items = new vis.DataSet(transformedData);

            // Настройки временной шкалы
            const options = {
                stack: true, // Стек активностей (если они перекрываются)
                showCurrentTime: false, // Не показывать текущее время
                zoomable: false, // Запрет масштабирования
                start: new Date().setHours(0, 0, 0, 0), // Начало дня
                end: new Date().setHours(23, 59, 59, 999), // Конец дня
                editable: false, // Запрет редактирования элементов
                orientation: 'top', // Ориентация меток времени
                tooltip: {
                    followMouse: true, // Подсказка следует за курсором
                    overflowMethod: 'cap' // Ограничение текста в подсказке
                },
                format: {
                    minorLabels: {
                        hour: 'HH:mm', // Формат времени
                        minute: 'HH:mm'
                    }
                }
            };

            // Инициализация временной шкалы
            const container = document.getElementById('visualization');
            const timeline = new vis.Timeline(container, items, options);
        })
        .catch(error => console.error('Ошибка загрузки данных:', error));
});

// Функция для преобразования данных
function transformDataForVis(apiData) {
    const today = new Date().toISOString().split('T')[0]; // Текущая дата
    return apiData.map(activity => ({
        content: activity.name,
        start: `${today}T${activity.start_time}`,
        end: `${today}T${activity.end_time}`,
        style: `background-color: ${activity.color};`, // Цвет из категории
        title: `Название: ${activity.name}\nВремя: ${activity.start_time} - ${activity.end_time}` // Тултип
    }));
}