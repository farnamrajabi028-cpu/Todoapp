from django.contrib import admin
from django.urls import path

from todoapplication import views


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "todo/<int:todo_id>/toggle/",
        views.toggle_todo,
        name="toggle_todo",
    ),

    path(
        "todo/<int:todo_id>/delete/",
        views.delete_todo,
        name="delete_todo",
    ),
]
