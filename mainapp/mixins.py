from django.views.generic import View

from mainapp.models import GlobalCategory, Customer, Cart


class GetCategorysMixin(View):

    def dispatch(self, request, *args, **kwargs):
        self.g_categorys = GlobalCategory.objects.all()
        return super().dispatch(request, *args, **kwargs)

class GetCurtMixin(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=request.user)
            cart = Cart.objects.filter(owner=customer, ordered=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
            self.cart = cart
        else:
            self.cart = None

        return super().dispatch(request, *args, **kwargs)
