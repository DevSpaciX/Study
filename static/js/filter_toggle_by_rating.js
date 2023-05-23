  const toggleButton = document.getElementById('toggle-button');
  toggleButton.addEventListener('click', () => {
    // Изменяем значение фильтра на противоположное
    const currentValue = '{{ request.GET.popular_first }}' === 'on';
    const newValue = !currentValue;
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set('popular_first', newValue ? 'on' : '');
    // Перезагружаем страницу с новыми параметрами
            const applyFiltersButton = document.getElementById("apply-filters-button");
        applyFiltersButton.onclick = function () {
            form.submit();
        }
  });