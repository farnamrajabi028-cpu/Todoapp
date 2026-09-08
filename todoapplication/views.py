from django.shortcuts import render, redirect, get_object_or_404
from .models import Todo


def home(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()

        if title:
            Todo.objects.create(
                title=title,
                description=description,
            )

        return redirect("home")

    pending_todos = Todo.objects.filter(is_completed=False).order_by("-created_at")
    completed_todos = Todo.objects.filter(is_completed=True).order_by("-created_at")

    context = {
        "pending_todos": pending_todos,
        "completed_todos": completed_todos,
    }

    return render(request, "todoapplication/home.html", context)


def toggle_todo(request, todo_id):
    if request.method == "POST":
        todo = get_object_or_404(Todo, id=todo_id)
        todo.is_completed = not todo.is_completed
        todo.save()

    return redirect("home")
