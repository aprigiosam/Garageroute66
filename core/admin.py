from django.contrib import admin

from . import models


class ServiceItemInline(admin.TabularInline):
    model = models.ServiceItem
    extra = 1


class PaymentInline(admin.TabularInline):
    model = models.Payment
    extra = 0


class ServiceAttachmentInline(admin.TabularInline):
    model = models.ServiceAttachment
    extra = 0


@admin.register(models.ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "vehicle", "status", "priority", "created_at")
    list_filter = ("status", "priority", "created_at")
    search_fields = (
        "number",
        "vehicle__plate",
        "vehicle__model",
        "customer__name",
    )
    date_hierarchy = "created_at"
    inlines = [ServiceItemInline, PaymentInline, ServiceAttachmentInline]


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    search_fields = ("name", "document_id", "phone")
    list_display = ("name", "phone", "email", "created_at")


@admin.register(models.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("plate", "brand", "model", "customer")
    list_filter = ("brand",)
    search_fields = ("plate", "brand", "model", "customer__name")


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "status", "method", "paid_at")
    list_filter = ("status", "method")
    search_fields = ("order__number",)


@admin.register(models.StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "from_status", "to_status", "changed_by", "created_at")
    list_filter = ("to_status",)
    search_fields = ("order__number", "notes")


@admin.register(models.ServiceAttachment)
class ServiceAttachmentAdmin(admin.ModelAdmin):
    list_display = ("order", "category", "description", "uploaded_by", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("order__number", "description")
