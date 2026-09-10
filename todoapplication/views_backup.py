from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


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

    return render(request, "todo/login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not username or not email or not password1 or not password2:
            messages.error(
                request,
                "لطفاً همه فیلدها را تکمیل کنید.",
            )

        elif User.objects.filter(username=username).exists():
            messages.error(
                request,
                "این نام کاربری قبلاً استفاده شده است.",
            )

        elif User.objects.filter(email=email).exists():
            messages.error(
                request,
                "این ایمیل قبلاً ثبت شده است.",
            )

        elif password1 != password2:
            messages.error(
                request,
                "رمز عبور و تکرار آن یکسان نیستند.",
            )

        elif len(password1) < 8:
            messages.error(
                request,
                "رمز عبور باید حداقل ۸ کاراکتر داشته باشد.",
            )

        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password1,
            )

            messages.success(
                request,
                "حساب کاربری با موفقیت ساخته شد؛ اکنون وارد شوید.",
            )

            return redirect("login")

    return render(request, "todo/register.html")
