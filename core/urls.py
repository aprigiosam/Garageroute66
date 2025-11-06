from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "core"

urlpatterns = [
    path("login/", views.AuthLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="core:login"), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("ordens/", views.order_list, name="order_list"),
    path("ordens/nova/", views.order_create, name="order_create"),
    path("ordens/<int:pk>/", views.order_detail, name="order_detail"),
    path("ordens/<int:pk>/editar/", views.order_edit, name="order_edit"),
    path("ordens/<int:pk>/aprovacao/", views.order_approval, name="order_approval"),
    path("ordens/<int:pk>/execucao/", views.order_execution, name="order_execution"),
    path("ordens/<int:pk>/entrega/", views.order_checkout, name="order_checkout"),
    path("ordens/<int:pk>/recibo/", views.order_receipt, name="order_receipt"),
    path("orcamento/<str:token>/", views.public_order, name="public_order"),
]
