import datetime
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, JsonResponse
from store.models import CartItem, ProductVariant
from coupon.models import Coupon
from .models import Address, Order, OrderProduct, Payment
from .forms import AddressForm

from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.views.generic import ListView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .render import Render
from django.utils import timezone
# Create your views here.

@login_required(login_url='store:login')
def payments(request):
    current_user = request.user
    try:
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method')
            order_no = request.POST.get('order_no')
            order = Order.objects.get(user=current_user, order_number = order_no)

            if payment_method == 'Razorpay':
                # process Razorpay payment
                amount_paid = request.POST.get('amount_paid')
                payment_id = request.POST.get('payment_id')
                status = request.POST.get('status')
                payment_method = "Razorpay"
            else:
                # process COD payment
                amount_paid = order.order_total
                payment_id = "cash on delivery"
                status = "Pending"
                payment_method = "Cash On Delivery"     

            payment = Payment(
                    user = current_user,
                    payment_id = payment_id,
                    payment_method = payment_method,
                    amount_paid = amount_paid,
                    status = status,
                )
            payment.save()
            order.payment = payment
            order.save()

            cart_items = CartItem.objects.filter(user = current_user)
            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order = order
                orderproduct.payment = payment
                orderproduct.user = current_user
                orderproduct.variant = item.variant
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.variant.price
                orderproduct.ordered = True
                orderproduct.save()

                # Reduce stock
                product_variant = ProductVariant.objects.get(id = item.variant.id)
                product_variant.stock -= item.quantity
                product_variant.save()

                
            # Clear Cart
            CartItem.objects.filter(user=current_user).delete()
            messages.success(request, 'Your order has been placed successfully.')
            if payment_method == 'Razorpay':
                return JsonResponse({'status': "Your order has been placed successfully."})
            redirect_url = f'/orders/order_completed/?order_number={order.order_number}'                
            return redirect(redirect_url)

    except Exception as e:
        messages.error(request, 'Error, Payment Incomplete')
        return redirect('orders:place_order')

@login_required(login_url='store:login')
def place_order(request, total=0, quantity=0):
    current_user = request.user
    try:
        cart_items = CartItem.objects.filter(user = current_user)
        cart_count = cart_items.count()
        if cart_count <= 0:
            return redirect('store:category')
        
        gst = 0
        grand_total = 0
        total = 0
        shipping = 0
        sub_total = 0
        discount = 0
        coupon = None
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
        
        if request.method == 'POST':
            billing_address_id = request.POST.get('billing_address')
            billing_address = Address.objects.get(id=billing_address_id)
            data = Order()  
            data.user = current_user
            data.address = billing_address
            data.order_total = grand_total
            data.gst = gst
            data.shipping = shipping
            data.coupon = coupon
            data.discount = discount
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            bid = data.id

            request.session['coupon_id'] = None
                        
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(bid)
            data.order_number = order_number
            data.save()
            order = data
            context = {
                'order': order,
                'cart_items' : cart_items,
                'sub_total': sub_total,
                'total' : total,
                'shipping' : shipping,
                'gst' : gst,
                'grand_total' : grand_total,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            return redirect('store:checkout')
    except Exception as e:
        if not request.user.is_authenticated:
            return redirect('store:login')
        else:
            raise e
    
def order_complete(request):
    order_number = request.GET.get('order_number')
    try:
        order = Order.objects.get(order_number=order_number)
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
            'order_products': order_products,
            'transaction_id': order.payment.payment_id,
            'subtotal': subtotal,
            'total': total,
            'shipping': shipping,
            'gst': gst,
        }
        return render(request, 'orders/order_complete.html', context)
    
    except Order.DoesNotExist:
        return redirect('store:home')    

class OrderPdf(LoginRequiredMixin, View):

    def get(self, request, order_number):
        order = Order.objects.get(order_number=order_number)
        try:
            order_products = OrderProduct.objects.filter(order=order)

            subtotal = 0
            total = 0
            for i in order_products:
                subtotal += i.product_price * i.quantity

            total = subtotal - order.discount
            shipping = 100
            gst = (18 * total)/100

            today = timezone.now()
            context = {
                'today': today,
                'order': order,
                'total': total,
                'subtotal': subtotal,
                'shipping': shipping,
                'gst': gst,
                'request': request,
            }
            return Render.render('orders/order_pdf.html', context)
        except order.DoesNotExist:
            messages.error(request, "Order does not exist.")
            return redirect('store:panel')

class AddAddress(LoginRequiredMixin, CreateView):
    form_class = AddressForm
    template_name = 'orders/add_address.html'
    success_url = reverse_lazy('orders:address')

    def form_valid(self, form):
        # Set the user field to the current user before saving the form
        form.instance.user = self.request.user
        return super().form_valid(form)

class ListAddress(LoginRequiredMixin, ListView):
    model = Address
    context_object_name = 'addresses'
    template_name = 'orders/my_address.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

class EditAddress(LoginRequiredMixin, UpdateView):
    model = Address
    fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'city', 'state', 'pin']
    template_name = 'orders/edit_address.html'
    success_url = reverse_lazy('orders:address')    

class DeleteAddress(DeleteView):
    model = Address
    context_object_name = 'address'
    template_name = 'orders/delete_address.html'
    success_url = reverse_lazy('orders:address')
