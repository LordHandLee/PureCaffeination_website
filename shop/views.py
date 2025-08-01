from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe 
import json
from .models import Order, Product, StripePrice

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def home(request):
    return render(request, 'home.html', {'theme': 'brand'})

def product(request):
    product_info = {
        'name': 'Pure Caffeination',
        'price_dollars': '4.99',
        'price_cents': 499,
        'description': '100mg pure caffeine capsules. 240 count. No fillers. No sugar.',
        'stripe_price_id': 'price_12345',  # Replace with actual price ID from Stripe
    }
    return render(request, 'product.html', {'theme': 'brand'})#, {'product': product_info})

# def cart(request):
#     # return render(request, 'cart.html', {'theme': 'brand'})
#     cart = request.session.get('cart')
#     if not cart:
#         return HttpResponse("Your cart is empty.")


#     try:
#         product = get_object_or_404(Product, pk=cart['product_id'])
#         quantity = int(cart.get('quantity', 1))
#         price_cents = product.price_cents or 0
#         estimated_total = (price_cents * quantity) / 100
#     except Exception as e:
#         return HttpResponse(f"Error loading cart: {str(e)}", status=500)

#     return render(request, 'cart.html', {
#         'theme': 'brand',
#         'cart': cart,
#         'product': product,
#         'estimated_total': estimated_total
#     })

#     #return render(request, 'cart.html', {'theme': 'brand'})#{'cart': cart})

def cart(request):
    cart = request.session.get('cart')
    if not cart:
        return HttpResponse("Your cart is empty.")

    if request.method == 'POST':
        cart['quantity'] = int(request.POST.get('quantity', 1))
        cart['purchase_type'] = request.POST.get('purchase_type', 'one-time')
        cart['interval_months'] = int(request.POST.get('interval_months', 1)) if cart['purchase_type'] == 'subscription' else None
        request.session['cart'] = cart

    try:
        product = get_object_or_404(Product, pk=cart['product_id'])
        quantity = int(cart.get('quantity', 1))
        base_price = product.price_cents

        # Discount logic
        discount_percent = 0
        if cart.get('purchase_type') == 'subscription':
            discount_percent += 10
        if quantity >= 2:
            discount_percent += 10

        discounted_price_cents = base_price * (1 - discount_percent / 100)
        estimated_total = (discounted_price_cents * quantity) / 100

        return render(request, 'cart.html', {
            'theme': 'brand',
            'cart': {
                **cart,
                'price_dollars': f"{discounted_price_cents / 100:.2f}"
            },
            'product': product,
            'estimated_total': estimated_total,
            'price_cents_discounted': int(discounted_price_cents)
        })
    except Exception as e:
        return HttpResponse(f"Error loading cart: {str(e)}", status=500)
    
@csrf_exempt
def update_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            purchase_type = data.get('purchase_type', 'one-time')
            interval_months = int(data.get('interval_months', 1)) if purchase_type == 'subscription' else None

            cart = request.session.get('cart')
            if not cart:
                return JsonResponse({'error': 'No cart found'}, status=400)

            cart['quantity'] = quantity
            cart['purchase_type'] = purchase_type
            cart['interval_months'] = interval_months
            request.session['cart'] = cart

            product = get_object_or_404(Product, pk=cart['product_id'])
            base_price = product.price_cents or 0

            # Discount logic
            discount_percent = 0
            if purchase_type == 'subscription':
                discount_percent += 10
            if quantity >= 2:
                discount_percent += 10

            discounted_price = base_price * (1 - discount_percent / 100)
            estimated_total = (discounted_price * quantity) / 100

            return JsonResponse({
                'estimated_total': estimated_total,
                'discount_percent': discount_percent
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=405)
    #         price_cents = product.price_cents or 0
    #         estimated_total = (price_cents * quantity) / 100

    #         return JsonResponse({'estimated_total': estimated_total})
    #     except Exception as e:
    #         return JsonResponse({'error': str(e)}, status=500)
    # return JsonResponse({'error': 'Invalid request'}, status=405)

def checkout(request):
    coupon_codes = {'volume discount': 'promo_1RrILF2ZdAyTmf1nljvz2d5v',
                    'subscription discount': 'promo_1RrIJz2ZdAyTmf1nDegoIpzr',
                    'volume discount once': 'promo_1RrILu2ZdAyTmf1npjoSUm4x',}
    
    cart = request.session.get('cart')
    if not cart:
        return HttpResponse("Your cart is empty.", status=400)
    
    try:
        product = get_object_or_404(Product, pk=cart['product_id'])
        quantity = int(cart.get('quantity', 1))
        purchase_type = cart.get('purchase_type', 'one-time')
        interval_months = int(cart.get('interval_months') or 1)

        # Determine which coupon(s) to apply
        promotion_codes = []
        if quantity >= 2 and purchase_type == 'subscription':
            promotion_codes = [coupon_codes['volume discount'], coupon_codes['subscription discount']]  # or just ['20OFFCOMBO']
            print("Applying volume discount and subscription discount")
        elif quantity >= 2:
            promotion_codes = [coupon_codes['volume discount once']]
            print("Applying volume discount once")
        elif purchase_type == 'subscription':
            promotion_codes = [coupon_codes['subscription discount']]
            print("Applying subscription discount")

        # Get the stripe promotion code IDs
        stripe_promotions = []
        for code in promotion_codes:
            promo = stripe.PromotionCode.list(code=code, active=True).data
            print("Promo code found:", promo)
            if promo:
                stripe_promotions.append(promo[0].id)

        if purchase_type == 'subscription':
            price_obj = StripePrice.objects.filter(
                product=product,
                one_time=False,
                recurring_interval=interval_months
            ).first()
            mode = 'subscription'
        else:
            price_obj = StripePrice.objects.filter(
                product=product,
                one_time=True
            ).first()
            mode = 'payment'

        if not price_obj:
            return HttpResponse("Could not find a matching Stripe price.", status=500)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_obj.stripe_price_id,  # Replace with your Stripe price ID
                'quantity': quantity,
            }],
            automatic_tax={'enabled': True},
            billing_address_collection='required',
            shipping_address_collection={"allowed_countries": ["US", "CA"]},
            mode=mode,
            discounts=[{'promotion_code': pcode} for pcode in stripe_promotions],
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cart/'),
        )
        return redirect(session.url, code=303)
    except Exception as e:
        return HttpResponse(f"Error creating Stripe session: {str(e)}", status=500)
    
def add_to_cart(request, product_id):
    print(product_id)
    product = get_object_or_404(Product, stripe_product_id=product_id)
    request.session['cart'] = {
        'product_id': product.id,
        'name': product.name,
        'price_cents': product.price_cents,
        'price_dollars': product.price_dollars,
        'quantity': 1,
        'purchase_type': 'one-time',  # default
    }
    return redirect('/cart/')


def cart_view(request):
    cart = request.session.get('cart')
    if not cart:
        return HttpResponse("Your cart is empty.")

    # Update from POST data
    if request.method == 'POST':
        cart['quantity'] = int(request.POST.get('quantity', 1))
        cart['purchase_type'] = request.POST.get('purchase_type', 'one-time')
        if cart['purchase_type'] == 'subscription':
            cart['interval_months'] = int(request.POST.get('interval_months', 1))
        else:
            cart['interval_months'] = None
        request.session['cart'] = cart
        return redirect('/checkout/')

    return render(request, 'cart.html', {'theme': 'brand'})#{'cart': cart})


def success(request):
    return render(request, 'success.html', {'theme': 'brand'})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id')

        # Optional: Retrieve full session with expanded line items
        try:
            line_items = stripe.checkout.Session.list_line_items(session_id, limit=10)
        except Exception as e:
            return HttpResponse(f"Error retrieving line items: {str(e)}", status=400)

        quantity = 1
        if line_items and line_items.data:
            line_item = line_items.data[0]  # Assume single product purchase
            stripe_product_id = line_item['price']['product']
            quantity = line_item.get('quantity', 1)
        try:
            product = Product.objects.get(stripe_product_id=stripe_product_id)
        except Product.DoesNotExist:
            product = None  # Or handle gracefully
        shipping_details = session.get('collected_information', {}).get('shipping_details', {})

        Order.objects.create(
            email=session.get('customer_details', {}).get('email'),
            name=shipping_details.get('name', 'No Name'),
            address=shipping_details.get('address', {}),
            amount_paid=session.get('amount_total', 0) / 100,
            stripe_session_id=session_id,
            quantity=quantity,
            product=product,
        )

    return HttpResponse(status=200)

    # if event['type'] == 'checkout.session.completed':
    #     session = event['data']['object']

    #     Order.objects.create(
    #         email=session['customer_details']['email'],
    #         name=session['shipping']['name'],
    #         address=session['shipping']['address'],
    #         amount_paid=session['amount_total'] / 100,
    #         stripe_session_id=session['id'],
    #     )

    # return HttpResponse(status=200)