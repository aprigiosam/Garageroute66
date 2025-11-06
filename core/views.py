from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from urllib.parse import quote

from .forms import (
    CustomerForm,
    LoginForm,
    QuickVehicleForm,
    ServiceAttachmentFormSet,
    ServiceItemFormSet,
    PublicApprovalForm,
    ServiceOrderApprovalForm,
    ServiceOrderDiagnosisForm,
    ServiceOrderExecutionForm,
    ServiceOrderForm,
    PaymentForm,
)
from .models import Customer, ServiceAttachment, ServiceOrder, Vehicle, Payment


def _build_public_link(request, order: ServiceOrder) -> str | None:
    path = order.get_public_approval_path()
    if not path:
        return None
    return request.build_absolute_uri(path)


def _send_public_link_email(request, order: ServiceOrder, link: str) -> bool:
    if not order.customer.email:
        return False
    subject = f"Orçamento da ordem {order.number}"
    expiration = (
        order.public_token_expires_at.strftime("%d/%m/%Y %H:%M")
        if order.public_token_expires_at
        else "brevemente"
    )
    message = (
        f"Olá {order.customer.name},\n\n"
        f"A oficina encaminhou o orçamento para a ordem de serviço {order.number}.\n"
        f"Acesse o link abaixo para aprovar ou recusar:\n\n"
        f"{link}\n\n"
        f"O link expira em {expiration}.\n\n"
        "Qualquer dúvida, entre em contato com a oficina.\n"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@minhaoficina.local")
    send_mail(
        subject,
        message,
        from_email,
        [order.customer.email],
        fail_silently=True,
    )
    return True


def _build_whatsapp_url(order: ServiceOrder, link: str) -> str | None:
    if not order.customer.phone or not link:
        return None
    digits = "".join(filter(str.isdigit, order.customer.phone))
    if not digits:
        return None
    if digits.startswith("0"):
        digits = digits[1:]
    if len(digits) < 10:
        return None
    message = (
        f"Olá {order.customer.name}, segue o link para aprovar a OS {order.number}: {link}"
    )
    return f"https://wa.me/{digits}?text={quote(message)}"


class AuthLoginView(LoginView):
    template_name = "registration/login.html"
    form_class = LoginForm


@login_required
def dashboard(request):
    """Simple overview with key indicators for the mechanic/owner."""

    orders = ServiceOrder.objects.select_related("vehicle", "customer")
    open_orders = orders.exclude(status=ServiceOrder.Status.DELIVERED).count()
    awaiting_approval = orders.filter(status=ServiceOrder.Status.WAITING_APPROVAL).count()
    in_progress = orders.filter(status=ServiceOrder.Status.IN_PROGRESS).count()
    finished = orders.filter(status=ServiceOrder.Status.DELIVERED).count()

    status_breakdown = (
        orders.values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )

    context = {
        "open_orders": open_orders,
        "awaiting_approval": awaiting_approval,
        "in_progress": in_progress,
        "finished": finished,
        "status_breakdown": status_breakdown,
        "recent_orders": orders.order_by("-created_at")[:5],
    }
    return render(request, "core/dashboard.html", context)


@login_required
def order_list(request):
    """Lists service orders with quick filters."""

    orders = ServiceOrder.objects.select_related("vehicle", "customer")

    status = request.GET.get("status")
    if status:
        orders = orders.filter(status=status)

    priority = request.GET.get("priority")
    if priority:
        orders = orders.filter(priority=priority)

    search = request.GET.get("q")
    if search:
        orders = orders.filter(
            Q(number__icontains=search)
            | Q(vehicle__plate__icontains=search)
            | Q(vehicle__model__icontains=search)
            | Q(customer__name__icontains=search)
        )

    context = {
        "orders": orders.order_by("-created_at"),
        "selected_status": status,
        "selected_priority": priority,
        "search": search or "",
    }
    return render(request, "core/order_list.html", context)


@login_required
def order_detail(request, pk: int):
    order = get_object_or_404(
        ServiceOrder.objects.select_related("vehicle", "customer").prefetch_related("items", "payments", "attachments"),
        pk=pk,
    )
    order.enforce_public_token_state()
    public_url = _build_public_link(request, order)
    whatsapp_url = _build_whatsapp_url(order, public_url) if public_url else None
    context = {
        "order": order,
        "public_url": public_url,
        "whatsapp_url": whatsapp_url,
        "public_token_valid": order.is_public_token_valid(),
        "can_manage_execution": order.status
        in {
            ServiceOrder.Status.APPROVED,
            ServiceOrder.Status.IN_PROGRESS,
            ServiceOrder.Status.READY,
        },
        "can_manage_checkout": order.status
        in {
            ServiceOrder.Status.READY,
            ServiceOrder.Status.DELIVERED,
        },
    }
    return render(request, "core/order_detail.html", context)


@login_required
@transaction.atomic
def order_edit(request, pk: int):
    """Diagnóstico e preparação do orçamento da OS."""

    order = get_object_or_404(
        ServiceOrder.objects.select_related("vehicle", "customer"),
        pk=pk,
    )
    form = ServiceOrderDiagnosisForm(prefix="order", instance=order)
    items_formset = ServiceItemFormSet(prefix="items", instance=order)
    attachments_formset = ServiceAttachmentFormSet(prefix="attachments", instance=order)

    if request.method == "POST":
        previous_status = order.status
        form = ServiceOrderDiagnosisForm(
            request.POST,
            prefix="order",
            instance=order,
        )
        items_formset = ServiceItemFormSet(
            request.POST,
            prefix="items",
            instance=order,
        )
        attachments_formset = ServiceAttachmentFormSet(
            request.POST,
            request.FILES,
            prefix="attachments",
            instance=order,
        )

        if form.is_valid() and items_formset.is_valid() and attachments_formset.is_valid():
            order = form.save(commit=False)
            action = request.POST.get("action")

            if action == "send_for_approval":
                order.status = ServiceOrder.Status.WAITING_APPROVAL
                order.approval_total = order.total_items
                if not order.diagnosis_completed_at:
                    order.diagnosis_completed_at = timezone.now()
            elif order.status in (
                ServiceOrder.Status.RECEIVED,
                ServiceOrder.Status.DIAGNOSIS,
            ):
                order.status = ServiceOrder.Status.DIAGNOSIS

            order.save()
            if order.status == ServiceOrder.Status.WAITING_APPROVAL:
                order.generate_public_token()
                public_link = _build_public_link(request, order)
                if public_link and _send_public_link_email(request, order, public_link):
                    messages.info(
                        request,
                        "Orçamento enviado por e-mail para o cliente.",
                    )
                else:
                    messages.warning(
                        request,
                        "Link público gerado. Copie e compartilhe com o cliente para aprovação.",
                    )
            items_formset.save()

            attachments = attachments_formset.save(commit=False)
            for attachment in attachments:
                if not attachment.uploaded_by:
                    attachment.uploaded_by = request.user if request.user.is_authenticated else None
                attachment.save()
            for deleted in attachments_formset.deleted_objects:
                deleted.delete()

            if previous_status != order.status:
                order.status_history.create(
                    from_status=previous_status,
                    to_status=order.status,
                    changed_by=request.user,
                    notes="Status atualizado na etapa de diagnóstico.",
                )

            messages.success(request, "Diagnóstico salvo com sucesso.")

            if action == "send_for_approval":
                return redirect("core:order_detail", pk=order.pk)
            return redirect("core:order_edit", pk=order.pk)

        messages.error(request, "Revise os dados informados antes de salvar.")

    context = {
        "order": order,
        "form": form,
        "items_formset": items_formset,
        "attachments_formset": attachments_formset,
    }
    return render(request, "core/order_edit.html", context)


@login_required
@transaction.atomic
def order_approval(request, pk: int):
    """Handles approval workflow after diagnosis is sent to client."""

    order = get_object_or_404(
        ServiceOrder.objects.select_related("vehicle__customer"),
        pk=pk,
    )
    order.enforce_public_token_state()
    form = ServiceOrderApprovalForm(prefix="order", instance=order)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "regenerate_link":
            order.generate_public_token(force=True)
            link = _build_public_link(request, order)
            if link and _send_public_link_email(request, order, link):
                messages.success(request, "Link renovado e enviado ao cliente por e-mail.")
            else:
                messages.success(request, "Novo link público gerado com sucesso.")
            return redirect("core:order_approval", pk=order.pk)
        if action == "revoke_link":
            order.revoke_public_token()
            messages.info(request, "Link público revogado.")
            return redirect("core:order_approval", pk=order.pk)

        previous_status = order.status
        form = ServiceOrderApprovalForm(
            request.POST,
            prefix="order",
            instance=order,
        )
        if form.is_valid():
            order = form.save(commit=False)

            if action == "approve":
                order.status = ServiceOrder.Status.APPROVED
                order.approval_confirmed_at = order.approval_confirmed_at or timezone.now()
                order.approval_recorded_by = request.user
                if not order.approval_channel:
                    order.approval_channel = ServiceOrder.ApprovalChannel.IN_PERSON
                if order.approval_total is None:
                    order.approval_total = order.total_items
                success_message = "Ordem aprovada com sucesso."
            elif action == "reject":
                order.status = ServiceOrder.Status.CANCELED
                order.approval_confirmed_at = timezone.now()
                order.approval_recorded_by = request.user
                if not order.approval_channel:
                    order.approval_channel = ServiceOrder.ApprovalChannel.IN_PERSON
                success_message = "Ordem marcada como cancelada pelo cliente."
            elif action == "reopen":
                order.status = ServiceOrder.Status.DIAGNOSIS
                order.approval_confirmed_at = None
                order.approval_recorded_by = None
                success_message = "Ordem reaberta para ajustes no diagnóstico."
            else:
                success_message = "Informações de aprovação salvas."

            order.save()
            if order.status == ServiceOrder.Status.WAITING_APPROVAL and not order.public_token:
                order.generate_public_token()

            if previous_status != order.status:
                order.status_history.create(
                    from_status=previous_status,
                    to_status=order.status,
                    changed_by=request.user,
                    notes="Status atualizado na etapa de aprovação.",
                )

            messages.success(request, success_message)
            if action == "reopen":
                return redirect("core:order_edit", pk=order.pk)
            return redirect("core:order_detail", pk=order.pk)

        messages.error(request, "Revise os dados informados antes de concluir a aprovação.")

    public_url = _build_public_link(request, order)
    whatsapp_url = _build_whatsapp_url(order, public_url) if public_url else None
    context = {
        "order": order,
        "form": form,
        "public_url": public_url,
        "whatsapp_url": whatsapp_url,
    }
    return render(request, "core/order_approval.html", context)


@login_required
@transaction.atomic
def order_execution(request, pk: int):
    """Manage execution stage of the service order."""

    order = get_object_or_404(
        ServiceOrder.objects.select_related("vehicle__customer"),
        pk=pk,
    )

    if order.status not in {
        ServiceOrder.Status.APPROVED,
        ServiceOrder.Status.IN_PROGRESS,
        ServiceOrder.Status.READY,
    }:
        messages.error(
            request,
            "A execução só pode ser gerenciada para ordens aprovadas ou em execução.",
        )
        return redirect("core:order_detail", pk=order.pk)

    form = ServiceOrderExecutionForm(prefix="order", instance=order)
    attachments_formset = ServiceAttachmentFormSet(
        prefix="attachments",
        instance=order,
        queryset=order.attachments.exclude(
            category=ServiceAttachment.Category.RECEIPT
        ),
    )

    if request.method == "POST":
        form = ServiceOrderExecutionForm(
            request.POST,
            prefix="order",
            instance=order,
        )
        attachments_formset = ServiceAttachmentFormSet(
            request.POST,
            request.FILES,
            prefix="attachments",
            instance=order,
            queryset=order.attachments.exclude(
                category=ServiceAttachment.Category.RECEIPT
            ),
        )

        if form.is_valid() and attachments_formset.is_valid():
            previous_status = order.status
            order = form.save(commit=False)
            if order.status == ServiceOrder.Status.IN_PROGRESS and not order.execution_started_at:
                order.execution_started_at = timezone.now()
            if order.status == ServiceOrder.Status.READY:
                order.execution_completed_at = order.execution_completed_at or timezone.now()
            if order.status == ServiceOrder.Status.APPROVED:
                order.execution_started_at = None
                order.execution_completed_at = None
            order.save()

            attachments = attachments_formset.save(commit=False)
            for attachment in attachments:
                if not attachment.file:
                    continue
                if not attachment.uploaded_by:
                    attachment.uploaded_by = request.user
                attachment.category = ServiceAttachment.Category.VEHICLE_PHOTO
                attachment.save()
            for deleted in attachments_formset.deleted_objects:
                deleted.delete()

            if previous_status != order.status:
                order.status_history.create(
                    from_status=previous_status,
                    to_status=order.status,
                    changed_by=request.user,
                    notes="Status atualizado durante a execução.",
                )

            messages.success(request, "Dados da execução atualizados com sucesso.")
            return redirect("core:order_detail", pk=order.pk)

        messages.error(request, "Revise os dados destacados antes de salvar.")

    context = {
        "order": order,
        "form": form,
        "attachments_formset": attachments_formset,
    }
    return render(request, "core/order_execution.html", context)


@login_required
@transaction.atomic
def order_checkout(request, pk: int):
    """Handle payments and delivery of the service order."""

    order = get_object_or_404(
        ServiceOrder.objects.select_related("vehicle__customer"),
        pk=pk,
    )

    if order.status not in {
        ServiceOrder.Status.READY,
        ServiceOrder.Status.DELIVERED,
    }:
        messages.error(
            request,
            "A finalização só pode ser acessada quando a OS está pronta para entrega.",
        )
        return redirect("core:order_detail", pk=order.pk)

    payment_form = PaymentForm(prefix="payment")
    receipts_queryset = order.attachments.filter(
        category=ServiceAttachment.Category.RECEIPT
    )
    receipts_formset = ServiceAttachmentFormSet(
        prefix="receipts",
        instance=order,
        queryset=receipts_queryset,
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_payment":
            payment_form = PaymentForm(request.POST, prefix="payment")
            if payment_form.is_valid():
                payment = payment_form.save(commit=False)
                payment.order = order
                if payment.status == Payment.Status.CONFIRMED and not payment.paid_at:
                    payment.paid_at = timezone.now()
                if not payment.received_by:
                    payment.received_by = request.user
                payment.save()

                messages.success(request, "Pagamento registrado com sucesso.")
                return redirect("core:order_checkout", pk=order.pk)
            messages.error(request, "Revise os dados do pagamento informado.")

        elif action == "update_receipts":
            receipts_formset = ServiceAttachmentFormSet(
                request.POST,
                request.FILES,
                prefix="receipts",
                instance=order,
                queryset=receipts_queryset,
            )
            if receipts_formset.is_valid():
                attachments = receipts_formset.save(commit=False)
                for attachment in attachments:
                    if not attachment.file:
                        continue
                    if not attachment.uploaded_by:
                        attachment.uploaded_by = request.user
                    attachment.category = ServiceAttachment.Category.RECEIPT
                    attachment.save()
                for deleted in receipts_formset.deleted_objects:
                    deleted.delete()
                messages.success(request, "Comprovantes atualizados.")
                return redirect("core:order_checkout", pk=order.pk)
            messages.error(request, "Revise os dados dos anexos.")

        elif action == "deliver":
            if order.balance > Decimal("0.00"):
                messages.error(
                    request,
                    "Ainda existe saldo pendente. Registre todos os pagamentos antes de liberar o veículo.",
                )
            else:
                previous_status = order.status
                order.status = ServiceOrder.Status.DELIVERED
                order.delivered_at = timezone.now()
                order.save()
                order.status_history.create(
                    from_status=previous_status,
                    to_status=order.status,
                    changed_by=request.user,
                    notes="Veículo liberado após confirmação de pagamento.",
                )
                messages.success(request, "OS concluída e veículo liberado ao cliente.")
                return redirect("core:order_detail", pk=order.pk)

        elif action == "reopen_ready":
            previous_status = order.status
            order.status = ServiceOrder.Status.READY
            order.delivered_at = None
            order.save(update_fields=["status", "delivered_at"])
            order.status_history.create(
                from_status=previous_status,
                to_status=order.status,
                changed_by=request.user,
                notes="Entrega desfeita para ajustes.",
            )
            messages.info(request, "Status ajustado para 'Pronta para entrega'.")
            return redirect("core:order_checkout", pk=order.pk)

    context = {
        "order": order,
        "payment_form": payment_form,
        "receipts_formset": receipts_formset,
    }
    return render(request, "core/order_checkout.html", context)


@login_required
def order_receipt(request, pk: int):
    """Render a printable receipt for delivered orders."""

    order = get_object_or_404(
        ServiceOrder.objects.select_related("vehicle__customer").prefetch_related("items", "payments"),
        pk=pk,
    )

    if order.status != ServiceOrder.Status.DELIVERED:
        messages.error(
            request,
            "O recibo só fica disponível quando a ordem está finalizada.",
        )
        return redirect("core:order_detail", pk=order.pk)

    context = {
        "order": order,
        "payments": order.payments.filter(status=Payment.Status.CONFIRMED),
        "total_itens": order.total_items,
        "total_pago": order.total_paid,
        "usuario": request.user,
    }
    return render(request, "core/order_receipt.html", context)


@login_required
@transaction.atomic
def order_create(request):
    """Create a service order with optional inline customer/vehicle creation."""

    existing_customers = Customer.objects.order_by("name")
    existing_vehicles = Vehicle.objects.select_related("customer").order_by("plate")

    customer_form = CustomerForm(prefix="customer")
    vehicle_form = QuickVehicleForm(prefix="vehicle")
    order_form = ServiceOrderForm(prefix="order")

    if request.method == "POST":
        order_form = ServiceOrderForm(request.POST, prefix="order")
        customer_form = CustomerForm(request.POST, prefix="customer")
        vehicle_form = QuickVehicleForm(request.POST, prefix="vehicle")

        customer: Customer | None = None
        vehicle: Vehicle | None = None
        existing_vehicle_id = request.POST.get("existing_vehicle")
        existing_customer_id = request.POST.get("existing_customer")

        if existing_vehicle_id:
            vehicle = get_object_or_404(Vehicle, pk=existing_vehicle_id)
            customer = vehicle.customer
        else:
            if existing_customer_id:
                customer = get_object_or_404(Customer, pk=existing_customer_id)
            else:
                if customer_form.is_valid():
                    customer = customer_form.save()
                else:
                    messages.error(request, "Revise os dados do cliente para continuar.")

            if customer and vehicle_form.is_valid():
                vehicle = vehicle_form.save(commit=False)
                vehicle.customer = customer
                vehicle.save()
            elif not existing_customer_id:
                messages.error(request, "Informe os dados do veículo para continuar.")

        if customer and vehicle and order_form.is_valid():
            order = order_form.save(commit=False)
            order.vehicle = vehicle
            order.customer = customer
            if not order.responsible:
                order.responsible = request.user
            order.save()
            order.status_history.create(
                from_status="",
                to_status=order.status,
                changed_by=request.user if request.user.is_authenticated else None,
                notes="OS criada pelo painel",
            )
            messages.success(
                request,
                f"Ordem de serviço {order.number} criada com sucesso!",
            )
            return redirect(reverse("core:order_detail", args=[order.pk]))
        else:
            # preserve selected options so the template can re-render properly
            context = {
                "order_form": order_form,
                "customer_form": customer_form,
                "vehicle_form": vehicle_form,
                "existing_customers": existing_customers,
                "existing_vehicles": existing_vehicles,
                "selected_customer": existing_customer_id,
                "selected_vehicle": existing_vehicle_id,
                "issue_priority_fields": {"issue_description", "priority"},
            }
            return render(request, "core/order_create.html", context)

    context = {
        "order_form": order_form,
        "customer_form": customer_form,
        "vehicle_form": vehicle_form,
        "existing_customers": existing_customers,
        "existing_vehicles": existing_vehicles,
        "selected_customer": None,
        "selected_vehicle": None,
        "issue_priority_fields": {"issue_description", "priority"},
    }
    return render(request, "core/order_create.html", context)


def public_order(request, token: str):
    """Public-facing view for customers to approve or reject a service order."""

    order = get_object_or_404(
        ServiceOrder.objects.select_related("vehicle__customer").prefetch_related("items", "attachments"),
        public_token=token,
    )

    order.enforce_public_token_state()
    order.refresh_from_db(fields=["public_token_revoked"])
    token_valid = order.is_public_token_valid()
    is_waiting = order.status == ServiceOrder.Status.WAITING_APPROVAL and token_valid
    decision = request.POST.get("decision", "approve")
    success = False
    success_message = ""
    form = None

    if request.method == "POST" and is_waiting:
        form = PublicApprovalForm(request.POST, decision=decision)
        if decision not in {"approve", "reject"}:
            form.add_error(None, "Ação inválida.")
        if form.is_valid():
            previous_status = order.status
            approval_total = form.cleaned_data.get("approval_total") or order.total_items
            approval_notes = form.cleaned_data.get("approval_notes")
            approval_confirmed_by = form.cleaned_data.get("approval_confirmed_by")

            order.approval_total = approval_total
            order.approval_notes = approval_notes or ""
            order.approval_confirmed_by = approval_confirmed_by
            order.approval_channel = ServiceOrder.ApprovalChannel.PUBLIC_LINK
            order.approval_confirmed_at = timezone.now()
            order.approval_recorded_by = None

            if decision == "approve":
                order.status = ServiceOrder.Status.APPROVED
                success_message = "Obrigado! O orçamento foi aprovado com sucesso."
            else:
                order.status = ServiceOrder.Status.CANCELED
                success_message = "Orçamento marcado como não aprovado. A oficina será notificada."

            order.save()
            order.status_history.create(
                from_status=previous_status,
                to_status=order.status,
                changed_by=None,
                notes="Status atualizado via link público.",
            )
            is_waiting = False
            success = True
        else:
            success_message = "Corrija os dados destacados antes de enviar sua resposta."
    else:
        initial_total = order.approval_total or order.total_items
        form = PublicApprovalForm(initial={"approval_total": initial_total}) if is_waiting else None

    if not token_valid and not success_message:
        success_message = "Este link não está mais disponível. Solicite um novo link à oficina."

    vehicle_photos = order.attachments.filter(
        category=ServiceAttachment.Category.VEHICLE_PHOTO
    )

    context = {
        "order": order,
        "form": form if is_waiting else None,
        "is_waiting": is_waiting,
        "success": success,
        "message": success_message,
        "decision": decision,
        "token_valid": token_valid,
        "vehicle_photos": vehicle_photos,
    }
    return render(request, "core/order_public.html", context)
