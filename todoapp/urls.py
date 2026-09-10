from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from todoapplication import views


urlpatterns = [
    path('check-username/', views.check_username, name='check_username'),
    # پنل مدیریت جنگو
    path(
        "admin/",
        admin.site.urls,
    ),

    # صفحه ورود؛ صفحه اصلی سایت
    path(
        "",
        views.login_view,
        name="login",
    ),

    # صفحه ثبت‌نام
    path(
        "register/",
        views.register_view,
        name="register",
    ),

    # صفحه مدیریت تسک‌های کاربر
    path(
        "tasks/",
        views.home,
        name="home",
    ),

    # خروج از حساب کاربری
    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    # تغییر وضعیت تسک
    path(
        "todo/<int:todo_id>/toggle/",
        views.toggle_todo,
        name="toggle_todo",
    ),

    # حذف تسک
    path(
        "todo/<int:todo_id>/delete/",
        views.delete_todo,
        name="delete_todo",
    ),

    # فرم درخواست بازیابی رمز عبور
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name=(
                "registration/password_reset_subject.txt"
            ),
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),

    # نمایش پیام ارسال لینک بازیابی رمز عبور
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    # صفحه تعیین رمز عبور جدید
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),

    # نمایش پیام موفقیت تغییر رمز عبور
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
