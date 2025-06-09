document.addEventListener('DOMContentLoaded', function () {
    // Загрузка данных через API
    fetch('/api/chart-data/')
        .then(response => response.json())
        .then(activities => {
            console.log('Данные из API:', activities); // Проверяем данные

            function isValidTime(time) {
                const timeRegex = /^([01]?\d|2[0-3]):([0-5]?\d)$/; // Регулярное выражение для HH:mm
                return timeRegex.test(time);
            }

            const validActivities = activities.filter(activity => {
                return activity.start_time && activity.end_time &&
                    isValidTime(activity.start_time) &&
                    isValidTime(activity.end_time);
            });

            if (validActivities.length === 0) {
                console.error('Нет корректных данных для отображения графика.');
                return;
            }
            
            const ctx = document.getElementById('timelineChart').getContext('2d');

            // Подготовка данных для графика
            const labels = Array.from({ length: 24 }, (_, i) => `${i}:00`); // Метки времени (00:00 - 23:59)
            const datasets = activities.map(activity => ({
                label: activity.name,
                data: [
                    { x: new Date(`1970-01-01T${activity.start_time}`), y: 0 },
                    { x: new Date(`1970-01-01T${activity.end_time}`), y: 0 }
                ],
                backgroundColor: activity.color,
                borderColor: activity.color,
                borderWidth: 1,
                barThickness: 20,
                order: 1 // Упорядочивание блоков
            }));

            // Создание графика
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    indexAxis: 'x', // Горизонтальная ориентация
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'hour',
                            },
                            ticks: {
                                source: 'labels'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grid: {
                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const activity = activities[context.dataIndex];
                                    return `${activity.name} (${activity.start_time} - ${activity.end_time})`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Ошибка загрузки данных:', error));
});