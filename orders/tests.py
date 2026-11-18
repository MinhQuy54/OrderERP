from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Order


class OrderModelTest(TestCase):
    def _make_order(self, **kwargs):
        defaults = {
            "customer": "Nguyễn Thị Hoa",
            "item": "Nến thơm tinh dầu thiên nhiên AuraScent",
            "qty": 2,
            "rate": Decimal("150000.00"),
        }
        defaults.update(kwargs)
        return Order(**defaults)

    def test_tao_don_hang_thanh_cong(self):
        order = self._make_order(qty=3, rate=Decimal("200000.00"))
        order.save()
        self.assertIsNotNone(order.pk)
        self.assertEqual(order.amount, Decimal("600000.00"))
        self.assertEqual(order.status, Order.Status.MOI)

    def test_tu_dong_tinh_amount(self):
        order = self._make_order(qty=5, rate=Decimal("85000.50"))
        order.save()
        self.assertEqual(order.amount, Decimal("5") * Decimal("85000.50"))

    def test_trang_thai_mac_dinh_la_moi(self):
        order = self._make_order()
        order.save()
        self.assertEqual(order.status, "Mới")

    def test_loi_khi_qty_bang_0(self):
        order = self._make_order(qty=0)
        with self.assertRaises(ValidationError) as ctx:
            order.save()
        self.assertIn("qty", ctx.exception.message_dict)

    def test_loi_khi_rate_am(self):
        order = self._make_order(rate=Decimal("-1.00"))
        with self.assertRaises(ValidationError) as ctx:
            order.save()
        self.assertIn("rate", ctx.exception.message_dict)

    def test_loi_khi_rate_bang_0(self):
        order = self._make_order(rate=Decimal("0.00"))
        with self.assertRaises(ValidationError) as ctx:
            order.save()
        self.assertIn("rate", ctx.exception.message_dict)

    def test_chan_sua_don_da_giao(self):
        order = self._make_order(qty=1, rate=Decimal("100000.00"))
        order.save()
        Order.objects.filter(pk=order.pk).update(status=Order.Status.DA_GIAO)
        order.refresh_from_db()

        order.qty = 99
        with self.assertRaises(ValidationError) as ctx:
            order.save()
        self.assertIn("Đã giao", str(ctx.exception))

    def test_chan_sua_don_huy(self):
        order = self._make_order(qty=1, rate=Decimal("100000.00"))
        order.save()
        Order.objects.filter(pk=order.pk).update(status=Order.Status.HUY)
        order.refresh_from_db()

        order.customer = "Hacker"
        with self.assertRaises(ValidationError) as ctx:
            order.save()
        self.assertIn("Hủy", str(ctx.exception))

    def test_chan_doi_trang_thai_don_huy(self):
        order = self._make_order(qty=2, rate=Decimal("50000.00"))
        order.save()
        Order.objects.filter(pk=order.pk).update(status=Order.Status.HUY)
        order.refresh_from_db()

        order.status = Order.Status.MOI
        with self.assertRaises(ValidationError):
            order.save()


class OrderAPITest(APITestCase):
    def setUp(self):
        Order.objects.create(
            customer="Trần Minh",
            item="Nến thơm hoa nhài",
            qty=2,
            rate=Decimal("120000.00"),
            status=Order.Status.MOI,
        )
        Order.objects.filter(customer="Trần Minh").update(status=Order.Status.DA_GIAO)

        Order.objects.create(
            customer="Lê Thị Mai",
            item="Nến thơm lavender",
            qty=3,
            rate=Decimal("95000.00"),
            status=Order.Status.MOI,
        )
        Order.objects.filter(customer="Lê Thị Mai").update(status=Order.Status.DA_GIAO)

        Order.objects.create(
            customer="Phạm Văn Bình",
            item="Nến thơm sả chanh",
            qty=1,
            rate=Decimal("80000.00"),
        )

        Order.objects.create(
            customer="Hoàng Thu Thảo",
            item="Nến thơm bạc hà",
            qty=4,
            rate=Decimal("60000.00"),
            status=Order.Status.MOI,
        )
        Order.objects.filter(customer="Hoàng Thu Thảo").update(status=Order.Status.HUY)

    def test_api_lay_danh_sach_don_hang(self):
        url = "/api/orders/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)

    def test_api_tao_don_hang_thanh_cong(self):
        url = "/api/orders/"
        payload = {
            "customer": "Vũ Thanh Hà",
            "item": "Nến thơm tinh dầu hoa hồng",
            "qty": 2,
            "rate": "180000.00",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Decimal(response.data["amount"]),
            Decimal("360000.00"),
        )

    def test_api_loi_qty_bang_0(self):
        url = "/api/orders/"
        payload = {
            "customer": "Test User",
            "qty": 0,
            "rate": "100000.00",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_loi_rate_am(self):
        url = "/api/orders/"
        payload = {
            "customer": "Test User",
            "qty": 1,
            "rate": "-50000.00",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_chan_sua_don_da_giao(self):
        order = Order.objects.filter(status=Order.Status.DA_GIAO).first()
        url = f"/api/orders/{order.pk}/"
        response = self.client.patch(url, {"qty": 100}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Đã giao", str(response.data))

    def test_api_bao_cao_doanh_thu(self):
        url = "/api/orders/revenue-report/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        summary = response.data["summary"]
        self.assertEqual(summary["total_delivered_orders"], 2)

        expected_revenue = Decimal("240000.00") + Decimal("285000.00")
        self.assertEqual(
            Decimal(str(summary["total_revenue"])),
            expected_revenue,
        )

    def test_api_bao_cao_khong_tinh_don_moi_va_huy(self):
        url = "/api/orders/revenue-report/"
        response = self.client.get(url)
        summary = response.data["summary"]
        self.assertEqual(summary["total_delivered_orders"], 2)
