from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from decimal import Decimal
from cart.models import CartItem  
import random
import string
import requests
import json

from .models import Order, OrderItem

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    delivery_fee = Decimal('5.00')
    total_with_delivery = order.total
    context = {
        'order': order,
        'delivery_fee': delivery_fee,
        'total_with_delivery': total_with_delivery
    }
    return render(request, 'order/order_detail.html', context)

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart_detail')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        cart_total = sum(Decimal(item.get_total_price()) for item in cart_items)
        delivery_fee = Decimal('5.00')
        total_with_delivery = cart_total + delivery_fee

        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            shipping_address=request.POST.get('shipping_address'),
            phone=request.POST.get('phone'),
            notes=request.POST.get('notes', ''),
            payment_method=payment_method,
            total=total_with_delivery
        )

        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        cart_items.delete()

        if payment_method == 'eSewa':
            # REAL eSewa payment
            return redirect('esewa_payment', order.id)

        messages.success(request, 'Your order has been placed successfully!')
        return redirect('order_detail', order.id)

    cart_total = sum(Decimal(item.get_total_price()) for item in cart_items)
    delivery_fee = Decimal('5.00')
    total_with_delivery = cart_total + delivery_fee

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'delivery_fee': delivery_fee,
        'total_with_delivery': total_with_delivery
    }
    return render(request, 'order/place_order.html', context)

