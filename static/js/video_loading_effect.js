        document.addEventListener('DOMContentLoaded', function () {
            const videoContainer = document.querySelector('#video-container');

            // Показываем сообщение о загрузке
            var loadingMessage = videoContainer.querySelector('#loading-message');
            loadingMessage.style.display = 'block';

            // Скрываем сообщение о загрузке и показываем iframe после загрузки видео
            var videoIframe = videoContainer.querySelector('iframe');
            videoIframe.addEventListener('load', function () {
                loadingMessage.style.display = 'none';
                videoIframe.style.display = 'block';
            });
        });