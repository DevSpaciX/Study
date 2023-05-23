const slider = document.getElementById("price-range");
        const output = document.getElementById("price-output");
        const form = document.getElementById("filter-form");

        // Обработчик события, который вызывается при изменении значения слайдера
        slider.oninput = function () {
            // Получаем значение слайдера
            const price = this.value;
            // console.log(price)

            // Отображаем выбранную пользователем цену
            output.textContent = `$0 - $${price}`;

            // Устанавливаем значение в скрытое поле формы
            document.getElementById("id_price_min").value = 0;
            document.getElementById("id_price_max").value = price;
        }

        // Обработчик события для отправки формы при нажатии на кнопку
        const applyFiltersButton = document.getElementById("apply-filters-button");
        applyFiltersButton.onclick = function () {
            form.submit();
        }