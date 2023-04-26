from django.shortcuts import render, reverse, redirect
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.contrib import messages

from . models import Wishlist, Coupon
from store.models import ProductVariant, Cart, CartItem
from store.views import _cart_id
from .forms import CouponForm

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
# Create your views here.

class WishListView(View):
    def get(self, *args, **kwargs):
        try:
            if self.request.user.is_authenticated:
                wish_items = Wishlist.objects.filter(customer=self.request.user)
                context = {
                    'wish_items': wish_items,
                }
                return render(self.request, 'coupon/wishlist.html', context)
            else:
                messages.error(self.request, "Please log in to view your wishlist.")
                return redirect('store:login')
        except:
            pass

def add_to_wishlist(request, product_slug, size_slug):
    variant = ProductVariant.objects.get(product__slug=product_slug, size__slug=size_slug)
    try:
        wishlist_item_exists = Wishlist.objects.filter(customer=request.user, variant=variant).exists()
        if wishlist_item_exists:
            messages.error(request, "Item already exists in your wishlist.")
        else:
            Wishlist.objects.create(customer=request.user, variant=variant)
            messages.success(request, "Item added to your wishlist.")
    except:
            pass
    finally:
        return HttpResponseRedirect(reverse('coupon:wishlist'))

def remove_from_wishlist(request, item_id):
    try:
        Wishlist.objects.get(id=item_id).delete()
        messages.success(request, "Item removed from your wishlist.")
        return HttpResponseRedirect(reverse('coupon:wishlist'))
    except:
        pass


def add_to_cart(request, variant_id):
    current_user = request.user
    wish_item = Wishlist.objects.get(customer=current_user, variant__id=variant_id)
    if current_user.is_authenticated:
        variant = ProductVariant.objects.get(id=variant_id)
        try:
            cart_item = CartItem.objects.get(variant=variant, user=current_user)
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, "Item added to cart.")
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=variant.product,
                variant=variant,
                user=current_user,
                quantity=1,
            )
            cart_item.save()
            messages.success(request, "Item added to cart.")
        wish_item.delete()
        return redirect('store:cart')
    else:
        variant = ProductVariant.objects.get(id=variant_id)
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
            cart.save()
        try:
            cart_item = CartItem.objects.get(variant=variant, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, "Item added to cart.")
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=variant.product,
                variant=variant,
                cart=cart,
                quantity=1,
            )
            cart_item.save()
            messages.success(request, "Item added to cart.")
        wish_item.delete()
        return redirect('store:cart')    

@require_POST
def apply_coupon(request):
    now = timezone.now()
    form = CouponForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code, valid_from__lte=now, valid_till__gte=now, active=True)
            request.session['coupon_id'] = coupon.id
            messages.success(request, "Coupon applied successfully.")
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
            messages.error(request, "Coupon not applicable, try again.")
    return redirect('store:cart')

def remove_coupon(request):
    try:
        coupon = request.session['coupon_id']
        if coupon:
            request.session['coupon_id'] = None
            messages.success(request, "Coupon removed successfully.")
    except:
        messages.error(request, "No coupons applied.")
    return redirect('store:cart')

