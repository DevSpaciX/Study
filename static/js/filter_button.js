const showFiltersBtn = document.getElementById('show-filters-btn');
const filter = document.getElementById('filter');

showFiltersBtn.addEventListener('click', () => {
  if (filter.style.display === 'none') {
    filter.style.display = 'block';
    showFiltersBtn.textContent = 'Hide filter';
  } else {
    filter.style.display = 'none';
    showFiltersBtn.textContent = 'Show filter';
  }
});