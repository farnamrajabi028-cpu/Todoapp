import jdatetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Todo


def parse_jalali_date(value):
    value = value.strip()

    if not value:
        return None

    try:
        year, month, day = map(int, value.split("/"))
        return jdatetime.date(
            year,
            month,
            day,
        ).togregorian()
    except (ValueError, TypeError):
        return None






def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)

            next_url = request.POST.get("next")
            if next_url:
                return redirect(next_url)

            return redirect("home")

        messages.error(
            request,
            "نام کاربری یا رمز عبور صحیح نیست.",
        )

    return render(request, "todoapplication/login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm") or request.POST.get("confirm_password") or ""

        if not username or not password:
            messages.error(request, "لطفاً تمامی فیلدهای الزامی را تکمیل کنید.")
            return render(request, "todoapplication/register.html")

        if password != password_confirm:
            messages.error(request, "رمز عبور با تکرار آن مطابقت ندارد.")
            return render(request, "todoapplication/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "این نام کاربری قبلاً استفاده شده است.")
            return render(request, "todoapplication/register.html")

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, f"خوش آمدید {username}! حساب شما با موفقیت ساخته شد.")
        return redirect("home")

    return render(request, "todoapplication/register.html")

def home(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()

        start_date_text = request.POST.get("start_date", "").strip()
        end_date_text = request.POST.get("end_date", "").strip()
        deadline_text = request.POST.get("deadline", "").strip()

        start_date = parse_jalali_date(start_date_text)
        end_date = parse_jalali_date(end_date_text)
        deadline = parse_jalali_date(deadline_text)

        invalid_date = (
            (start_date_text and start_date is None)
            or (end_date_text and end_date is None)
            or (deadline_text and deadline is None)
        )

        if not title:
            messages.error(
                request,
                "عنوان تسک نمی‌تواند خالی باشد.",
            )
        elif invalid_date:
            messages.error(
                request,
                "یکی از تاریخ‌ها معتبر نیست. نمونه صحیح: 1405/06/18",
            )
        else:
            Todo.objects.create(
                user=request.user,
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                deadline=deadline,
            )

            messages.success(
                request,
                "تسک با موفقیت اضافه شد.",
            )
            return redirect("home")

    pending_todos = Todo.objects.filter(
        user=request.user,
        is_completed=False,
    )

    completed_todos = Todo.objects.filter(
        user=request.user,
        is_completed=True,
    )

    context = {
        "pending_todos": pending_todos,
        "completed_todos": completed_todos,
    }

    return render(
        request,
        "todoapplication/home.html",
        context,
    )



@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "با موفقیت از حساب کاربری خارج شدید.")
    return redirect("login")




@login_required
def toggle_todo(request, todo_id):
    todo = get_object_or_404(
        Todo,
        id=todo_id,
        user=request.user,
    )

    if request.method == "POST":
        todo.is_completed = not todo.is_completed
        todo.save(update_fields=["is_completed"])

        if todo.is_completed:
            messages.success(request, "تسک به بخش انجام‌شده منتقل شد.")
        else:
            messages.success(request, "تسک به بخش در انتظار منتقل شد.")

    return redirect("home")


@login_required
def delete_todo(request, todo_id):
    todo = get_object_or_404(
        Todo,
        id=todo_id,
        user=request.user,
    )

    if request.method == "POST":
        todo.delete()
        messages.success(request, "تسک با موفقیت حذف شد.")

    return redirect("home")


def check_username(request):
    username = request.GET.get("username", "").strip()
    if not username:
        return JsonResponse({"exists": False})
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({"exists": exists})
