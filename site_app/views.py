from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from django.views.generic import (
    DetailView,)
from site_app.models import Item, Order, Tax, Discount
import stripe

def get_stripe_keys(currency):
    if currency.lower() == 'eur':
        return settings.STRIPE_SECRET_KEY_EUR, settings.STRIPE_PUBLIC_KEY_EUR
    else:
        return settings.STRIPE_SECRET_KEY_USD, settings.STRIPE_PUBLIC_KEY_USD

class ItemDetailView(DetailView):
    model = Item
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.currency == 'eur':
            context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY_EUR
        else:
            context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY_USD
        return context
    
class OrderDetailView(DetailView):
    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.items.first().currency == 'eur':
            context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY_EUR
        else:
            context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY_USD
        return context  
    
    
def buy_item_intent(request: WSGIRequest, pk):
    item = get_object_or_404(Item, pk=pk)
    secret_key, public_key = get_stripe_keys(item.currency)
    amount = int(item.price * 100)
    
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=item.currency,
        payment_method_types=['card'],
        api_key=secret_key 
    )
    
    context = {
        'client_secret': intent.client_secret,
        'stripe_public_key': public_key,
        'item': item
    }
    return render(request, 'site_app/payment_intent.html', context)


def buy_order_intent(request: WSGIRequest, pk):
    order = get_object_or_404(Order, pk=pk)
    first_item = order.items.first()
    currency = first_item.currency if first_item else 'usd'
    
    secret_key, public_key = get_stripe_keys(currency)
    total_amount = int(order.total_sum() * 100)
    
    intent = stripe.PaymentIntent.create(
        amount=total_amount,
        currency=currency,
        payment_method_types=['card'],
        metadata={'order_id': order.id},
        api_key=secret_key
    )
    
    context = {
        'client_secret': intent.client_secret,
        'stripe_public_key': public_key,
        'order': order,
        'total_amount': order.total_sum(),
    }
    return render(request, 'site_app/payment_intent.html', context)


def add_to_order(request: WSGIRequest, item_id: int):
    order_id = request.session.get('order_id')
    
    if order_id:
        order = Order.objects.filter(id=order_id).first()
        if not order:
            order = Order.objects.create()
            request.session['order_id'] = order.id
    else:
        order = Order.objects.create()
        request.session['order_id'] = order.id
        
    item = get_object_or_404(Item, pk=item_id)
    order.items.add(item)
    return redirect('order_detail', pk=order.pk)


def update_order(request, pk):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        discount_id = request.POST.get('discount_id')
        tax_id = request.POST.get('tax_id')
    
        if discount_id:
            try:
                order.discount = Discount.objects.get(pk=discount_id)
            except Discount.DoesNotExist:
                pass
        if tax_id:
            try:
                order.tax = Tax.objects.get(pk=int(tax_id))
            except Tax.DoesNotExist:
                pass
        order.save()
        
    return redirect('order_detail', pk=pk)
    
    
def create_order_checkout_session(request, pk):
    order = get_object_or_404(Order, pk=pk)
    domain = "http://127.0.0.1:8000"

    first_item = order.items.first()
    currency = first_item.currency if first_item else 'usd'

    if currency == 'eur':
        stripe.api_key = settings.STRIPE_SECRET_KEY_EUR
    else:
        stripe.api_key = settings.STRIPE_SECRET_KEY_USD


    coupon_id = None
    if order.discount:
        try:
            coupon = stripe.Coupon.create(
                percent_off=order.discount.percent_off,
                duration="once", # единаразаво применяем скидку, чтобы не было дюпов
                name=order.discount.name
            )
            coupon_id = coupon.id
        except Exception as e:
            return JsonResponse({'error': str(e)})
    tax_rate_id = None
    if order.tax:
        tax_rate = f"{order.tax.rate:.2f}"
        print(tax_rate)
        try:
            tax_rate = stripe.TaxRate.create(
                display_name=order.tax.name,
                inclusive=False, # накидываем налог поверх цены (то-есть налог не включен в цену изначально)
                percentage=order.tax.rate,
            )
            tax_rate_id = tax_rate.id
        except Exception as e:
            return JsonResponse({'error': str(e)})

    line_items = []
    for item in order.items.all():
        item_data = {
            'price_data': {
                'currency': currency,
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': int(item.price * 100),
            },
            'quantity': 1,
        }
        
        if tax_rate_id:
            item_data['tax_rates'] = [tax_rate_id]
            
        line_items.append(item_data)
    session_data = {
        'payment_method_types': ['card'],
        'line_items': line_items,
        'mode': 'payment',
        'success_url': domain + '/success/',
        'cancel_url': domain + '/cancel/',
    }
    if coupon_id:
        session_data['discounts'] = [{'coupon': coupon_id}]

    try:
        checkout_session = stripe.checkout.Session.create(**session_data)
        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)})
   
    
def create_checkout_session(request: WSGIRequest, pk: int):
    print(type(request))
    item = get_object_or_404(Item, pk=pk)
    domain = "http://127.0.0.1:8000"
    
    if item.currency == 'eur':
        stripe.api_key = settings.STRIPE_SECRET_KEY_EUR
    else:
        stripe.api_key = settings.STRIPE_SECRET_KEY_USD
    
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': item.currency,
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': int(item.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=domain + '/success/', 
        cancel_url=domain + '/cancel/',
    )
    return JsonResponse({'id': checkout_session.id})


def success_view(request):
    if 'order_id' in request.session:
        del request.session['order_id']
        
    return redirect('item_detail', pk=1)

def cancel_view(request):
    return redirect('item_detail', pk=1)

def add_test_items(request: WSGIRequest):
    items_data = [
    {'name': 'test1', 'description': 'desc for test1', 'price': 99.99},
    {'name': 'test2', 'description': 'desc for test2', 'price': 123.45, 'currency': 'eur'},
    {'name': 'test3', 'description': 'desc for test3', 'price': 50.00},
    {'name': 'test4', 'description': 'desc for test4', 'price': 75.25, 'currency': 'eur'},
    {'name': 'test5', 'description': 'desc for test5', 'price': 200.00},
    {'name': 'test6', 'description': 'desc for test6', 'price': 15.75, 'currency': 'eur'},
    {'name': 'test7', 'description': 'desc for test7', 'price': 89.99, 'currency': 'eur'},
    {'name': 'test8', 'description': 'desc for test8', 'price': 299.99}
    ]
    for i in items_data:
        itm = Item(name=i['name'], description=i['description'], price=i['price'])
        itm.save()
    print(Item.objects.all())
    return redirect('item_detail', pk=1)
