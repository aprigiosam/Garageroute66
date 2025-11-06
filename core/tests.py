from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Customer, ServiceOrder, Vehicle, ServiceItem, Payment, ServiceAttachment


class PublicApprovalTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="owner", email="owner@example.com", password="password123"
        )
        self.customer = Customer.objects.create(
            name="Cliente Teste",
            email="cliente@example.com",
            phone="+55 11999999999",
        )
        self.vehicle = Vehicle.objects.create(
            customer=self.customer,
            brand="Ford",
            model="Fiesta",
            plate="ABC1234",
        )
        self.order = ServiceOrder.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            issue_description="Barulho na suspensão",
            status=ServiceOrder.Status.WAITING_APPROVAL,
        )

    def test_public_token_expiration_revokes_and_logs(self):
        self.order.generate_public_token(force=True)
        original_history = self.order.status_history.count()
        self.order.public_token_expires_at = timezone.now() - timedelta(days=1)
        self.order.save(update_fields=["public_token_expires_at"])

        self.order.enforce_public_token_state()
        self.order.refresh_from_db()

        self.assertTrue(self.order.public_token_revoked)
        self.assertEqual(
            self.order.status_history.count(),
            original_history + 1,
        )
        self.assertIn(
            "expirado",
            self.order.status_history.latest("created_at").notes,
        )

    def test_public_approval_flow(self):
        self.order.generate_public_token(force=True)
        url = reverse("core:public_order", args=[self.order.public_token])
        response = self.client.post(
            url,
            {
                "decision": "approve",
                "approval_confirmed_by": "Fulano",
                "approval_total": "150.50",
                "approval_notes": "Pode seguir.",
                "agree": "on",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, ServiceOrder.Status.APPROVED)
        self.assertEqual(self.order.approval_confirmed_by, "Fulano")
        self.assertEqual(self.order.approval_total, Decimal("150.50"))
        self.assertTrue(
            self.order.status_history.filter(
                notes__icontains="via link público"
            ).exists()
        )

    def test_public_link_expired_view(self):
        self.order.generate_public_token(force=True)
        self.order.public_token_expires_at = timezone.now() - timedelta(hours=1)
        self.order.save(update_fields=["public_token_expires_at"])

        url = reverse("core:public_order", args=[self.order.public_token])
        response = self.client.get(url)
        self.assertContains(response, "não está mais disponível", status_code=200)
        self.order.refresh_from_db()
        self.assertTrue(self.order.public_token_revoked)


class CheckoutTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="owner2", email="owner2@example.com", password="password123"
        )
        self.customer = Customer.objects.create(name="Cliente Pagamento")
        self.vehicle = Vehicle.objects.create(
            customer=self.customer,
            brand="Fiat",
            model="Uno",
        )
        self.order = ServiceOrder.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            issue_description="Revisão completa",
            status=ServiceOrder.Status.READY,
        )
        ServiceItem.objects.create(
            order=self.order,
            description="Troca de óleo",
            quantity=1,
            unit_price=Decimal("100.00"),
        )
        self.client.force_login(self.user)

    def test_cannot_deliver_with_pending_balance(self):
        url = reverse("core:order_checkout", args=[self.order.pk])
        response = self.client.post(url, {"action": "deliver"}, follow=True)
        self.assertContains(response, "saldo pendente", status_code=200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, ServiceOrder.Status.READY)
        self.assertIsNone(self.order.delivered_at)

    def test_add_payment_and_deliver(self):
        url = reverse("core:order_checkout", args=[self.order.pk])
        response = self.client.post(
            url,
            {
                "action": "add_payment",
                "payment-amount": "100.00",
                "payment-method": Payment.Method.CASH,
                "payment-status": Payment.Status.CONFIRMED,
                "payment-paid_at": "",
                "payment-notes": "Pago em dinheiro",
                "receipts-TOTAL_FORMS": "1",
                "receipts-INITIAL_FORMS": "0",
                "receipts-MIN_NUM_FORMS": "0",
                "receipts-MAX_NUM_FORMS": "1000",
                "receipts-0-id": "",
                "receipts-0-category": ServiceAttachment.Category.RECEIPT,
                "receipts-0-description": "",
                "receipts-0-file": "",
            },
            follow=True,
        )
        self.assertContains(response, "Pagamento registrado", status_code=200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_paid, Decimal("100.00"))
        # deliver
        response = self.client.post(url, {"action": "deliver"}, follow=True)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, ServiceOrder.Status.DELIVERED)
        self.assertIsNotNone(self.order.delivered_at)

    def test_receipt_available_after_delivery(self):
        url = reverse("core:order_checkout", args=[self.order.pk])
        self.client.post(
            url,
            {
                "action": "add_payment",
                "payment-amount": "100.00",
                "payment-method": Payment.Method.CASH,
                "payment-status": Payment.Status.CONFIRMED,
                "payment-paid_at": "",
                "payment-notes": "",
                "receipts-TOTAL_FORMS": "1",
                "receipts-INITIAL_FORMS": "0",
                "receipts-MIN_NUM_FORMS": "0",
                "receipts-MAX_NUM_FORMS": "1000",
                "receipts-0-id": "",
                "receipts-0-category": ServiceAttachment.Category.RECEIPT,
                "receipts-0-description": "",
                "receipts-0-file": "",
            },
        )
        self.client.post(url, {"action": "deliver"})
        receipt_url = reverse("core:order_receipt", args=[self.order.pk])
        response = self.client.get(receipt_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recibo de Serviços")

    def test_receipt_blocks_when_not_delivered(self):
        self.order.status = ServiceOrder.Status.READY
        self.order.save(update_fields=["status"])
        receipt_url = reverse("core:order_receipt", args=[self.order.pk])
        response = self.client.get(receipt_url, follow=True)
        self.assertContains(response, "só fica disponível", status_code=200)
