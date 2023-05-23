      $(document).ready(function () {
          $('#comment-form').submit(function (event) {
              event.preventDefault(); // предотвращаем стандартное поведение отправки формы
              var rating = $('input[name="rate"]:checked').val();

              if (rating == null) { // если не выбрана оценка, вызываем ошибку
                  $('#error').show(); // показываем блок с ошибкой
                  return;
              }

              // отправляем данные формы на сервер
              $.ajax({
                  type: 'POST',
                  url: '{% url "course:my_ajax_view" %}',
                  data: $(this).serialize(),
                  success: function (response) {
                      $('#success').show();
                      $('#comment-form').trigger("reset"); // перезагрузка страницы
                  },
                  error: function (xhr, status, error) {
                      console.log('Error:', error);
                  }
              });
          });
      });