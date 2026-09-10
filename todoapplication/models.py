from django.conf import settings
from django.db import models


class Todo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="todos",
        verbose_name="کاربر",
        null=True,
        blank=True,
    )

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    is_completed = models.BooleanField(
        default=False,
        verbose_name="انجام شده",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ایجاد",
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ شروع",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ پایان",
    )

    deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name="ددلاین",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "تسک"
        verbose_name_plural = "تسک‌ها"

    def __str__(self):
        return self.title
