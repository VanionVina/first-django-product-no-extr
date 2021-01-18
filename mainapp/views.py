from decimal import Decimal

from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages

from .forms import LoginForm, Registration, OrderForm
from .mixins import GetCategorysMixin, GetCurtMixin
from .models import Category, GlobalCategory, Customer, CartProduct, Order, Product
from .logic import get_products, cart_logic


class Index(GetCurtMixin, GetCategorysMixin, View):

    def get(self, request):
        products = Product.objects.all()
        context = {
            'products': products,
            'g_categorys': self.g_categorys,
            'cart': self.cart,
        }
        return render(request, 'index.html', context)


class ProductDetail(GetCurtMixin, GetCategorysMixin, View):

    def get(self, request, product_slug):
        product = Product.objects.get(slug=product_slug)
        context = {
            'product': product,
            'g_categorys': self.g_categorys,
            'cart': self.cart,
        }
        return render(request, 'product_detail.html', context)


class GlobalCategoryDetail(GetCurtMixin, GetCategorysMixin, View):

    def get(self, request, global_category_slug):
        very_g_category = GlobalCategory.objects.get(slug=global_category_slug)
        categorys = get_products.get_categorys_for_global_category(very_g_category.slug)
        products = []
        for category in categorys:
            products_for_category = Product.objects.filter(category=category)
            products += products_for_category
        context = {
                'products': products,
                'g_categorys': self.g_categorys,
                'cart': self.cart,
                'vg_category': very_g_category,
        }
        return render(request, 'global_category_detail.html', context)


class CategoryDetail(GetCurtMixin, GetCategorysMixin, View):

    def get(self, request, category_slug):
        category = Category.objects.get(slug=category_slug)
        products = Product.objects.filter(category=category)
        context = {
            'self_category': category,
            'products': products,
            'g_categorys': self.g_categorys,
            'cart': self.cart,
        }
        return render(request, 'category_detail.html', context)


class LoginView(View):

    def get(self, request):
        form = LoginForm
        context = {
            'form': form,
        }
        return render(request, 'registration/login.html', context)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
        return render(request, 'registration/login.html', context={'form': form})


class RegistrationView(View):

    def get(self, request):
        form = Registration
        context = {
                'form': form,
        }
        return render(request, 'registration//registration.html', context)

    def post(self, request):
        form = Registration(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']
            user = User.objects.create(username=username)
            user.set_password(password)
            user.customer.phone = phone
            user.customer.address = address
            user.save()
            messages.add_message(request, messages.INFO, 'Succefully register, now log in')
            return HttpResponseRedirect(reverse('login'))
        return render(request, 'registration/registration.html', context={'form': form})


class AddToCart(GetCurtMixin, View):

    def get(self, request, product_slug):
        if not request.user.is_authenticated:
            messages.add_message(request, messages.INFO, 'Log in to do this')
            return HttpResponseRedirect(reverse('login'))
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
        product = Product.objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=customer, to_cart=self.cart, product=product,
            )
        if created:
            cart_product.total_price = product.price
            self.cart.products.add(cart_product)
            cart_product.save()
        cart_logic.cart_recalc(self.cart)
        return HttpResponseRedirect(reverse('cart_detail'))


class CartView(GetCurtMixin, View):

    def get(self, request):
        context = {
            'cart': self.cart,
        }
        return render(request, 'cart_detail.html', context)


class DeleteCartProduct(GetCurtMixin, View):

    def get(self, request, cart_product_id):
        product = CartProduct.objects.get(id=cart_product_id)
        self.cart.products.remove(product)
        product.delete()
        cart_logic.cart_recalc(self.cart)
        return HttpResponseRedirect(reverse('cart_detail'))


class ChangeCartProductAmount(GetCurtMixin, View):

    def post(self, request, cart_product_id):
        product = CartProduct.objects.get(id=cart_product_id)
        amount = request.POST.get('amount')
        product.amount = amount
        product.total_price = Decimal(product.product.price) * Decimal(amount)
        product.amount = amount
        product.save()
        cart_logic.cart_recalc(self.cart)
        return HttpResponseRedirect(reverse('cart_detail'))


class UserProfile(GetCurtMixin, View):

    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(user=customer)
        context = {
                'cart': self.cart,
                'orders': orders,
                }
        return render(request, 'user_profile.html', context)


class OrderView(GetCurtMixin, View):

    def get(self, request):
        if self.cart.final_amount == 0:
            return HttpResponseRedirect(reverse('cart_detail'))
        form = OrderForm
        context = {
            'cart': self.cart,
            'form': form,
        }
        return render(request, 'create_order.html', context)
    
    def post(self, request):
        form = OrderForm(request.POST)
        if form.is_valid():
            customer = Customer.objects.get(user=request.user)
            cart = self.cart
            first_name = request.POST.get('first_name')
            address = request.POST.get('address')
            phone = request.POST.get('phone')
            order = Order.objects.create(
                user=customer, cart=cart, first_name=first_name,
                address=address, phone=phone,
                )
            order.save()
            self.cart.ordered = True
            self.cart.save()
            return HttpResponseRedirect(reverse('user_profile'))

class CartOrderedView(GetCurtMixin, View):

    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)
        context = {
            'cart': self.cart,
            'order': order,
        }
        return render(request, 'order_view.html', context)


class CreateNewView(GetCurtMixin, View):

    def get(self, request):
        context = {
            "cart": self.cart,
        }
        return render(request, "create_new.html", context)
