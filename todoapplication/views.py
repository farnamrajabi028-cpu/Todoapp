from datetime import datetime

from django.shortcuts import get_object_or_404, redirect, render

from .models import Todo


def convert_date(date_value):
    if not date_value:
        return None

    try:
        return datetime.strptime(
            date_value,
            "%d/%m/%Y"
        ).date()
    except ValueError:
        return None


def home(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()

        start_date = convert_date(
            request.POST.get("start_date", "").strip()
        )

        end_date = convert_date(
            request.POST.get("end_date", "").strip()
        )

        deadline = convert_date(
            request.POST.get("deadline", "").strip()
        )

        if title:
            Todo.objects.create(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                deadline=deadline,
            )

        return redirect("home")

    pending_todos = Todo.objects.filter(
        is_completed=False
    ).order_by("-created_at")

    completed_todos = Todo.objects.filter(
        is_completed=True
    ).order_by("-created_at")

    context = {
        "pending_todos": pending_todos,
        "completed_todos": completed_todos,
    }

    return render(
        request,
        "todoapplication/home.html",
        context
    )


def toggle_todo(request, todo_id):
    if request.method == "POST":
        todo = get_object_or_404(Todo, id=todo_id)
        todo.is_completed = not todo.is_completed
        todo.save()

    return redirect("home")
