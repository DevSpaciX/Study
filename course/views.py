import json

import stripe
from django import forms
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.forms import TextInput, Select
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django_filters import rest_framework as filters, CharFilter
from django.views import generic, View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from course.bot import run_bot
from course.forms import SignUpForm, LoginForm
from course.models import Course, Category, Lecture, Comment, User, Payment, Homework, Test
from course_core import settings
# from course.bot import run_bot

stripe.api_key = settings.STRIPE_SECRET_KEY


class CourseFilter(filters.FilterSet):
    category_name = CharFilter(
        field_name="category__title",
        lookup_expr="icontains",
        widget=Select(
            choices=[("", "All")] + [(category.title, category.title) for category in Category.objects.all()],
            attrs={
                "class": "w-full border border-gray-400 py-2 px-3 rounded-md shadow-sm"
            },
        ),
    )

    course_filter = filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        widget=TextInput(
            attrs={
                "class": "block w-full p-4 pl-10 text-sm text-gray-900 border border-gray-300 "
                         "rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 "
                         "dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 "
                         "dark:focus:border-blue-500",
                "placeholder": "Search",
            }
        ),
    )
    course_level = CharFilter(
        field_name="level",
        lookup_expr="icontains",
        widget=Select(
            choices=[("", "All")] + Course.LEVEL_CHOICES,
            attrs={
                "class": "w-full border border-gray-400 py-2 px-3 rounded-md shadow-sm"
            },
        ),
    )

    @staticmethod
    def filter_popular_first(queryset, name, value):
        if value:
            return queryset.order_by("-rating")
        else:
            return queryset.order_by("price")

    class Meta:
        model = Course
        fields = ["category_name"]


class ListOfCourses(generic.ListView):
    model = Course
    template_name = "course/home_page.html"
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = CourseFilter(self.request.GET)

        # Установка порядка сортировки для object_list
        object_list = self.model.objects.order_by('rating')

        paginator = Paginator(object_list, self.paginate_by)
        page = self.request.GET.get('page')
        courses = paginator.get_page(page)
        context['courses'] = courses
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        filter = CourseFilter(self.request.GET, queryset=queryset.order_by('rating'))
        return filter.qs.distinct()


class DetailCourses(LoginRequiredMixin, generic.DetailView):
    queryset = Course.objects.prefetch_related("lecture")
    template_name = "course/course_detail.html"
    login_url = reverse_lazy("course:login")

    def get_context_data(self, **kwargs):
        context = super(DetailCourses, self).get_context_data(**kwargs)
        context["course"] = Course.objects.get(pk=self.kwargs["pk"])
        context["lectures"] = Lecture.objects.filter(course_id=self.kwargs["pk"])
        context["comments"] = Comment.objects.filter(course_id=self.kwargs["pk"])
        context["STRIPE_PUBLIC_KEY"] = settings.STRIPE_PUBLIC_KEY

        return context

    # @csrf_exempt
    # def post(self, request, *args, **kwargs):
    #     user = request.user.pk
    #     product_id = self.kwargs["pk"]
    #     product = Course.objects.get(id=product_id)
    #     YOUR_DOMAIN = "https://crm29507.dzencode.net/"
    #     checkout_session = stripe.checkout.Session.create(
    #         payment_method_types=["card"],
    #         line_items=[
    #             {
    #                 "price_data": {
    #                     "currency": "usd",
    #                     "unit_amount": product.price * 100,
    #                     "product_data": {
    #                         "name": product.title,
    #                     },
    #                 },
    #                 "quantity": 1,
    #             },
    #         ],
    #         metadata={"product_id": product.id, "user_id": user},
    #         mode="payment",
    #         success_url=YOUR_DOMAIN + f"success/?session_id={{CHECKOUT_SESSION_ID}}",
    #         cancel_url=YOUR_DOMAIN + "/cancel/",
    #     )
    #     return JsonResponse({"id": checkout_session.id})


def success(request):
    session_id = request.GET.get('session_id')
    checkout_session = stripe.checkout.Session.retrieve(session_id)

    if checkout_session.payment_status == 'paid':
        product_id = checkout_session.metadata['product_id']
        user_id = checkout_session.metadata['user_id']
        User.objects.get(pk=user_id).course_paid.add(product_id)

    return render(request, 'course/success.html')


class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, "authentication/sign_up.html", {"form": form})

    def post(self, request):
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)
            return redirect(reverse("course:home-page"))
        return render(request, "authentication/sign_up.html", {"form": form})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "authentication/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect(reverse("course:home-page"))
            form.add_error(None, "Invalid username or password")
        return render(request, "authentication/login.html", {"form": form})


def my_ajax_view(request):
    rating = request.POST.get("rate")
    comment_content = request.POST.get("comment-text")
    user = request.user.pk
    course_id = request.POST.get("course_id")
    Comment.objects.create(
        sender=User.objects.get(pk=user),
        content=comment_content,
        course=Course.objects.get(pk=course_id),
        rating=rating,
    )
    return JsonResponse(
        {"status": "success", "message": "Комментарий успешно создан."}, status=200
    )


def profile(request, slug):
    homework = Homework.objects.all()
    profile = get_object_or_404(User, username=slug)
    completed_lectures = {}  # словарь для хранения количества пройденных лекций
    all_done_lectures = 0
    all_tests = 0

    for course in Course.objects.all():
        done_lectures = 0
        for lecture in course.lecture.all():
            if lecture in profile.listened_lectures.all():
                done_lectures += 1
                all_done_lectures += 1
            for test in lecture.test_set.all():
                all_tests += 1

        all_lectures = course.lecture.all().count() + all_tests
        completed_lectures[course.title] = (
            round(done_lectures / all_lectures * 100)
            if done_lectures > 0
            else 0
        )

    context = {
        "profile": profile,
        "completed_lectures": completed_lectures,
        "done_lectures": all_done_lectures,
        "homework": homework,
    }
    return render(request, "course/profile.html", context=context)


class LearnCourses(LoginRequiredMixin, generic.DetailView):
    queryset = Course.objects.prefetch_related("lecture")
    template_name = "course/learn_page.html"
    login_url = reverse_lazy("course:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_pk = self.kwargs["pk"]
        lecture_pk = self.kwargs["lecture_pk"]
        lectures = Lecture.objects.filter(course_id=course_pk)
        context["lectures"] = lectures
        context["course_pk"] = course_pk
        context["lecture"] = Lecture.objects.filter(pk=lecture_pk, course_id=course_pk)
        return context

    def post(self, request, pk, lecture_pk):
        user = get_object_or_404(User, pk=request.user.pk)
        lecture = get_object_or_404(Lecture, id=lecture_pk)

        # Удалить лекцию из listened_lectures и добавить в on_review_lectures
        if lecture in user.rejected_lectures.all():
            user.rejected_lectures.remove(lecture)
            user.on_review_lectures.add(lecture)

        if lecture not in user.rejected_lectures.all():
            user.on_review_lectures.add(lecture)

        Homework.objects.create(
            student=user,
            homework=lecture.home_work,
            course=Course.objects.get(pk=pk),
            lecture=lecture,
        )

        # Сохранить изменения
        user.save()

        # Отправить ответ на запрос
        if lecture.pk != Lecture.objects.filter(course_id=pk).last().pk:
            return HttpResponseRedirect(
                reverse_lazy("course:learn-page", args=[pk, lecture_pk + 1])
            )
        return HttpResponseRedirect(
            reverse_lazy(
                "course:learn-page",
                args=[pk, Lecture.objects.filter(course_id=pk).first().pk],
            )
        )


class Homeworks(generic.ListView):
    model = Homework
    template_name = "course/homeworks.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            # Если пользователь не является сотрудником, то вернуть ошибку 404
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["homeworks"] = Homework.objects.all()
        return context

    def post(self, request):
        user = get_object_or_404(User, pk=request.POST.get("student_pk"))
        homework = get_object_or_404(Homework, pk=request.POST.get("homework_pk"))
        lecture = get_object_or_404(Lecture, id=request.POST.get("lecture_pk"))
        print(lecture)
        action = request.POST.get("action")
        print(action)
        if action == "accept":
            print('OK')
            if lecture in user.rejected_lectures.all():
                user.rejected_lectures.remove(lecture)
            if lecture in user.on_review_lectures.all():
                user.on_review_lectures.remove(lecture)
            user.listened_lectures.add(lecture)

        if action == "reject":
            print('NOT')
            if (
                    lecture in user.on_review_lectures.all()
                    and lecture not in user.rejected_lectures.all()
            ):
                user.on_review_lectures.remove(lecture)
                user.rejected_lectures.add(lecture)

        homework.delete()
        user.save()
        return JsonResponse(
            {"status": "success"}, status=200
        )


def quiz_view(request, pk):
    course = Test.objects.get(pk=pk).questions.all()  # Получение данных из модели Course
    quiz_array = []

    for i, item in enumerate(course):
        question = {
            "id": str(i),
            "question": item.question_text,
            "options": [item.option1, item.option2, item.option3, item.option4],
            "correct": item.correct_option
        }
        quiz_array.append(question)

    context = {
        "quiz_array_json": json.dumps(quiz_array)  # Преобразование массива в JSON-строку
    }

    return render(request, 'course/quiz_template.html', context)


# Django view для обработки запросов от Telegram
@csrf_exempt
def telegram_webhook(request):
    run_bot()
    return HttpResponse()
