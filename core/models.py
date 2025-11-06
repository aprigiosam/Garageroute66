from __future__ import annotations

import logging
from decimal import Decimal
from datetime import timedelta
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract base model with creation and update timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Customer(TimeStampedModel):
    """Represents a garage customer."""

    name = models.CharField("Nome", max_length=120)
    document_id = models.CharField(
        "Documento",
        max_length=20,
        blank=True,
        help_text="CPF/CNPJ ou outro identificador",
    )
    phone = models.CharField("Telefone", max_length=25, blank=True)
    email = models.EmailField("E-mail", blank=True)
    address = models.CharField("Endereço", max_length=255, blank=True)
    notes = models.TextField("Observações", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self) -> str:
        return self.name


class Vehicle(TimeStampedModel):
    """Vehicle associated to a customer."""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="vehicles",
        verbose_name="Cliente",
    )
    plate = models.CharField("Placa", max_length=10, blank=True)
    brand = models.CharField("Marca", max_length=80)
    model = models.CharField("Modelo", max_length=80)
    year = models.PositiveIntegerField("Ano", null=True, blank=True)
    color = models.CharField("Cor", max_length=40, blank=True)
    vin = models.CharField("Chassi", max_length=32, blank=True)
    mileage = models.PositiveIntegerField("Quilometragem", null=True, blank=True)
    notes = models.TextField("Observações", blank=True)

    class Meta:
        ordering = ["plate", "brand", "model"]
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "plate"],
                condition=~Q(plate=""),
                name="unique_vehicle_plate_per_customer",
            )
        ]

    def __str__(self) -> str:
        descriptor = self.plate or f"{self.brand} {self.model}"
        return f"{descriptor} - {self.customer.name}"


class ServiceOrder(TimeStampedModel):
    """Main entity representing the work order."""

    class Status(models.TextChoices):
        RECEIVED = "received", "Recebida"
        DIAGNOSIS = "diagnosis", "Em diagnóstico"
        WAITING_APPROVAL = "waiting_approval", "Aguardando aprovação"
        APPROVED = "approved", "Aprovada"
        IN_PROGRESS = "in_progress", "Em execução"
        READY = "ready", "Pronta para entrega"
        DELIVERED = "delivered", "Finalizada"
        CANCELED = "canceled", "Cancelada"

    class Priority(models.TextChoices):
        LOW = "low", "Baixa"
        NORMAL = "normal", "Normal"
        HIGH = "high", "Alta"
        URGENT = "urgent", "Urgente"

    class ApprovalChannel(models.TextChoices):
        IN_PERSON = "in_person", "Presencial"
        PHONE = "phone", "Telefone"
        WHATSAPP = "whatsapp", "WhatsApp"
        EMAIL = "email", "E-mail"
        OTHER = "other", "Outro"
        PUBLIC_LINK = "public_link", "Link público"

    number = models.CharField(
        "Número da OS",
        max_length=20,
        unique=True,
        editable=False,
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Cliente",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Veículo",
    )
    title = models.CharField("Título", max_length=120, default="Ordem de Serviço")
    issue_description = models.TextField("Descrição do problema")
    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
    )
    priority = models.CharField(
        "Prioridade",
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    estimated_delivery = models.DateTimeField(
        "Previsão de entrega", null=True, blank=True
    )
    delivered_at = models.DateTimeField("Data de entrega", null=True, blank=True)
    diagnosis_description = models.TextField(
        "Diagnóstico técnico", blank=True
    )
    diagnosis_completed_at = models.DateTimeField(
        "Diagnóstico concluído em", null=True, blank=True
    )
    public_token = models.CharField(
        "Token público",
        max_length=64,
        unique=True,
        blank=True,
        null=True,
    )
    public_token_created_at = models.DateTimeField(
        "Token gerado em", null=True, blank=True
    )
    public_token_expires_at = models.DateTimeField(
        "Token expira em", null=True, blank=True
    )
    public_token_revoked = models.BooleanField(
        "Token revogado", default=False
    )
    approval_total = models.DecimalField(
        "Valor aprovado",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    approval_channel = models.CharField(
        "Canal de aprovação",
        max_length=20,
        choices=ApprovalChannel.choices,
        blank=True,
    )
    approval_notes = models.TextField(
        "Notas da aprovação",
        blank=True,
    )
    approval_confirmed_at = models.DateTimeField(
        "Aprovação registrada em", null=True, blank=True
    )
    approval_confirmed_by = models.CharField(
        "Aprovado por",
        max_length=120,
        blank=True,
        help_text="Nome do cliente responsável pela aprovação.",
    )
    approval_recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_orders",
        verbose_name="Aprovação registrada por",
    )
    execution_started_at = models.DateTimeField(
        "Execução iniciada em", null=True, blank=True
    )
    execution_completed_at = models.DateTimeField(
        "Execução finalizada em", null=True, blank=True
    )
    execution_notes = models.TextField(
        "Notas da execução", blank=True
    )
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_orders",
        verbose_name="Responsável",
    )
    internal_notes = models.TextField("Observações internas", blank=True)
    customer_notes = models.TextField("Notas para o cliente", blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ordem de Serviço"
        verbose_name_plural = "Ordens de Serviço"

    def __str__(self) -> str:
        return f"OS {self.number} - {self.vehicle}"

    @classmethod
    def generate_number(cls) -> str:
        today_str = timezone.localdate().strftime("%Y%m%d")
        last_order = (
            cls.objects.filter(number__startswith=today_str)
            .order_by("-number")
            .first()
        )
        if not last_order:
            sequence = 1
        else:
            try:
                sequence = int(last_order.number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                sequence = 1
        return f"{today_str}-{sequence:03d}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.generate_number()
        if self.vehicle:
            self.customer = self.vehicle.customer
        super().save(*args, **kwargs)

    @property
    def total_items(self) -> Decimal:
        return sum((item.total for item in self.items.all()), Decimal("0.00"))

    @property
    def total_paid(self) -> Decimal:
        confirmed = self.payments.filter(status=Payment.Status.CONFIRMED)
        return sum((payment.amount for payment in confirmed), Decimal("0.00"))

    @property
    def balance(self) -> Decimal:
        return self.total_items - self.total_paid

    def generate_public_token(self, force: bool = False) -> str:
        """Generate or refresh the public approval token."""
        if self.pk is None:
            raise ValueError("Save the service order before generating a public token.")

        if not force and self.public_token and not self.public_token_revoked:
            return self.public_token

        self.public_token = uuid.uuid4().hex
        self.public_token_created_at = timezone.now()
        expiration_days = getattr(
            settings,
            "PUBLIC_APPROVAL_LINK_EXPIRATION_DAYS",
            3,
        )
        self.public_token_expires_at = self.public_token_created_at + timedelta(days=expiration_days)
        self.public_token_revoked = False
        self.save(
            update_fields=[
                "public_token",
                "public_token_created_at",
                "public_token_expires_at",
                "public_token_revoked",
            ]
        )
        return self.public_token

    def get_public_approval_path(self) -> str | None:
        if not self.public_token or self.public_token_revoked:
            return None
        return reverse("core:public_order", args=[self.public_token])

    def revoke_public_token(self) -> None:
        """Invalidate the current public token."""
        if not self.public_token:
            return
        self.public_token_revoked = True
        self.save(update_fields=["public_token_revoked"])

    def is_public_token_valid(self) -> bool:
        if not self.public_token or self.public_token_revoked:
            return False
        if self.public_token_expires_at and timezone.now() > self.public_token_expires_at:
            return False
        return self.status == self.Status.WAITING_APPROVAL

    def enforce_public_token_state(self) -> None:
        """Check for expiration and revoke token if needed, logging the event."""
        if (
            self.public_token
            and not self.public_token_revoked
            and self.public_token_expires_at
            and timezone.now() > self.public_token_expires_at
        ):
            self.public_token_revoked = True
            self.save(update_fields=["public_token_revoked"])
            self.status_history.create(
                from_status=self.status,
                to_status=self.status,
                changed_by=None,
                notes="Link público expirado automaticamente.",
            )
            logger.info(
                "Public approval link for order %s expired and was revoked.", self.number
            )


def attachment_upload_to(instance: "ServiceAttachment", filename: str) -> str:
    ext = filename.split(".")[-1] if "." in filename else ""
    identifier = uuid.uuid4()
    category = instance.category
    order_number = instance.order.number if instance.order_id else "pending"
    if ext:
        return f"service_orders/{order_number}/{category}/{identifier}.{ext}"
    return f"service_orders/{order_number}/{category}/{identifier}"


class ServiceItem(TimeStampedModel):
    """Items of a service order (labor, parts, etc.)."""

    class Category(models.TextChoices):
        LABOR = "labor", "Mão de obra"
        PART = "part", "Peça"
        SERVICE = "service", "Serviço terceirizado"
        OTHER = "other", "Outros"

    order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Ordem de serviço",
    )
    description = models.CharField("Descrição", max_length=150)
    category = models.CharField(
        "Categoria",
        max_length=20,
        choices=Category.choices,
        default=Category.LABOR,
    )
    quantity = models.DecimalField(
        "Quantidade",
        max_digits=7,
        decimal_places=2,
        default=Decimal("1.00"),
    )
    unit_price = models.DecimalField(
        "Valor unitário",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    notes = models.CharField("Observações", max_length=255, blank=True)

    class Meta:
        verbose_name = "Item da OS"
        verbose_name_plural = "Itens da OS"

    def __str__(self) -> str:
        return f"{self.description} ({self.order.number})"

    @property
    def total(self) -> Decimal:
        return (self.quantity or Decimal("0.00")) * (self.unit_price or Decimal("0.00"))


class Payment(TimeStampedModel):
    """Payment records related to a service order."""

    class Method(models.TextChoices):
        CASH = "cash", "Dinheiro"
        CARD = "card", "Cartão"
        PIX = "pix", "PIX"
        BANK_TRANSFER = "bank_transfer", "Transferência"
        OTHER = "other", "Outro"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        CONFIRMED = "confirmed", "Confirmado"
        CANCELLED = "cancelled", "Cancelado"

    order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Ordem de serviço",
    )
    method = models.CharField(
        "Forma de pagamento",
        max_length=20,
        choices=Method.choices,
        default=Method.CASH,
    )
    amount = models.DecimalField("Valor", max_digits=10, decimal_places=2)
    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    paid_at = models.DateTimeField("Data do pagamento", null=True, blank=True)
    notes = models.CharField("Observações", max_length=255, blank=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="received_payments",
        null=True,
        blank=True,
        verbose_name="Recebido por",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"

    def __str__(self) -> str:
        return f"Pagamento {self.amount} - {self.order.number}"

    def save(self, *args, **kwargs):
        if self.status == self.Status.CONFIRMED and not self.paid_at:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)


class ServiceAttachment(TimeStampedModel):
    """Files linked to the service order, such as vehicle photos or receipts."""

    class Category(models.TextChoices):
        VEHICLE_PHOTO = "vehicle_photo", "Foto do veículo"
        RECEIPT = "receipt", "Comprovante / cupom fiscal"

    order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Ordem de serviço",
    )
    category = models.CharField(
        "Categoria",
        max_length=20,
        choices=Category.choices,
        default=Category.VEHICLE_PHOTO,
    )
    file = models.FileField("Arquivo", upload_to=attachment_upload_to)
    description = models.CharField(
        "Descrição", max_length=120, blank=True, help_text="Ex.: detalhe do dano, número do cupom."
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Enviado por",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Anexo da OS"
        verbose_name_plural = "Anexos da OS"

    def __str__(self) -> str:
        return f"{self.get_category_display()} - {self.order.number}"

    @property
    def is_image(self) -> bool:
        if not self.file:
            return False
        name = self.file.name.lower()
        return name.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))


class StatusHistory(TimeStampedModel):
    """Keeps a timeline of status changes for the order."""

    order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Ordem de serviço",
    )
    from_status = models.CharField(
        "Status anterior",
        max_length=20,
        choices=ServiceOrder.Status.choices,
        blank=True,
    )
    to_status = models.CharField(
        "Status atual",
        max_length=20,
        choices=ServiceOrder.Status.choices,
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Alterado por",
    )
    notes = models.CharField("Observações", max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Histórico de status"
        verbose_name_plural = "Histórico de status"

    def __str__(self) -> str:
        return f"{self.order.number}: {self.from_status} → {self.to_status}"
logger = logging.getLogger(__name__)
