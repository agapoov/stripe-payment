import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView

from .models import Item, Order

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentsView(View):
    def get(self, request, item_id):
        try:
            item = get_object_or_404(Item, id=item_id)
            
            stripe_price = int(item.price * 100)
            
            session_data = {
                'line_items': [{
                    'price_data': {
                        'currency': item.currency,
                        'product_data': {
                            'name': item.name,
                            'description': item.description
                        },
                        'unit_amount': stripe_price,
                    },
                    'quantity': 1,
                }],
                'mode': 'payment',
                'success_url': request.build_absolute_uri(reverse_lazy('success')),
                'cancel_url': request.build_absolute_uri(reverse_lazy('cancel')),
            }

            session = stripe.checkout.Session.create(**session_data)
            
            return JsonResponse({'id': session.id})
            
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)


class OrderPaymentView(View):
    def get(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            
            line_items = []
            for item in order.items.all():
                stripe_price = int(item.price * 100)
                line_items.append({
                    'price_data': {
                        'currency': item.currency,
                        'product_data': {
                            'name': item.name,
                            'description': item.description
                        },
                        'unit_amount': stripe_price,
                    },
                    'quantity': 1,
                })

            session_data = {
                'line_items': line_items,
                'mode': 'payment',
                'success_url': request.build_absolute_uri(reverse_lazy('success')),
                'cancel_url': request.build_absolute_uri(reverse_lazy('cancel')),
            }

            if order.discount:
                if not order.discount.stripe_coupon_id:
                    coupon = stripe.Coupon.create(
                        percent_off=float(order.discount.percent_off),
                        duration="once"
                    )
                    order.discount.stripe_coupon_id = coupon.id
                    order.discount.save()
                session_data['discounts'] = [{
                    'coupon': order.discount.stripe_coupon_id,
                }]

            if order.tax:
                if not order.tax.stripe_tax_rate_id:
                    tax_rate = stripe.TaxRate.create(
                        display_name=order.tax.name,
                        percentage=float(order.tax.rate),
                        inclusive=False
                    )
                    order.tax.stripe_tax_rate_id = tax_rate.id
                    order.tax.save()
                for item in line_items:
                    item['tax_rates'] = [order.tax.stripe_tax_rate_id]

            session = stripe.checkout.Session.create(**session_data)

            order.status = 'paid'
            order.save()

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


class CancelView(TemplateView):
    template_name = 'payments/cancel.html'


class OrderDetailView(DetailView):
    model = Order
    template_name = 'payments/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_pub_key'] = settings.STRIPE_PUBLIC_KEY
        return context
