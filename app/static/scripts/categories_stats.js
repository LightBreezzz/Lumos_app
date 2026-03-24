document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('categoriesPieChart').getContext('2d');
    let chart;
    let lastData = null;
    let lastPeriod = 'all';
    let lastStart = '';
    let lastEnd = '';
    let drilldownMode = false;
    let lastCategoryLabel = '';

    function formatTime(hours) {
        const totalMinutes = Math.round(hours * 60);
        const h = Math.floor(totalMinutes / 60);
        const m = totalMinutes % 60;
        if (h > 0 && m > 0) return `${h} ч. ${m} мин.`;
        if (h > 0) return `${h} ч.`;
        return `${m} мин.`;
    }

    function renderBackButton() {
        let btn = document.getElementById('backToCategoriesBtn');
        if (!btn) {
            btn = document.createElement('button');
            btn.id = 'backToCategoriesBtn';
            btn.className = 'btn-action';
            btn.style.margin = '0 auto 18px auto';
            btn.style.display = 'block';
            btn.innerText = 'Назад к категориям';
            btn.onclick = function () {
                drilldownMode = false;
                document.getElementById('visualization-title').innerText = 'Статистика по категориям';
                btn.remove();
                fetchAndRender(lastPeriod, lastStart, lastEnd);
            };
            document.querySelector('.today-page').prepend(btn);
        }
    }

    function fetchAndRender(period = 'all', start = '', end = '') {
        lastPeriod = period;
        lastStart = start;
        lastEnd = end;
        fetch(`/api/categories-stats/?period=${period}${period === 'custom' && start && end ? `&start=${start}&end=${end}` : ''}`)
            .then(r => r.json())
            .then(data => {
                lastData = data;
                if (chart) chart.destroy();
                chart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            data: data.data,
                            backgroundColor: data.colors,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        onClick: function(evt, elements) {
                            if (elements.length && !drilldownMode) {
                                const idx = elements[0].index;
                                const categoryLabel = data.labels[idx];
                                const categoryId = getCategoryIdByLabel(categoryLabel);
                                console.log('Drilldown click:', {idx, categoryLabel, categoryId, ids: lastData.ids});
                                if (categoryId) {
                                    drilldownMode = true;
                                    lastCategoryLabel = categoryLabel;
                                    document.getElementById('visualization-title').innerText = `Подкатегории: ${categoryLabel}`;
                                    fetch(`/api/subcategories-stats/?category_id=${categoryId}&period=${lastPeriod}${lastPeriod === 'custom' && lastStart && lastEnd ? `&start=${lastStart}&end=${lastEnd}` : ''}`)
                                        .then(r => r.json())
                                        .then(subData => {
                                            if (chart) chart.destroy();
                                            chart = new Chart(ctx, {
                                                type: 'pie',
                                                data: {
                                                    labels: subData.labels,
                                                    datasets: [{
                                                        data: subData.data,
                                                        backgroundColor: subData.colors,
                                                        borderWidth: 1
                                                    }]
                                                },
                                                options: {
                                                    responsive: true,
                                                    plugins: {
                                                        legend: {
                                                            position: 'bottom',
                                                            labels: { boxWidth: 18, font: { size: 15 } }
                                                        },
                                                        tooltip: {
                                                            callbacks: {
                                                                label: function(context) {
                                                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                                                    const value = context.parsed;
                                                                    const percent = total > 0 ? Math.round(value / total * 100) : 0;
                                                                    return `${context.label}: ${percent}% — ${formatTime(value)}`;
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            });
                                            renderBackButton();
                                        });
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { boxWidth: 18, font: { size: 15 } }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const value = context.parsed;
                                        const percent = total > 0 ? Math.round(value / total * 100) : 0;
                                        return `${context.label}: ${percent}% — ${formatTime(value)}`;
                                    }
                                }
                            }
                        }
                    }
                });
            });
    }

    // Получить id категории по названию (ищем в lastData)
    function getCategoryIdByLabel(label) {
        if (!lastData) return null;
        const idx = lastData.labels.indexOf(label);
        if (idx === -1) return null;
        if (lastData.ids && lastData.ids[idx]) return lastData.ids[idx];
        console.log('Drilldown debug:', {label, idx, ids: lastData.ids, labels: lastData.labels});
        return null;
    }

    // Кнопки периода
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            if (drilldownMode) {
                drilldownMode = false;
                document.getElementById('visualization-title').innerText = 'Статистика по категориям';
                const btnBack = document.getElementById('backToCategoriesBtn');
                if (btnBack) btnBack.remove();
            }
            fetchAndRender(this.dataset.period);
        });
    });

    // Кнопка произвольного диапазона
    document.getElementById('customRangeBtn').addEventListener('click', function () {
        const start = document.getElementById('startDate').value;
        const end = document.getElementById('endDate').value;
        if (start && end) {
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            if (drilldownMode) {
                drilldownMode = false;
                document.getElementById('visualization-title').innerText = 'Статистика по категориям';
                const btnBack = document.getElementById('backToCategoriesBtn');
                if (btnBack) btnBack.remove();
            }
            fetchAndRender('custom', start, end);
        }
    });

    // По умолчанию — всё время
    fetchAndRender('all');
}); 