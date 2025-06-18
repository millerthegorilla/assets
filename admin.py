from django.contrib import admin

from .models import Asset
from .models import AssetTransfer
from .models import AssetType
from .models import Location

# Register your models here.


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "unique_id",
        "created",
        "last_updated",
        "current_holder",
        "name",
        "description",
        "type",
        "status",
        "location",
        "serial_number",
    )
    search_fields = ("name", "description", "type", "status")
    list_filter = ("type", "status")
    ordering = ("-created",)
    readonly_fields = ("created", "last_updated")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("current_holder")


@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)
    ordering = ("-id",)
    readonly_fields = ("created", "last_updated")

    # def get_queryset(self, request):
    #     return super().get_queryset(request).select_related("type_name",
    # "type_description")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)
    ordering = ("-id",)
    readonly_fields = ("created", "last_updated")

    # def get_queryset(self, request):
    #     return super().get_queryset(request).select_related("location_name",
    # "location_description")


@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "asset",
        "from_user",
        "to_user",
        "notes",
        "created",
        "last_updated",
    )
    search_fields = ("asset__name", "from_user__username", "to_user__username")
    list_filter = ("asset", "from_user", "to_user")
    ordering = ("-created",)
    readonly_fields = ("created", "last_updated")

    # def get_queryset(self, request):
    #     return super().get_queryset(request).select_related("asset",
    # "from_user", "to_user")
