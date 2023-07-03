from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Lecture, Category, User, Comment, Course, Homework, Payment, Test, Question, Employee

admin.site.register(Course)
admin.site.register(Comment)


@admin.register(User)
class SuperUser(UserAdmin):
    list_display = UserAdmin.list_display + ("get_course",)

    def get_course(self, obj):
        return [course_paid.title for course_paid in obj.course_paid.all()]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional info",
            {
                "fields": (
                    "image",
                    "course_paid",
                    "listened_lectures",
                    "rejected_lectures",
                    "on_review_lectures",
                )
            },
        ),
    )


admin.site.register(Payment)
admin.site.register(Homework)
admin.site.register(Category)
admin.site.register(Lecture)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Employee)