from __future__ import annotations

from decimal import Decimal

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory

from .models import (
    Customer,
    ServiceAttachment,
    ServiceItem,
    ServiceOrder,
    Payment,
    Vehicle,
)


class BaseBootstrapForm(forms.ModelForm):
    """Applies Bootstrap classes automatically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            base_class = "form-control"
            if isinstance(field.widget, forms.CheckboxInput):
                base_class = "form-check-input"
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                base_class = "form-select"
            field.widget.attrs["class"] = f"{css} {base_class}".strip()
            if not field.required and "placeholder" not in field.widget.attrs:
                field.widget.attrs["placeholder"] = "Opcional"


class CustomerForm(BaseBootstrapForm):
    class Meta:
        model = Customer
        fields = ["name", "document_id", "phone", "email", "address", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class VehicleForm(BaseBootstrapForm):
    class Meta:
        model = Vehicle
        fields = [
            "customer",
            "plate",
            "brand",
            "model",
            "year",
            "color",
            "vin",
            "mileage",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We'll supply the queryset when we use the form; keep it empty by default to avoid leaking inactive customers.
        self.fields["customer"].widget = forms.HiddenInput()


class QuickVehicleForm(BaseBootstrapForm):
    """Vehicle form without the customer field to compose new OS creation."""

    class Meta:
        model = Vehicle
        fields = ["plate", "brand", "model", "year", "color", "vin", "mileage", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class ServiceOrderForm(BaseBootstrapForm):
    class Meta:
        model = ServiceOrder
        fields = [
            "title",
            "issue_description",
            "priority",
            "status",
            "estimated_delivery",
            "internal_notes",
            "customer_notes",
        ]
        widgets = {
            "issue_description": forms.Textarea(attrs={"rows": 4}),
            "internal_notes": forms.Textarea(attrs={"rows": 3}),
            "customer_notes": forms.Textarea(attrs={"rows": 2}),
            "estimated_delivery": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].initial = ServiceOrder.Status.RECEIVED
        hidden_fields = ["title", "status", "estimated_delivery", "internal_notes", "customer_notes"]
        for field_name in hidden_fields:
            field = self.fields.get(field_name)
            if field:
                field.widget = forms.HiddenInput()
        if "title" in self.fields and not self.initial.get("title"):
            self.fields["title"].initial = "Ordem de Serviço"


class ServiceOrderDiagnosisForm(BaseBootstrapForm):
    class Meta:
        model = ServiceOrder
        fields = [
            "issue_description",
            "diagnosis_description",
            "internal_notes",
            "customer_notes",
            "priority",
        ]
        widgets = {
            "issue_description": forms.Textarea(attrs={"rows": 3}),
            "diagnosis_description": forms.Textarea(attrs={"rows": 4}),
            "internal_notes": forms.Textarea(attrs={"rows": 3}),
            "customer_notes": forms.Textarea(attrs={"rows": 2}),
        }


class ServiceItemForm(BaseBootstrapForm):
    class Meta:
        model = ServiceItem
        fields = ["description", "category", "quantity", "unit_price", "notes"]
        widgets = {
            "notes": forms.TextInput(attrs={"placeholder": "Observações"}),
        }


ServiceItemFormSet = inlineformset_factory(
    ServiceOrder,
    ServiceItem,
    form=ServiceItemForm,
    extra=1,
    can_delete=True,
)


class ServiceAttachmentForm(BaseBootstrapForm):
    class Meta:
        model = ServiceAttachment
        fields = ["category", "description", "file"]
        widgets = {
            "description": forms.TextInput(attrs={"placeholder": "Ex.: Foto frontal, Cupom 123"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].required = False


ServiceAttachmentFormSet = inlineformset_factory(
    ServiceOrder,
    ServiceAttachment,
    form=ServiceAttachmentForm,
    extra=1,
    can_delete=True,
)


class PaymentForm(BaseBootstrapForm):
    class Meta:
        model = Payment
        fields = ["amount", "method", "status", "paid_at", "notes"]
        widgets = {
            "notes": forms.TextInput(attrs={"placeholder": "Observações internas"}),
            "paid_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs.update({"min": "0.01", "step": "0.01"})
        self.fields["paid_at"].required = False


class PublicApprovalForm(forms.Form):
    approval_confirmed_by = forms.CharField(
        label="Seu nome completo",
        max_length=120,
    )
    approval_total = forms.DecimalField(
        label="Valor aprovado",
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.00"),
        help_text="Confirme o valor total aprovado. Se deixar em branco, será usado o valor calculado pela oficina.",
    )
    approval_notes = forms.CharField(
        label="Observações (opcional)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    agree = forms.BooleanField(
        label="Declaro que li e concordo com o orçamento apresentado.",
        required=False,
    )

    def __init__(self, *args, decision: str = "approve", **kwargs):
        self.decision = decision
        super().__init__(*args, **kwargs)
        self.fields["approval_total"].widget.attrs["step"] = "0.01"
        if self.decision != "approve":
            # Não exigir confirmação para rejeição
            self.fields["agree"].required = False
            self.fields["agree"].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        if self.decision == "approve":
            if not cleaned_data.get("agree"):
                self.add_error(
                    "agree",
                    "É necessário aceitar os termos para aprovar o orçamento.",
                )
        return cleaned_data


class ServiceOrderApprovalForm(BaseBootstrapForm):
    class Meta:
        model = ServiceOrder
        fields = [
            "approval_total",
            "approval_channel",
            "approval_confirmed_by",
            "approval_notes",
            "estimated_delivery",
        ]
        widgets = {
            "approval_notes": forms.Textarea(attrs={"rows": 3}),
            "estimated_delivery": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and not self.initial.get("approval_total"):
            self.fields["approval_total"].initial = self.instance.total_items
        self.fields["approval_total"].widget.attrs["min"] = "0"
        self.fields["approval_total"].widget.attrs["step"] = "0.01"
        if "estimated_delivery" in self.fields:
            self.fields["estimated_delivery"].required = False


class ServiceOrderExecutionForm(BaseBootstrapForm):
    class Meta:
        model = ServiceOrder
        fields = [
            "status",
            "execution_notes",
        ]
        widgets = {
            "execution_notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_statuses = [
            ServiceOrder.Status.APPROVED,
            ServiceOrder.Status.IN_PROGRESS,
            ServiceOrder.Status.READY,
        ]
        self.fields["status"].choices = [
            (value, label)
            for value, label in ServiceOrder.Status.choices
            if value in allowed_statuses
        ]


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css} form-control".strip()
