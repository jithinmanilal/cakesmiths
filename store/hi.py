
def customer_login(request):  
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
			messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
			try:
				query = requests.utils.urlparse(url).query
				params = dict(x.split('=')for x in query.split('&'))
				if 'next' in params:
					next_page = params['next']
					return redirect(next_page)
			except:
				return redirect('store:home')
		else:
			messages.error(request, 'Invalid login Credentials')
			return redirect('store:login')
	return render(request, 'store/login.html')