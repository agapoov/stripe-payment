import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView

from .models import Item

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentsView(View):
    def get(self, request, item_id):
        try:
            item = get_object_or_404(Item, id=item_id)
            session = stripe.checkout.Session.create(
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.name,
                            'description': item.description
                        },
                        'unit_amount': item.price,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse_lazy('success')),
                cancel_url='http://localhost:4242/cancel',
            )
            return JsonResponse({'id': session.id})
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)


class ItemDetailView(DetailView):
    model = Item
    template_name = 'payments/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_pub_key'] = settings.STRIPE_PUBLIC_KEY
        return context


class SuccessView(TemplateView):
    template_name = 'payments/success.html'
