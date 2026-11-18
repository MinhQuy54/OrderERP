from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "item",
            "qty",
            "rate",
            "amount",
            "status",
            "created_at",
        ]
        read_only_fields = ["amount", "created_at"]

    def validate(self, attrs):
        if self.instance is not None:
            if self.instance.status in Order.LOCKED_STATUSES:
                raise serializers.ValidationError(
                    f"Đơn hàng đã ở trạng thái «{self.instance.status}» — không thể chỉnh sửa."
                )
        return attrs


class RevenueReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=20, decimal_places=2)
