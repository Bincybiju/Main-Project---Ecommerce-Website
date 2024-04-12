from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import Http404


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponse('<script>alert("Product added successfully!"); window.location.href = "/admin_profile/";</script>')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

@login_required
def edit_products(request):
    products = Product.objects.all()
    return render(request, 'edit_products.html', {'products': products})

@login_required
def editproduct(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return HttpResponse('<script>alert("Product updated successfully!"); window.location.href = "/edit_products/";</script>')
    else:
        form = ProductForm(instance=product)

    return render(request, 'editproduct.html', {'form': form, 'product': product})

@login_required
def delete_products(request):
    products = Product.objects.all()
    return render(request, 'delete_products.html', {'products': products})

@login_required
def delete_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    
    if request.method == 'POST':
        product.delete()
        return redirect('admin_profile') 
    
    return render(request, 'confirm_delete_product.html', {'product': product})

def logout_view(request):
    logout(request)
    return redirect('login_view')

from django.db.models import Avg

@login_required
def customer_profile(request):
    products = Product.objects.all()
    
    for product in products:
        avg_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))
        product.avg_rating = avg_rating['rating__avg'] if avg_rating['rating__avg'] else 0

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(product_name__icontains=search_query)
        if not products.exists():
            return render(request, 'customer_profile.html', {'error_message': 'No products available.', 'user': request.user})
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)
        try:
            min_price = float(min_price)
            max_price = float(max_price)
            if min_price < 0 or max_price < 0:
                # Handle negative prices
                return render(request, 'customer_profile.html', {'error_message': 'Prices cannot be negative.', 'user': request.user})
            elif min_price > max_price:
                # Handle invalid price range
                return render(request, 'customer_profile.html', {'error_message': 'Minimum price cannot be greater than maximum price.', 'user': request.user})
            else:
                products = products.filter(price__gte=min_price, price__lte=max_price)
                if not products.exists():
                    return render(request, 'customer_profile.html', {'error_message': 'No products available.', 'user': request.user})
        except ValueError:
            return render(request, 'customer_profile.html', {'error_message': 'Invalid price format.', 'user': request.user})
    context = {
        'user': request.user,
        'products': products
    }
    return render(request, 'customer_profile.html', context)



@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        if created:
            messages.success(request, f"{product.product_name} added to cart successfully.")
        else:
            messages.info(request, f"{product.product_name} is already in your cart.")

        return redirect('view_cart')
    else:
        return HttpResponse(status=400)

@login_required
def view_cart(request):
    if request.method == 'POST':
        for item in CartItem.objects.filter(user=request.user):
            quantity_key = 'quantity_' + str(item.id)
            if quantity_key in request.POST:
                new_quantity = int(request.POST[quantity_key])
                if new_quantity > 0:
                    item.quantity = new_quantity
                    item.save()

        return redirect('view_cart')

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        item.total_price = item.product.price * item.quantity
    
    total_price = sum(item.total_price for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }

   
    return render(request, 'view_cart.html', context)

@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('orderitem_set__product')
    orderstatus = OrderStatus.objects.all()

    return render(request, 'view_orders.html', {'orders': orders, 'orderstatus': orderstatus})

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('view_cart')
    
@login_required
def rate_product(request, product_id):
    product = Product.objects.get(pk=product_id)

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.product_id = product.id  
            rating.user = request.user  
            rating.save()
            return HttpResponse('<script>alert("Product rated successfully!"); window.location.href = "/view_orders/";</script>')

    else:
        form = RatingForm()
    
    context = {
        'form': form,
        'product': product
    }

    return render(request, 'rate_product.html', context)

from django.core.mail import send_mail
from django.db import transaction

@login_required
def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                shipping_address = form.cleaned_data['shipping_address']
                payment_method = form.cleaned_data['payment_method']

                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address,
                    payment_method=payment_method,
                )

                for item in request.user.cartitem_set.all():
                    ordered_quantity = item.quantity
                    product = item.product

                    if ordered_quantity <= product.available_quantity:
                        product.available_quantity -= ordered_quantity
                        product.save()

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=ordered_quantity
                        )
                    else:
                        messages.error(request, f"Not enough stock available for {product.product_name}.")
                        return redirect('view_cart')

                request.user.cartitem_set.all().delete()

                subject = 'Order Confirmation'
                message = f"Dear {request.user.username},\n\nYour order has been successfully placed.\n\nThank you for shopping with us!\n\nBest regards,\nThe ShopMart Team"
                from_email = 'tkmce.alumniportal@gmail.com' 
                to_email = [request.user.email]
                send_mail(subject, message, from_email, to_email)

                return redirect('customer_profile')

    else:
        form = CheckoutForm()
        cart_items = request.user.cartitem_set.all()
        total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'checkout.html', {'form': form, 'cart_items': cart_items, 'total_price': total_price})

@login_required
def manage_orders(request):
    orders = Order.objects.all()
    orderstatus = OrderStatus.objects.all()
    return render(request, 'manage_orders.html', {'orders': orders, 'orderstatus': orderstatus})


@login_required
def update_order_status(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        raise Http404("Order does not exist")

    try:
        order_status = OrderStatus.objects.get(order=order)
    except OrderStatus.DoesNotExist:
        order_status = OrderStatus(order=order)

    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order_status)
        if form.is_valid():
            form.save()
            return HttpResponse('<script>alert("Status updated successfully!"); window.location.href = "/manage_orders/";</script>')
    else:
        form = OrderStatusUpdateForm(instance=order_status)

    return render(request, 'update_order_status.html', {'form': form, 'order': order})

@login_required
def view_orders_admin(request):
    orders = Order.objects.all()  
    return render(request, 'view_orders_admin.html', {'orders': orders})

@login_required
def view_reviews(request):
    reviews = Rating.objects.all()  
    products = Product.objects.all()
    return render(request, 'view_reviews.html', {'reviews': reviews, 'products': products})

def filter_by_category(request, category_name):
    products = Product.objects.filter(category=category_name)
    context = {
        'products': products,
        'user': request.user, 
    }
    return render(request, 'customer_profile.html', context)