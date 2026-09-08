from django.http import HttpResponse


def home(request):
    return HttpResponse("<h1>Todo Application</h1>")
