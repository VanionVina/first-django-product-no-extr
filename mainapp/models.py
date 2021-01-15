from django.contrib.auth.models import User
from django.contrib.admin.utils import NestedObjects
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.urls import reverse

from .logic.save_image import save_save

# Category
# Product
# Customer
# Cart
# CartProduct


class GlobalCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Global category name')
    slug = models.SlugField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(GlobalCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_relevant_categorys(self):
        collector = NestedObjects(using='default')
        collector.collect([self])
        for index, line in enumerate(collector.data.values()):
            if index == 1:
                return line

    def get_absolute_url(self):
        return reverse('global_category_detail', kwargs={'global_category_slug': self.slug})


class Category(models.Model):
    global_category = models.ForeignKey(GlobalCategory, on_delete=models.CASCADE,
                                        verbose_name='To global category')
    name = models.CharField(max_length=100, verbose_name='Category name')
    slug = models.SlugField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.global_category} : {self.name}'

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'category_slug': self.slug})


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Product name')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Product category', default=None)
    slug = models.SlugField(unique=True, editable=False)
    description = models.TextField(verbose_name='Product description')
    price = models.DecimalField(verbose_name='Product price', max_digits=10, decimal_places=2)
    image = models.ImageField(verbose_name='Image')
    stars = models.DecimalField(max_digits=2, decimal_places=1, verbose_name='Rating',
                                blank=True, null=True)

    def get_absolute_url(self):
        context = {
            'product_slug': self.slug
        }
        return reverse('product_detail', kwargs=context)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.image = save_save(self.image)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.slug


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.IntegerField(verbose_name='Phone number', null=True)
    address = models.CharField(max_length=255, verbose_name='Address', null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_customer(sender, instance, **kwargs):
    instance.customer.save()


class Cart(models.Model):
    final_price = models.DecimalField(null=True, blank=True, max_digits=100, decimal_places=2,
                                      verbose_name='Final price')
    final_amount = models.IntegerField(null=True, blank=True,
                                       verbose_name='Total amount')
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Owner')
    products = models.ManyToManyField('CartProduct', blank=True)
    ordered = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.final_amount:
            self.final_amount = 0
        if not self.final_price:
            self.final_price = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Cart: {self.id} | Owner: {self.owner}'


class CartProduct(models.Model):
    user = models.ForeignKey(Customer, verbose_name='Customer', on_delete=models.CASCADE)
    to_cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Amount', default=1)
    total_price = models.DecimalField(verbose_name='Total price', null=True, blank=True,
                                      max_digits=100, decimal_places=2)

    def __str__(self):
        return f'Cart product: {self.product_slug} | For cart: {self.to_cart.id}'


class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'MNew'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered')
    )
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    phone = models.IntegerField()
    created = models.DateTimeField(auto_created=True, auto_now=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f'Order to cart: {self.cart.id}'
