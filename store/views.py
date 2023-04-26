from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.edit import UpdateView, FormView
from django.contrib import messages

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy, reverse

from dashboard.forms import CustomerRegisterForm, EditUserProfileForm
from .models import Product, Category, Cart, CartItem, ProductVariant
from orders.models import Order, OrderProduct
from coupon.models import Coupon
from dashboard import verify
from dashboard.verify import send
from dashboard.forms import VerifyForm, PasswordChangeForm
from coupon.forms import CouponForm
from orders.models import Address
import requests
from django.core.paginator import Paginator
# Create your views here.

def verification_required(view_func):
    def wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_verified:
            # Send the verification code to the user's phone number
            phone_number = request.user.phone
            send(phone_number)
            messages.success(request, "One Time Password has been sent to your cellphone.")
            # Redirect to the verification page
            return redirect('store:verify')

        # User is verified, call the original view function
        return view_func(request, *args, **kwargs)

    return user_passes_test(lambda u: u.is_authenticated, login_url='store:login')(wrapped_view_func)


class VerificationRequiredMixin(LoginRequiredMixin):
    """A mixin that requires the user to be verified."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_verified:
            # Send the verification code to the user's phone number
            phone_number = request.user.phone
            send(phone_number)
            messages.success(request, "One Time Password has been sent to your cellphone.")
            # Render the verification form
            return redirect('store:verify')

        # User is verified, continue with the request
        return super().dispatch(request, *args, **kwargs)

def customer_login(request):
    if request.user.is_authenticated:
        messages.error(request, "You are already logged in.")
        return redirect('store:home')
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass

            login(request, user)
            if not request.user.is_verified:
                verify.send(request.user.phone)
                messages.success(request, 'OTP sent to your phone number please verify.')
                return redirect('store:verify')
            messages.success(request, 'You are now logged in.')
            return redirect('store:home')
        else:
            messages.error(request, 'Invalid login Credentials')
            return redirect('store:login')
    return render(request, 'store/login.html')
    
class CustomerRegister(FormView):
    template_name = 'store/register.html'
    form_class = CustomerRegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('store:login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('store:home')
        return super(CustomerRegister, self).get(*args, **kwargs)
    
@login_required(login_url='store:login')
def cancel_order(request, order_number):
    current_user = request.user
    order = Order.objects.get(user=current_user, order_number=order_number)
    try:
        if order.status == 'Submitted' or 'Confirmed' or 'Shipped':
            order.status = 'Cancel'
            order.save()
            messages.success(request, "Request for order cancellation recieved.")
        elif order.status == 'Delivered':
            order.status = 'Return'    
            order.save()    
            messages.success(request,"Request for order return recieved.")
        return redirect('store:order-deet', order.order_number)
    except Order.DoesNotExist:
        messages.error(request,"Order does not exist.")
        return redirect('store:panel')

@login_required(login_url='store:login')
def verify_code(request):
    if request.method == 'POST':
        form = VerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            if verify.check(request.user.phone, code):
                request.user.is_verified = True
                request.user.save()
                messages.success(request,"Your cellphone number has been verified.")
                return redirect('store:home')
    else:
        form = VerifyForm()
    return render(request, 'store/verify.html', {'form': form})

class HomeView(ListView):
    template_name = 'store/index.html'
    model = Category
    context_object_name = 'categories'
    ordering = 'name'
    paginate_by = 4

class Aboutview(TemplateView):
    template_name = 'store/about.html'

class CategoryListView(ListView):
    template_name = 'store/category_list.html'
    model = Category
    context_object_name = 'categories'
    ordering = 'name'
    paginate_by = 4

class ProductListView(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    paginate_by = 3

    def get_queryset(self):
        category_slug = self.kwargs.get('categories_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = Product.objects.filter(category=category)
        else:
            queryset = Product.objects.all()
        return queryset

def product_detail(request):
    category_slug = request.GET.get('category_slug')
    product_slug = request.GET.get('product_slug')
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        variants = product.productvariant_set.all()
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product)
    except Exception as e:
        raise e
    context = {
        'product' : product,
        'variants' : variants,
        'in_cart' : in_cart,
    }
    return render(request, 'store/product_detail.html', context)

def get_price(request):
    product_id = request.GET.get('product_id')
    selected_size = request.GET.get('size')
    try:
        # Get the product variant with the selected size
        variant = ProductVariant.objects.filter(product_id=product_id, size=selected_size).first()
    except ObjectDoesNotExist:
        messages.error(request, "Selected product not available.")
        return
    # Return the new price as a JSON response
    return JsonResponse({'price': variant.price})

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
   
class AddToCartView(View):
    def post(self, request, product_id, variant_id):
        current_user = request.user
        if current_user.is_authenticated:
            size = request.POST.get('size')
            product = Product.objects.get(id=product_id)
            variant = ProductVariant.objects.get(id=variant_id)
            try:
                cart_item = CartItem.objects.get(product=product, variant=variant, user=current_user)
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, "Item quantity successfully increased.")
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(
                    product=product,
                    variant=variant,
                    user=current_user,
                    quantity=1,
                )
                cart_item.save()
                messages.success(request, "Item successfully added to the cart.")
            return redirect('store:cart')
        else:
            size = request.POST.get('size')
            product = Product.objects.get(id=product_id)
            variant = variant = ProductVariant.objects.get(id=variant_id)
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    cart_id=_cart_id(request)
                )
            cart.save()
            try:
                cart_item = CartItem.objects.get(product=product, variant=variant, cart=cart)
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, "Item quantity successfully increased.")
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(
                    product=product,
                    variant=variant,
                    cart=cart,
                    quantity=1,
                )
                cart_item.save()
                messages.success(request, "Item successfully added to the cart.")
            return redirect('store:cart')

def add_cart(request, product_id):
    current_user = request.user
    if current_user.is_authenticated:
        if request.method == 'POST':
            size = request.POST.get('size')
            product = Product.objects.get(id=product_id)
            variant = product.productvariant_set.filter(size__name=size).first()
            
            try:
                cart_item = CartItem.objects.get(product=product, variant=variant, user=current_user)
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, "Item quantity successfully increased.")
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(
                    product=product,
                    variant=variant,
                    user=current_user,
                    quantity=1,
                )
                cart_item.save()
                messages.success(request, "Item successfully added to the cart.")
            return redirect('store:cart')
    else:
        if request.method == 'POST':
            size = request.POST.get('size')
            product = Product.objects.get(id=product_id)
            variant = product.productvariant_set.filter(size__name=size).first()
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    cart_id = _cart_id(request)
                )
            cart.save()
            try:
                cart_item = CartItem.objects.get(product=product, variant=variant, cart=cart)
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, "Item quantity successfully increased.")
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(
                    product=product,
                    variant=variant,
                    cart=cart,
                    quantity=1,
                )
                cart_item.save()
                messages.success(request, "Item successfully added to the cart.")
            return redirect('store:cart')

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id = product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, "Item quantity reduced in the cart.")
        else:
            cart_item.delete()
            messages.success(request, "Item successfully removed from the cart.")
    except:
        pass
    return redirect('store:cart')

def remove_cart_item(request, product_id, cart_item_id):   
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id =_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
        messages.success(request,"Item successfully removed from the cart.")
        return redirect('store:cart')
    except product.DoesNotExist:
        return redirect('store:cart')

def cart(request, total=0, quantity=0, cart_items=None):
    gst = 0
    grand_total = 0
    shipping = 0
    sub_total = 0
    discount = 0
    coupon = None
    coupon_form = CouponForm()
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)

        for cart_item in cart_items:
            sub_total += cart_item.variant.price * cart_item.quantity
            quantity += cart_item.quantity
        coupon_id = request.session.get('coupon_id')
        if coupon_id:
            coupon = Coupon.objects.get(id = coupon_id)
            discount = (coupon.discount* sub_total)/100
            total = sub_total - discount
        else:
            total = sub_total
        gst = (18 * total)/100
        shipping = 100
        grand_total = total + gst + shipping
            
    except ObjectDoesNotExist:
        pass

    context = {
        'coupon_form': coupon_form,
        'coupon': coupon,
        'sub_total': sub_total,
        'discount' : discount,
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'gst' : gst,
        'shipping' : shipping,
        'grand_total' : grand_total,
    }
    return render(request, 'store/cart.html', context)

class PanelView(VerificationRequiredMixin, ListView):
    template_name = 'store/panel.html'
    context_object_name = 'orders'
    paginate_by = 5
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, payment__isnull=False).order_by('-created_at')
    
@login_required(login_url='store:login')
@verification_required
def order_detail(request, order_number):
    current_user = request.user
    order = Order.objects.get(order_number=order_number)
    try:
        order_products = OrderProduct.objects.filter(order=order)

        total = 0
        subtotal = 0
        for i in order_products:
            subtotal += i.product_price * i.quantity

        total = subtotal - order.discount
        shipping = 100
        gst = (18 * total)/100
        
        context = {
            'order': order,
            'products': order_products,
            'subtotal': subtotal,
            'total': total,
            'shipping': shipping,
            'gst': gst,
        }
        return render(request, 'store/order_detail.html', context)
    except order.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect('store:panel')

@login_required(login_url='store:login')
@verification_required
def checkout(request, total=0, quantity=0, cart_items=None):
    gst = 0
    grand_total = 0
    shipping = 0
    sub_total = 0
    discount = 0
    coupon = None
    addresses = Address.objects.filter(user=request.user)
    try: 
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
        for cart_item in cart_items:
            sub_total += cart_item.variant.price * cart_item.quantity
            quantity += cart_item.quantity
        coupon_id = request.session.get('coupon_id')
        if coupon_id:
            coupon = Coupon.objects.get(id = coupon_id)
            discount = (coupon.discount* sub_total)/100
            total = sub_total - discount
        else:
            total = sub_total
        shipping = 100
        gst = (18 * total)/100
        grand_total = total + gst + shipping
    except ObjectDoesNotExist:
        pass
    context = {
        'coupon': coupon,
        'sub_total': sub_total,
        'discount' : discount,
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'gst' : gst,
        'grand_total' : grand_total,
        'shipping' : shipping,
        'addresses': addresses,
    }
    return render(request, 'store/checkout.html', context)

class PasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('store:panel')
    template_name = 'store/change_password.html'

class UpdateUserView(VerificationRequiredMixin, UpdateView):
    form_class = EditUserProfileForm
    template_name = 'store/edit_profile.html'
    success_url = reverse_lazy('store:panel')

    def get_object(self):
        return self.request.user


def search(request):
    try:
        query = request.GET['search']
        items = Product.objects.filter(name__icontains=query)
        context = {
            'items': items,
        }
        return render(request, 'store/search_results.html', context)
    except Product.DoesNotExist:
        messages.error(request, "Searched product unavailable.")
        return

def handle_not_found(request, exception):
    return render(request, 'store/not_found.html')