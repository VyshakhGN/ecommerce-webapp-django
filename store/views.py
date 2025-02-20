from django.shortcuts import render,get_object_or_404,redirect
from .models import Product, ReviewRating,ContactMessage, ProductGallery
from category.models import Category
from carts.views import _cart_id
from carts.models import CartItem
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q
from .forms import ReviewForm
from orders.models import OrderProduct

# display all the product
def store(request, category_slug=None):
    categories = None
    size_filter = request.GET.getlist('size')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    # sends the message to seller
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

       
        ContactMessage.objects.create(name=name, email=email, message=message)
        return render(request, 'home.html')
    # different product category
    else:
        if category_slug is not None:
            categories = get_object_or_404(Category, slug=category_slug)
            products = Product.objects.filter(category=categories, is_available=True)
        else:
            products = Product.objects.all().filter(is_available=True).order_by('id')
        # filter based on size
        if size_filter:
            products = products.filter(sizes__in=size_filter)
        if size_filter:
            products = products.filter(sizes__in=size_filter)
        #filter based on price
        if min_price and max_price:
            products = products.filter(price__range=(min_price, max_price))
        # pagination 
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

        context = {
            'products': paged_products,
            'product_count': product_count,
        }
        return render(request, 'store/store.html', context)


        
        
        
    
# Product detail page
def product_detail(request,category_slug,product_slug):
    try:
        single_product =Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user.id, product_id= single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None 
    else:
        orderproduct = None           

    

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery
    }
    return render(request,'store/product_detail.html',context)

    #Search the product based on name, description
def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-is_premium', '-created_date').filter( # search with premium product appears first
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }

    return render(request,'store/store.html', context) 

#review submission based on login and product bought
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)





