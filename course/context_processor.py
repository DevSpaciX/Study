from course.models import Homework


def context(request):
    homeworks = Homework.objects.all().count()
    return {
        "homeworks_count": homeworks,
    }
