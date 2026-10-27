from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "address",
        "total_price",
        "status",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("full_name", "email", "address")
    inlines = [OrderItemInline]
    readonly_fields = (
        "public_id",
        "status",
        "stripe_session_id",
        "paid_at",
        "total_price",
        "user",
    )

    def has_add_permission(self, request):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")
    list_filter = ("order", "product")
    search_fields = ("product__name",)
    readonly_fields = ("order", "product", "quantity", "price")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
