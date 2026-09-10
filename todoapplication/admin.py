from django.contrib import admin

from .models import Todo


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
