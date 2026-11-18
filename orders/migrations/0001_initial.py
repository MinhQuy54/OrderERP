# orders/migrations/0001_initial.py
"""Migration khởi tạo bảng Order."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "customer",
                    models.CharField(max_length=255, verbose_name="Tên khách hàng"),
                ),
                (
                    "item",
                    models.CharField(
                        default="Nến thơm tinh dầu thiên nhiên AuraScent",
                        max_length=500,
                        verbose_name="Sản phẩm",
                    ),
                ),
                (
                    "qty",
                    models.PositiveIntegerField(verbose_name="Số lượng"),
                ),
                (
                    "rate",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        verbose_name="Đơn giá (VNĐ)",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Tự động tính bằng Số lượng × Đơn giá",
                        max_digits=15,
                        verbose_name="Thành tiền (VNĐ)",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Mới", "Mới"),
                            ("Đã giao", "Đã giao"),
                            ("Hủy", "Hủy"),
                        ],
                        default="Mới",
                        max_length=20,
                        verbose_name="Trạng thái",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Ngày tạo đơn"
                    ),
                ),
            ],
            options={
                "verbose_name": "Đơn hàng",
                "verbose_name_plural": "Danh sách đơn hàng",
                "ordering": ["-created_at"],
            },
        ),
    ]

