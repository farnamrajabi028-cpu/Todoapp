from django.conf import settings
from django.db import models


class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="کاربر",
    )
    name = models.CharField(
        max_length=50,
        verbose_name="نام دسته‌بندی",
    )
    color = models.CharField(
        max_length=20,
        default="#7c3aed",
        verbose_name="رنگ برچسب",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ایجاد",
    )

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Todo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="todos",
        verbose_name="کاربر",
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="todos",
        verbose_name="دسته‌بندی",
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

    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'پایین'),
        (PRIORITY_MEDIUM, 'متوسط'),
        (PRIORITY_HIGH, 'بالا'),
    ]

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        verbose_name='اولویت',
    )

    REPEAT_NONE = 'none'
    REPEAT_DAILY = 'daily'
    REPEAT_WEEKLY = 'weekly'
    REPEAT_MONTHLY = 'monthly'

    REPEAT_CHOICES = [
        (REPEAT_NONE, 'بدون تکرار'),
        (REPEAT_DAILY, 'روزانه'),
        (REPEAT_WEEKLY, 'هفتگی'),
        (REPEAT_MONTHLY, 'ماهانه'),
    ]

    repeat_type = models.CharField(
        max_length=10,
        choices=REPEAT_CHOICES,
        default=REPEAT_NONE,
        verbose_name='تکرار',
    )

    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='shared_todos',
        blank=True,
        verbose_name='اشتراک‌گذاری شده با',
    )

    reminder_enabled = models.BooleanField(
        default=False,
        verbose_name='یادآوری فعال',
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

    @property
    def is_reminder_due(self):
        if not self.reminder_enabled or self.is_completed:
            return False

        from django.utils import timezone

        reference_date = self.deadline or self.start_date
        if reference_date is None:
            return False

        return reference_date <= timezone.localdate()

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="کاربر",
    )

    phone_number = models.CharField(
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="شماره همراه",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین تغییر",
    )

    class Meta:
        verbose_name = "پروفایل کاربر"
        verbose_name_plural = "پروفایل کاربران"

    def __str__(self):
        return self.phone_number or self.user.get_username()


class PhoneOTP(models.Model):
    phone_number = models.CharField(
        max_length=11,
        db_index=True,
        verbose_name="شماره همراه",
    )

    code_hash = models.CharField(
        max_length=128,
        verbose_name="هش کد تأیید",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ایجاد",
    )

    expires_at = models.DateTimeField(
        verbose_name="زمان انقضا",
    )

    attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="تعداد تلاش‌ها",
    )

    is_used = models.BooleanField(
        default=False,
        verbose_name="استفاده شده",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "کد ورود پیامکی"
        verbose_name_plural = "کدهای ورود پیامکی"
        indexes = [
            models.Index(
                fields=["phone_number", "is_used", "expires_at"],
                name="otp_phone_status_idx",
            ),
        ]

    def __str__(self):
        return f"{self.phone_number} - {self.created_at:%Y-%m-%d %H:%M}"
