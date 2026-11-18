from django.contrib import admin
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Order


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display   = ["id", "customer", "item", "qty", "display_rate", "display_amount", "display_status", "created_at"]
    list_filter    = ["status", "created_at"]
    search_fields  = ["customer", "item"]
    search_help_text = "Tìm theo tên khách hàng hoặc tên sản phẩm"
    ordering       = ["-created_at"]
    readonly_fields = ["amount", "created_at"]
    list_per_page  = 25

    fieldsets = (
        ("Thông tin khách hàng", {"fields": ("customer",), "classes": ("wide",)}),
        ("Chi tiết sản phẩm",    {"fields": ("item", "qty", "rate", "amount"), "classes": ("wide",)}),
        ("Trạng thái & Thời gian", {"fields": ("status", "created_at"), "classes": ("wide",)}),
    )

    @display(description="Đơn giá (VNĐ)", ordering="rate")
    def display_rate(self, obj):
        return format_html('<span style="font-family:monospace;">{} ₫</span>', f"{obj.rate:,.0f}")

    @display(description="Thành tiền (VNĐ)", ordering="amount")
    def display_amount(self, obj):
        return format_html('<strong style="color:#7c3aed;font-family:monospace;">{} ₫</strong>', f"{obj.amount:,.0f}")

    @display(description="Trạng thái", ordering="status")
    def display_status(self, obj):
        colors = {
            "Mới":     ("#1d4ed8", "#dbeafe"),
            "Đã giao": ("#15803d", "#dcfce7"),
            "Hủy":     ("#b91c1c", "#fee2e2"),
        }
        fg, bg = colors.get(obj.status, ("#374151", "#f3f4f6"))
        style = f"background:{bg};color:{fg};padding:2px 10px;border-radius:9999px;font-size:0.75rem;font-weight:600;"
        return format_html('<span style="{}">{}</span>', style, obj.status)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.status in Order.LOCKED_STATUSES:
            return False
        return super().has_delete_permission(request, obj)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "revenue-report/",
                self.admin_site.admin_view(self.revenue_report_view),
                name="orders_revenue_report",
            ),
        ]
        return custom + urls

    def revenue_report_view(self, request):
        report_data = (
            Order.objects.filter(status=Order.Status.DA_GIAO)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(total_orders=Count("id"), total_revenue=Sum("amount"))
            .order_by("-date")
        )

        overall = Order.objects.filter(status=Order.Status.DA_GIAO).aggregate(
            total_orders=Count("id"),
            total_revenue=Sum("amount"),
        )

        context = {
            **self.admin_site.each_context(request),
            "title": "Báo cáo Doanh thu theo Ngày",
            "report_data": report_data,
            "overall": overall,
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "admin/orders/revenue_report.html", context)
