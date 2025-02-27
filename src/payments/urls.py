from django.urls import path

from .views import (CancelView, ItemDetailView, OrderDetailView,
                    OrderPaymentView, PaymentsView, SuccessView)

urlpatterns = [
    path('item/<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('buy/<int:item_id>/', PaymentsView.as_view(), name='buy_item'),
    path('order/<int:order_id>/pay/', OrderPaymentView.as_view(), name='order_payment'),
    path('success/', SuccessView.as_view(), name='success'),
    path('cancel', CancelView.as_view(), name='cancel'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]
