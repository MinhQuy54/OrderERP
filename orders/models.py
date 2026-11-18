from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError


class Order(models.Model):
    class Status(models.TextChoices):
        MOI     = "Mới",     "Mới"
        DA_GIAO = "Đã giao", "Đã giao"
        HUY     = "Hủy",     "Hủy"

    LOCKED_STATUSES = {Status.DA_GIAO, Status.HUY}

    customer   = models.CharField(max_length=255, verbose_name="Tên khách hàng")
    item       = models.CharField(max_length=500, default="Nến thơm tinh dầu thiên nhiên AuraScent", verbose_name="Sản phẩm")
    qty        = models.PositiveIntegerField(verbose_name="Số lượng")
    rate       = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Đơn giá (VNĐ)")
    amount     = models.DecimalField(max_digits=15, decimal_places=2, blank=True, verbose_name="Thành tiền (VNĐ)")
    status     = models.CharField(max_length=20, choices=Status.choices, default=Status.MOI, verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo đơn")

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Danh sách đơn hàng"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"#{self.pk} — {self.customer} ({self.status})"

    def clean(self):
        errors = {}

        if self.qty is not None and self.qty <= 0:
            errors["qty"] = "Số lượng phải lớn hơn 0."

        if self.rate is not None and self.rate <= Decimal("0"):
            errors["rate"] = "Đơn giá phải lớn hơn 0."

        if self.pk:
            try:
                db = Order.objects.get(pk=self.pk)
            except Order.DoesNotExist:
                db = None

            if db and db.status in self.LOCKED_STATUSES:
                raise ValidationError(
                    f"Đơn hàng đã ở trạng thái «{db.status}» — không thể chỉnh sửa."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.qty and self.rate:
            self.amount = Decimal(str(self.qty)) * self.rate
        super().save(*args, **kwargs)
