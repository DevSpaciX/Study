from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from course.views import (
    ListOfCourses,
    LoginView,
    SignUpView,
    DetailCourses,
    my_ajax_view,
    profile,
    # stripe_webhook,
    LearnCourses,
    Homeworks, success, quiz_view, telegram_webhook,
)

urlpatterns = [
    path("", ListOfCourses.as_view(), name="home-page"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("login/", LoginView.as_view(), name="login"),
    path("sign_up/", SignUpView.as_view(), name="sign-up"),
    path("ajax/", my_ajax_view, name="my_ajax_view"),
    path("detail_page/<int:pk>/", DetailCourses.as_view(), name="detail-page"),
    path("homeworks/", Homeworks.as_view(), name="homework"),
    path("profile/<slug:slug>/", profile, name="profile"),
    path("learn/<int:pk>/<int:lecture_pk>/", LearnCourses.as_view(), name="learn-page"),
    path("success/", success, name="success"),
    path("test/<int:pk>/", quiz_view, name="test"),
    path('telegram/webhook/', telegram_webhook),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "course"
