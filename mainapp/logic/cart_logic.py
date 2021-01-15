from django.db import models


def cart_recalc(cart):
    final_price = cart.products.aggregate(models.Sum('total_price')).get('total_price__sum')
    cart_amount = cart.products.count()
    if not final_price:
        final_price = 0
    if not cart_amount:
        cart_amount = 0
    cart.final_price = final_price
    cart.final_amount = cart_amount
    cart.save()
