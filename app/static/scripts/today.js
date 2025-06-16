function renderTimeline() {
    const container = document.getElementById('visualization');
    if (!container) return;
    fetch('/api/chart-data/')
        .then(response => response.json())
        .then(apiData => {
            console.log('Данные из API:', apiData);

            const transformedData = transformDataForVis(apiData);
            console.log('transformedData:', transformedData);

            // Вычисляем min/max дату для диапазона графика
            const allStarts = transformedData.map(x => new Date(x.start).getTime());
            const allEnds = transformedData.map(x => new Date(x.end).getTime());
            const minDate = new Date(Math.min(...allStarts));
            const maxDate = new Date(Math.max(...allEnds));

            const items = new vis.DataSet(transformedData);

            const options = {
                stack: true,
                showCurrentTime: false,
                zoomable: false,
                start: minDate,
                end: maxDate,
                editable: false,
                orientation: 'top',
                tooltip: {
                    followMouse: true,
                    overflowMethod: 'cap'
                },
                format: {
                    minorLabels: {
                        hour: 'HH:mm',
                        minute: 'HH:mm'
                    }
                }
            };

            container.innerHTML = '';
            new vis.Timeline(container, items, options);
        })
        .catch(error => console.error('Ошибка загрузки данных:', error));
}

document.addEventListener('DOMContentLoaded', renderTimeline);

function transformDataForVis(apiData) {
    return apiData.map(activity => {
        // Получаем только время из start_time и end_time
        const startTime = activity.start_time.split('T')[1]?.slice(0,5) || '';
        const endTime = activity.end_time.split('T')[1]?.slice(0,5) || '';
        return {
            content: activity.name,
            start: activity.start_time,
            end: activity.end_time,
            style: `background-color: ${activity.color};`,
            title: `${activity.name}\n (${startTime} - ${endTime})`
        };
    });
}