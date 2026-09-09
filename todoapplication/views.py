import jdatetime

from django.shortcuts import get_object_or_404, redirect, render

from .models import Todo


def parse_jalali_date(value):
    """
    تبدیل تاریخ شمسی واردشده مانند 1405/06/18
    به تاریخ میلادی برای ذخیره در دیتابیس.
    """
    if not value:
        return None

    try:
        year, month, day = map(int, value.strip().split("/"))
        jalali_date = jdatetime.date(year, month, day)
        return jalali_date.togregorian()

    except (ValueError, TypeError):
        return None


def format_jalali_date(value):
    """
    تبدیل تاریخ میلادی دیتابیس به تاریخ شمسی برای نمایش.
    """
    if not value:
        return ""

    jalali_date = jdatetime.date.fromgregorian(date=value)
    return jalali_date.strftime("%Y/%m/%d")


def home(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()

        start_date = parse_jalali_date(
            request.POST.get("start_date")
        )

        end_date = parse_jalali_date(
            request.POST.get("end_date")
        )

        deadline = parse_jalali_date(
            request.POST.get("deadline")
        )

        if title:
            Todo.objects.create(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                deadline=deadline,
                is_completed=False,
            )

        return redirect("home")

    pending_todos = Todo.objects.filter(
        is_completed=False
    ).order_by("-created_at")

    completed_todos = Todo.objects.filter(
        is_completed=True
    ).order_by("-created_at")

    all_todos = list(pending_todos) + list(completed_todos)

    for todo in all_todos:
        todo.jalali_start_date = format_jalali_date(
            todo.start_date
        )

        todo.jalali_end_date = format_jalali_date(
            todo.end_date
        )

        todo.jalali_deadline = format_jalali_date(
            todo.deadline
        )

    return render(
        request,
        "todoapplication/home.html",
        {
            "pending_todos": pending_todos,
            "completed_todos": completed_todos,
        },
    )


def toggle_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)

    if request.method == "POST":
        todo.is_completed = not todo.is_completed
        todo.save(update_fields=["is_completed"])

    return redirect("home")
