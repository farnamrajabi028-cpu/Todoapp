import re
from datetime import timedelta
from urllib.parse import urlencode

import jdatetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PhoneOTPRequestForm, PhoneOTPVerifyForm
from .models import Category, Todo, UserProfile
from .services.otp import (
    OTPAttemptsExceededError,
    OTPExpiredError,
    OTPInvalidError,
    create_and_send_otp,
    verify_otp,
)
from .validators import validate_iranian_mobile


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

    return render(
        request,
        "todoapplication/login.html",
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        phone_number_raw = request.POST.get(
            "phone_number",
            "",
        ).strip()
        password = request.POST.get("password", "")
        password_confirm = (
            request.POST.get("password_confirm")
            or request.POST.get("confirm_password")
            or ""
        )

        context = {
            "entered_username": username,
            "entered_phone_number": phone_number_raw,
        }

        if (
            not username
            or not phone_number_raw
            or not password
            or not password_confirm
        ):
            messages.error(
                request,
                "لطفاً تمامی فیلدهای الزامی را تکمیل کنید.",
            )
            return render(
                request,
                "todoapplication/register.html",
                context,
            )

        try:
            phone_number = validate_iranian_mobile(
                phone_number_raw
            )
        except ValidationError as error:
            messages.error(
                request,
                error.messages[0],
            )
            return render(
                request,
                "todoapplication/register.html",
                context,
            )

        if password != password_confirm:
            messages.error(
                request,
                "رمز عبور با تکرار آن مطابقت ندارد.",
            )
            return render(
                request,
                "todoapplication/register.html",
                context,
            )

        if len(password) < 8:
            messages.error(
                request,
                "رمز عبور باید حداقل ۸ کاراکتر باشد.",
            )
            return render(
                request,
                "todoapplication/register.html",
                context,
            )

        if (
            not re.search(r"[A-Z]", password)
            or not re.search(r"[a-z]", password)
        ):
            messages.error(
                request,
                "رمز عبور باید شامل حروف بزرگ و کوچک انگلیسی باشد.",
            )
            return render(
                request,
                "todoapplication/register.html",
                context,
            )

        if not re.search(r"[0-9]", password):
            messages.error(
                request,
                "رمز عبور باید حداقل شامل یک عدد باشد.",
            )
            return render(
                request,
                "todoapplication/register.html",
                context,
            )

        if not re.search(r"[!@#$%^&*?,._-]", password):
            messages.error(
                request,
                "رمز عبور باید حداقل شامل یک نماد خاص باشد.",
            )
            return render(
                request,
                "todoapplication/register.html",
                context,
            )

        if User.objects.filter(
            username__iexact=username,
        ).exists():
            messages.error(
                request,
                "این نام کاربری قبلاً استفاده شده است.",
            )
            return render(
                request,
                "todoapplication/register.html",
                context,
            )

        if UserProfile.objects.filter(
            phone_number=phone_number,
        ).exists():
            messages.error(
                request,
                "این شماره همراه قبلاً ثبت‌نام کرده است.",
            )
            return render(
                request,
                "todoapplication/register.html",
                context,
            )

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email="",
                    password=password,
                )

                UserProfile.objects.create(
                    user=user,
                    phone_number=phone_number,
                )

        except IntegrityError:
            messages.error(
                request,
                "نام کاربری یا شماره همراه قبلاً ثبت شده است.",
            )
            return render(
                request,
                "todoapplication/register.html",
                context,
            )

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        messages.success(
            request,
            f"خوش آمدید {username}! حساب شما با موفقیت ساخته شد.",
        )

        return redirect("home")

    return render(
        request,
        "todoapplication/register.html",
    )


@login_required
def home(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get(
            "description",
            "",
        ).strip()

        category_name = request.POST.get("category_name", "").strip()
        category_id = request.POST.get("category_id", "").strip()
        category_color = request.POST.get("category_color", "#7c3aed").strip()

        start_date_text = request.POST.get(
            "start_date",
            "",
        ).strip()
        end_date_text = request.POST.get(
            "end_date",
            "",
        ).strip()
        deadline_text = request.POST.get(
            "deadline",
            "",
        ).strip()

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
                "یکی از تاریخ‌ها معتبر نیست. "
                "نمونه صحیح: 1405/06/18",
            )
        else:
            category = None
            if category_name:
                category, _ = Category.objects.get_or_create(
                    user=request.user,
                    name=category_name,
                    defaults={"color": category_color},
                )
            elif category_id:
                category = Category.objects.filter(
                    id=category_id,
                    user=request.user,
                ).first()

            Todo.objects.create(
                user=request.user,
                category=category,
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

    user_categories = Category.objects.filter(user=request.user).order_by("name")

    pending_list = Todo.objects.filter(
        user=request.user,
        is_completed=False,
    ).select_related("category").order_by("-id")

    completed_list = Todo.objects.filter(
        user=request.user,
        is_completed=True,
    ).select_related("category").order_by("-id")

    pending_paginator = Paginator(pending_list, 5)
    completed_paginator = Paginator(completed_list, 5)

    pending_page_number = request.GET.get("pending_page")
    completed_page_number = request.GET.get("completed_page")

    pending_todos = pending_paginator.get_page(pending_page_number)
    completed_todos = completed_paginator.get_page(completed_page_number)

    context = {
        "pending_todos": pending_todos,
        "completed_todos": completed_todos,
        "categories": user_categories,
    }

    return render(
        request,
        "todoapplication/home.html",
        context,
    )


@login_required
def add_to_google_calendar(request, todo_id):
    todo = get_object_or_404(
        Todo,
        id=todo_id,
        user=request.user,
    )

    start_date = (
        todo.start_date
        or todo.deadline
        or timezone.localdate()
    )
    end_date = (
        todo.end_date
        or todo.deadline
        or start_date
    )

    if end_date < start_date:
        messages.error(
            request,
            "لطفاً تاریخ معتبر وارد کنید. "
            "تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد.",
            extra_tags="calendar-date-error",
        )
        return redirect("home")

    google_end_date = end_date + timedelta(days=1)

    details = todo.description.strip()

    if todo.deadline:
        deadline_text = todo.deadline.strftime("%Y-%m-%d")
        details = (
            f"{details}\n\nDeadline: {deadline_text}"
            if details
            else f"Deadline: {deadline_text}"
        )

    params = {
        "action": "TEMPLATE",
        "text": todo.title,
        "dates": (
            f"{start_date.strftime('%Y%m%d')}/"
            f"{google_end_date.strftime('%Y%m%d')}"
        ),
        "details": details,
    }

    google_calendar_url = (
        "https://calendar.google.com/calendar/render?"
        + urlencode(params)
    )

    return redirect(google_calendar_url)


@login_required
def logout_view(request):
    logout(request)

    messages.success(
        request,
        "با موفقیت از حساب کاربری خارج شدید.",
    )

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
        todo.save(
            update_fields=["is_completed"],
        )

        if todo.is_completed:
            messages.success(
                request,
                "تسک به بخش انجام‌شده منتقل شد.",
            )
        else:
            messages.success(
                request,
                "تسک به بخش در انتظار منتقل شد.",
            )

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

        messages.success(
            request,
            "تسک با موفقیت حذف شد.",
        )

    return redirect("home")


def check_username(request):
    username = request.GET.get(
        "username",
        "",
    ).strip()

    if not username:
        return JsonResponse(
            {"exists": False},
        )

    exists = User.objects.filter(
        username__iexact=username,
    ).exists()

    return JsonResponse(
        {"exists": exists},
    )


def phone_login_request(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = PhoneOTPRequestForm(
        request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        phone_number = form.cleaned_data["phone_number"]

        profile_exists = UserProfile.objects.filter(
            phone_number=phone_number,
        ).exists()

        if not profile_exists:
            request.session.pop(
                "otp_phone_number",
                None,
            )

            messages.error(
                request,
                "حسابی با این شماره همراه پیدا نشد. "
                "ابتدا ثبت‌نام کنید.",
            )

            return render(
                request,
                "todoapplication/phone_otp_request.html",
                {"form": form},
            )

        try:
            create_and_send_otp(phone_number)
        except NotImplementedError:
            messages.error(
                request,
                "سرویس پیامک هنوز پیکربندی نشده است.",
            )
        else:
            request.session["otp_phone_number"] = (
                phone_number
            )

            messages.success(
                request,
                "کد تأیید برای شماره همراه شما ارسال شد.",
            )

            return redirect("phone_otp_verify")

    return render(
        request,
        "todoapplication/phone_otp_request.html",
        {"form": form},
    )


def phone_otp_verify(request):
    if request.user.is_authenticated:
        return redirect("home")

    phone_number = request.session.get(
        "otp_phone_number"
    )

    if not phone_number:
        messages.error(
            request,
            "ابتدا شماره همراه خود را وارد کنید.",
        )
        return redirect("phone_login")

    form = PhoneOTPVerifyForm(
        request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        try:
            verify_otp(
                phone_number,
                form.cleaned_data["code"],
            )
        except OTPExpiredError as error:
            messages.error(
                request,
                str(error),
            )
        except OTPAttemptsExceededError as error:
            messages.error(
                request,
                str(error),
            )
        except OTPInvalidError as error:
            messages.error(
                request,
                str(error),
            )
        else:
            profile = (
                UserProfile.objects
                .select_related("user")
                .filter(phone_number=phone_number)
                .first()
            )

            if profile is None:
                request.session.pop(
                    "otp_phone_number",
                    None,
                )

                messages.error(
                    request,
                    "حسابی با این شماره همراه پیدا نشد. "
                    "ابتدا ثبت‌نام کنید.",
                )

                return redirect("register")

            user = profile.user

            login(
                request,
                user,
                backend=(
                    "django.contrib.auth.backends."
                    "ModelBackend"
                ),
            )

            request.session.pop(
                "otp_phone_number",
                None,
            )

            messages.success(
                request,
                "با موفقیت وارد حساب کاربری شدید.",
            )

            return redirect("home")

    return render(
        request,
        "todoapplication/phone_otp_verify.html",
        {
            "form": form,
            "phone_number": phone_number,
        },
    )
