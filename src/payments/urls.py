from django.urls import path

from .views import ItemDetailView, PaymentsView, SuccessView

urlpatterns = [
    path('item/<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('buy/<int:item_id>/', PaymentsView.as_view(), name='buy_item'),
    path('success/', SuccessView.as_view(), name='success')
]
