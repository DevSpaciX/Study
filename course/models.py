import urllib

from PIL import Image
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_logged_in
from django.dispatch import receiver

class Category(models.Model):
    title = models.CharField(max_length=15)

    def __str__(self):
        return self.title
class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    amount = models.PositiveIntegerField()
    course = models.ForeignKey("Course", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.course} {self.user}"


class Homework(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    lecture = models.ForeignKey("Lecture", on_delete=models.SET_NULL, null=True)
    homework = models.URLField(null=False)
    course = models.ForeignKey("Course", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.student}`s work ({self.course})"


class User(AbstractUser):
    image = models.ImageField(upload_to="images/")
    course_paid = models.ManyToManyField(
        "Course", blank=True, related_name="user_course"
    )
    listened_lectures = models.ManyToManyField("Lecture", blank=True)
    rejected_lectures = models.ManyToManyField(
        "Lecture", blank=True, related_name="user_rework"
    )
    on_review_lectures = models.ManyToManyField(
        "Lecture", blank=True, related_name="user_on_review"
    )
    slug = models.SlugField(default="", null=False)


@receiver(user_logged_in)
def my_user_logged_in_callback(sender, request, user, **kwargs):
    social_account = SocialAccount.objects.get(user=request.user, provider="google")
    extra_data = social_account.extra_data
    avatar_url = extra_data.get("picture", None)
    # Сохраняем изображение с полным URL-адресом на Amazon S3 в поле avatar модели User
    if avatar_url:
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urllib.request.urlopen(avatar_url).read())
        img_temp.flush()
        user = request.user
        user.image.save(f"{user.username}_avatar.jpg", File(img_temp), save=True)


class Comment(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    course = models.ForeignKey(
        "Course", blank=True, null=True, on_delete=models.SET_NULL
    )
    rating = models.PositiveIntegerField(default=2)

    def __str__(self):
        return self.content[:10]


@receiver(post_save, sender=Comment)
def update_course_rating(sender, instance, **kwargs):
    course = instance.course
    comments_count = Comment.objects.filter(course=course).count()
    sum_of_ratings = Comment.objects.filter(course=course).aggregate(Sum("rating"))[
        "rating__sum"
    ]

    if comments_count:
        rating = round(sum_of_ratings / comments_count, 2)
        course.rating = rating
        course.save()




class Course(models.Model):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    LEVEL_CHOICES = [
        (BEGINNER, "Beginner"),
        (INTERMEDIATE, "Intermediate"),
        (ADVANCED, "Advanced"),
    ]

    title = models.CharField(max_length=20)
    description = models.TextField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    price = models.PositiveIntegerField()
    rating = models.FloatField(default=3)
    image = models.ImageField(upload_to="images/")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=BEGINNER)

    def __str__(self):
        return self.title

    def get_display_price(self):
        return self.price


class Lecture(models.Model):

    title = models.CharField(max_length=30)
    text = models.TextField(max_length=500)
    video = models.URLField(max_length=200)
    home_work = models.URLField(max_length=100)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lecture")

    def __str__(self):
        return self.title
