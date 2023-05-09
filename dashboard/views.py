from django.shortcuts import render, redirect
from .models import Customer
from store.models import ProductVariant, Product, Category, Size
from orders.models import Order
from coupon.models import Coupon
from orders.forms import OrderForm
from coupon.forms import AddCouponForm

from django.views.generic import ListView, TemplateView, DetailView, View
from django.contrib.auth.views import LoginView
from django.views.generic.edit import DeleteView, CreateView, UpdateView

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count

import csv
from django.http import HttpResponse, response
from django.utils import timezone
from orders.render import Render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
import datetime
from django.utils.timezone import make_aware
# Create your views here.

def superuser_login_required(view_func=None, login_url=None, redirect_field_name=None, *args, **kwargs):
    """
    Decorator for views that checks that the user is a superuser and is authenticated,
    or redirects to the login page.
    """
    decorator = [login_required(login_url=login_url, redirect_field_name=redirect_field_name)]
    decorator.append(user_passes_test(lambda u: u.is_superuser, login_url=login_url, redirect_field_name=redirect_field_name))

    def inner_decorator(view_func):
        return decorator[0](decorator[1](view_func))
    return inner_decorator(view_func) if view_func else inner_decorator


class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied()

class AdminLogin(LoginView):
    template_name = 'dashboard/admin_login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard:dash')

# class DashBoard(SuperuserRequiredMixin, LoginRequiredMixin, TemplateView):
#     template_name = 'dashboard/dash.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         orders = Order.objects.exclude(payment__isnull=True).order_by('-updated_at')
#         status_count = Order.objects.values('status').annotate(status_count=Count('status')).distinct()
#         variants_with_stock = ProductVariant.objects.values( 'product__name', 'size__name', 'price', 'stock')
#         context['orders'] = orders    # add them to the context dictionary
#         context['variants'] = variants_with_stock
#         context['status_counts'] = status_count
#         return context

@superuser_login_required
def dashboard(request):
    if request.method=='POST':
        from_date = request.POST.get('fromdate')
        to_date = request.POST.get('todate')
        search_result = Order.objects.filter(created_at__range=[from_date, to_date]).exclude(payment__isnull=True).order_by('-created_at')
        variants_with_stock = ProductVariant.objects.values( 'product__name', 'size__name', 'price', 'stock')
        status_count = Order.objects.filter(created_at__range=[from_date, to_date]).values('status').annotate(status_count=Count('status')).distinct()
        context = {
            'orders': search_result,
            'variants': variants_with_stock,
            'status_counts': status_count,
        }
        return render(request, 'dashboard/dash.html', context)
    else:
        orders = Order.objects.exclude(payment__isnull=True).order_by('-created_at')
        status_count = Order.objects.values('status').annotate(status_count=Count('status')).distinct()
        variants_with_stock = ProductVariant.objects.values( 'product__name', 'size__name', 'price', 'stock')
        context = {
                'orders': orders,
                'variants': variants_with_stock,
                'status_counts': status_count,
            }
        return render(request, 'dashboard/dash.html', context)

class Pdf(SuperuserRequiredMixin, LoginRequiredMixin, View):

    def get(self, request):
        orders = Order.objects.exclude(payment__isnull=True).order_by('-updated_at')
        today = timezone.now()
        context = {
            'today': today,
            'orders': orders,
            'request': request,
        }
        return Render.render('dashboard/pdf.html', context)
    
    def post(self, request):
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        from_datetime = datetime.datetime.strptime(fromdate, "%Y-%m-%d")
        to_datetime = datetime.datetime.strptime(todate, "%Y-%m-%d")
        from_datetime_aware = make_aware(from_datetime)
        to_datetime_aware = make_aware(to_datetime)
        orders = Order.objects.exclude(payment__isnull=True).filter(updated_at__range=[from_datetime_aware, to_datetime_aware]).order_by('-updated_at')
        today = timezone.now()
        context = {
            'today': today,
            'orders': orders,
            'request': request,
        }
        return Render.render('dashboard/pdf.html', context)

class Csv(SuperuserRequiredMixin, LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=order.csv'

        # Create CSV writer
        writer = csv.writer(response)

        # Get the date range from the POST data
        from_date_str = request.POST.get('fromdate', None)
        to_date_str = request.POST.get('todate', None)
        from_date = timezone.make_aware(datetime.datetime.strptime(from_date_str, '%Y-%m-%d')) if from_date_str else None
        to_date = timezone.make_aware(datetime.datetime.strptime(to_date_str, '%Y-%m-%d')) if to_date_str else None

        # Filter orders by date range
        orders = Order.objects.exclude(payment__isnull=True).order_by('-updated_at')
        if from_date:
            orders = orders.filter(updated_at__gte=from_date)
        if to_date:
            orders = orders.filter(updated_at__lte=to_date)

        # Add columns
        writer.writerow(['User', 'Billing Name', 'Order ID', 'Payment ID', 'Coupon', 'Discount', 'Total', 'Status'])

        # Loop through and append
        for order in orders:
            billing_name = order.address.first_name if order.address and order.address.first_name else ''
            coupon = order.coupon.code if order.coupon and order.coupon.code else ''
            writer.writerow([order.user.email, billing_name, order.order_number, order.payment.payment_id, coupon, order.discount, order.order_total, order.status])

        return response

class CouponList(SuperuserRequiredMixin, LoginRequiredMixin, ListView):
    model = Coupon
    context_object_name = 'coupons'
    template_name = 'dashboard/coupon_list.html'

class CouponCreate(SuperuserRequiredMixin, LoginRequiredMixin, CreateView):
    model = Coupon
    fields = ['code', 'valid_from', 'valid_till', 'discount']
    template_name = 'dashboard/coupon_form.html'
    success_url = reverse_lazy('dashboard:coupons')

class CouponUpdate(SuperuserRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Coupon
    fields = ['code', 'valid_from', 'valid_till', 'discount']
    context_object_name = 'coupon'
    template_name = 'dashboard/coupon_update.html'
    success_url = reverse_lazy('dashboard:coupons')

class CouponDelete(SuperuserRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Coupon
    context_object_name = 'coupon'
    template_name = 'dashboard/coupon_delete.html'
    success_url = reverse_lazy('dashboard:coupons')

@superuser_login_required
def order_list(request):
    if request.method=='POST':
        from_date = request.POST.get('fromdate')
        to_date = request.POST.get('todate')
        search_result = Order.objects.filter(created_at__range=[from_date, to_date]).exclude(payment__isnull=True).order_by('-created_at')
        context = {
            'orders': search_result,
        }
        return render(request, 'dashboard/order_list.html', context)
    else:
        orders = Order.objects.exclude(payment__isnull=True).order_by('-created_at')
        context = {
                'orders': orders,
            }
        return render(request, 'dashboard/order_list.html', context)

class OrderDetail(SuperuserRequiredMixin, LoginRequiredMixin, DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'dashboard/order_detail.html'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_number'] = self.kwargs['order_number']
        context['order_products'] = self.object.orderproduct_set.all()
        return context

class OrderUpdate(SuperuserRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'dashboard/order_update.html'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    success_url = reverse_lazy('dashboard:orders')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_number'] = self.kwargs['order_number']
        return context

class VariantList(SuperuserRequiredMixin, LoginRequiredMixin, ListView):
    model = ProductVariant
    context_object_name = 'variants'
    template_name = 'dashboard/variant_list.html'

class VariantCreate(SuperuserRequiredMixin, LoginRequiredMixin, CreateView):
    model = ProductVariant
    template_name = 'dashboard/variant_form.html'
    fields = '__all__'
    success_url = reverse_lazy('dashboard:variants')

class VariantUpdate(SuperuserRequiredMixin, LoginRequiredMixin, UpdateView):
    model = ProductVariant
    context_object_name = 'variant'
    template_name = 'dashboard/variant_update.html'
    fields = '__all__'
    success_url = reverse_lazy('dashboard:variants')

class VariantDelete(SuperuserRequiredMixin, LoginRequiredMixin, DeleteView):
    model = ProductVariant
    context_object_name = 'variant'
    template_name = 'dashboard/variant_delete.html'
    success_url = reverse_lazy('dashboard:variants')

class ProductList(SuperuserRequiredMixin, LoginRequiredMixin, ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'dashboard/products.html'

class ProductCreate(SuperuserRequiredMixin, LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'dashboard/product_form.html'
    fields = '__all__'
    success_url = reverse_lazy('dashboard:products')

class ProductUpdate(SuperuserRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Product
    context_object_name = 'product'
    template_name = 'dashboard/product_update.html'
    fields = '__all__'
    success_url = reverse_lazy('dashboard:products')

class ProductDelete(SuperuserRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Product
    context_object_name = 'product'
    template_name = 'dashboard/product_delete.html'
    success_url = reverse_lazy('dashboard:products')

class CategoryList(SuperuserRequiredMixin, LoginRequiredMixin, ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'dashboard/category_list.html'

class CategoryCreate(SuperuserRequiredMixin, LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'dashboard/category_form.html'
    fields = '__all__'
    success_url = reverse_lazy('dashboard:categories')

class CategoryUpdate(SuperuserRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Category
    context_object_name = 'category'
    template_name = 'dashboard/category_update.html'
    fields = '__all__'
    success_url = reverse_lazy('dashboard:categories')

class CategoryDelete(SuperuserRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Category
    context_object_name = 'category'
    template_name = 'dashboard/category_delete.html'
    success_url = reverse_lazy('dashboard:categories')

class SizeList(SuperuserRequiredMixin, LoginRequiredMixin, ListView):
    model = Size
    context_object_name = 'sizes'
    template_name = 'dashboard/size_list.html'

class SizeCreate(SuperuserRequiredMixin, LoginRequiredMixin, CreateView):
    model = Size
    template_name = 'dashboard/size_form.html'
    fields = '__all__'
    success_url = reverse_lazy('dashboard:categories')

class SizeUpdate(SuperuserRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Size
    context_object_name = 'size'
    template_name = 'dashboard/size_update.html'
    fields = '__all__'
    success_url = reverse_lazy('dashboard:categories')

class SizeDelete(SuperuserRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Size
    context_object_name = 'size'
    template_name = 'dashboard/size_delete.html'
    success_url = reverse_lazy('dashboard:categories')

class CustomerList(SuperuserRequiredMixin, LoginRequiredMixin, ListView):
    model = Customer
    context_object_name = 'customers'
    template_name = 'dashboard/customers.html'
    ordering = ['id']

class ToggleUserStatusView(SuperuserRequiredMixin, LoginRequiredMixin, View):
    def get(self, request, user_id):
        try:
            user = get_object_or_404(Customer, id=user_id)
            user.is_active = not user.is_active
            user.save()
        except Exception:
            return redirect('dashboard:dash')
        return redirect('dashboard:customer')
