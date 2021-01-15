from django.contrib import admin
from mainapp.models import *


admin.site.register(GlobalCategory)
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartProduct)

admin.site.register(Order)
admin.site.register(Product)
