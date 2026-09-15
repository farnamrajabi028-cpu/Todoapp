from django.contrib import admin

from .models import PhoneOTP, Todo, UserProfile



@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "is_completed",
        "start_date",
        "end_date",
        "deadline",
        "created_at",
    )

    list_filter = (
        "is_completed",
        "created_at",
        "start_date",
        "end_date",
        "deadline",
    )

    search_fields = (
        "title",
        "description",
        "user__username",
        "user__email",
    )

    ordering = ("-created_at",)

    list_select_related = ("user",)

    readonly_fields = ("created_at",)

    autocomplete_fields = ("user",)

    list_per_page = 25



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "phone_number",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "phone_number",
    )

    list_select_related = ("user",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = ("user",)


@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "phone_number",
        "created_at",
        "expires_at",
        "attempts",
        "is_used",
    )

    list_filter = (
        "is_used",
        "created_at",
        "expires_at",
    )

    search_fields = ("phone_number",)

    readonly_fields = (
        "code_hash",
        "created_at",
    )

    ordering = ("-created_at",)

    list_per_page = 25
