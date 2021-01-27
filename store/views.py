from django.shortcuts import render,redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, FormView, View, TemplateView
from .forms import *
from .models import *
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required



# Create your views here.
class home(TemplateView):
    model = Product
    template_name = "index.html"
    def get_context_data(self, **kwargs):
        context = super(home, self).get_context_data(**kwargs)
        context['products'] = Product.objects.order_by('-stock').filter()[:8]
        context['products1'] = Product.objects.order_by('-stock').filter()[9:17]
        context['products2'] = Product.objects.order_by('-stock').filter()[17:25]
        return context
    #return render(request,"index.html")

class shopbybrand(ListView):
    model = Product
    template_name = "category.html"
    def get_context_data(self, **kwargs):
        context = super(shopbybrand, self).get_context_data(**kwargs)
        brand_id = self.request.GET.get('category')
        total = Product.objects.values('brand').annotate(Count('brand'))

        context['total'] = total
        if brand_id:
            products = Product.get_product_by_category_id(brand_id)
            context['brands'] = products
            return context  
        else :
            lst = Product.objects.values_list('brand', flat=True).order_by('brand').distinct()[:1]
            brand = Product.objects.filter(brand=lst)
            context['brands'] = brand
            return context
        return context

def add_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    oi, created = OrderItem.objects.get_or_create(
        item=item,
        customer=request.user,
        ordered=False
    )
    oqs = Order.objects.filter(user=request.user, ordered=False)
    if oqs.exists():
        order = oqs[0]
        print(order)
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            oi.quantity += 1
            oi.save()
            return redirect("cart")
        else:
            order.items.add(oi)
            return redirect("cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(oi)
        return redirect("cart")

def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        try:
            order = Order.objects.get(user=customer,ordered=False)
            items = order.items.all()
        except:
            return redirect("/category/")
    else:
        items = []
        return redirect("/category/")

    context = {'items':items, 'order':order}
    return render(request,'cart.html',context)

@login_required(login_url="/login/")
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order = Order.objects.get(user=customer,ordered=False)
        items = order.items.all()
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
    context = {'items':items, 'order':order}
    return render(request,'checkout.html',context)

def confirmation(request):
    return render(request,"confirmation.html")

def contact(request):
    return render(request,"contact.html")

def login_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect('/home')
    if request.method == 'POST':
        form = Userlogin(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username,password=password)
            if user:
                login(request,user)
                return HttpResponseRedirect('/home')
    else:
        form = Userlogin()
    context['login_form'] = form
    return render(request,"login.html",context)

def register(request):
    context ={}
    if request.method == "POST":
        form = Register(request.POST)
        profile_form = CustomerForm(request.POST)
        add_form = AddressForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            add = add_form.save(commit=False)
            add.user = user
            add.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(username=username,password=raw_password)
            login(request,account)
            return HttpResponseRedirect('/home')
        else:
            context['registration_form'] = form
    else:
        form = Register()
        profile_form = CustomerForm()
        add_form = AddressForm()
    context = {'registration_form':form}
    return render(request,'register.html',context)

def logout_view(request):
    logout(request)
    return redirect('login_view')

class Profile(TemplateView):
    model = Customer, ShippingAddress
    template_name = 'profile.html'
    def get_user(self):
        user = self.request.user
        user1 = str(user)
        print("hey" + user1)
        return user
    def get_context_data(self, **kwargs):
        context = super(Profile, self).get_context_data(**kwargs)
        queryset = self.get_user()
        print(queryset)
        user1 = User.objects.filter(username=queryset)
        user2 = Customer.objects.filter(user=queryset)     
        user3 = ShippingAddress.objects.filter(user=queryset)   
        context = {'usermodel':user1, 'customermodel':user2, 'addmodel' :user3}
        return context

class Editprofile(FormView):
    # model = Customer 
    template_name = 'editprofile.html'
    form_class = EditBasicProfile
    success_url = "/profile/"

    def form_valid(self, form):
        a = EditBasicProfile(self.request.POST,instance=self.request.user)
        #b = CustomerForm(self.request.POST,instance=self.request.user)
        a.save()
        #b.save()
        return HttpResponseRedirect("/profile/")
    
    # def get_context_data(self, **kwargs):
    #     context = super(Editprofile, self).get_context_data(**kwargs)
    #     context['a'] = editbasicprofile
    #     return context

class ProductDetailView(TemplateView):
    model = Product
    template_name = "single-product.html"

    def get_queryset(self):
        slug_1 = self.kwargs['slug']
        return slug_1
        
    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        queryset = self.get_queryset()
        print(queryset)
        product = Product.objects.filter(slug=queryset)
        #return context

        stk = Product.objects.get(slug=queryset).stock
        if stk>0:
            get_brand = Product.objects.get(slug=queryset).category
            similar1 = Product.objects.filter(category=get_brand)
            similar = similar1.order_by('?')[:9]
            context = {'products':product,'stock':stk,'similar':similar}
        else:
            get_brand = Product.objects.get(slug=queryset).category
            similar1 = Product.objects.filter(category=get_brand)
            similar = similar1.order_by('?')[:9]
            msg = "Out Of Stock"
            context = {'product':product,'oos':msg,'similar':similar}
        return context

class SearchView(ListView):
    model = Product
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        srch = self.request.GET.get('q')
        if srch:
            try:
                context['search'] = Product.objects.filter(Q(category__icontains=srch)|
                                                    Q(name__icontains=srch)|
                                                    Q(brand__icontains=srch))
                return context
            except:
                context['error'] = "No results found  :("
        else:
            context['error'] = "No results found"

def remove_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                customer=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("cart")
        else:
            context = {}
            messages.info(request, "This item was not in your cart")
            return redirect("product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        
def remove_single_item_from_cart(request, slug):
    
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                customer=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            
            return redirect("cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("cart", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("cart", slug=slug)

def order_confirmation(request):
    context = {}
    customer = request.user
    order = Order.objects.get(user=customer,ordered=False)
    item_list = order.items.all().order_by('item_id')
    item_id = item_list.values('item_id')
    quantity = item_list.values('quantity')
    items = Product.objects.filter(id__in=item_id).order_by('id')
    stock = items.values('stock')
    address = ShippingAddress.objects.get(user=customer)
    print(stock)

   
    stock1 = []
    for k in stock:
        for k,v in k.items():
            stock1.append(v)
    quantity1 = []
    for a in quantity:
        for k,v in a.items():
            quantity1.append(v)

    confirmation = [stock1_i - quantity1_i for stock1_i, quantity1_i in zip(stock1, quantity1)]
    x = 0
    var = 0
    flag = 0
    oos_item_lst = []
    email = request.user.email
    for i in confirmation:
        if i<0:
            context["failed"] = "Items below are out of stock. Please reduce quantity or remove product from the cart to complete the order"
            id1 = item_id[var].values()
            oositem = Product.objects.filter(id__in=id1)
            oos_item_lst.append(oositem)
            flag=1
        var=var+1
    if flag==1:
        context['oositem'] = oos_item_lst
        # send_email_fail_task.delay(email)
        return render(request,"confirmation.html",context)
       

    for s in items:
        s.stock = confirmation[x]
        x = x+1
        s.save()
    order.ordered=True
    order.save()
    # send_email_task.delay(email)
    context = {'msg':"Your order is placed successfully.",
                'items':item_list,
                'order':order,
                'address':address,
    }
    return render(request,"confirmation.html",context)