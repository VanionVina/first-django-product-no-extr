from django.contrib.admin.utils import NestedObjects
from django.forms import model_to_dict
from mainapp.models import Category, GlobalCategory


def get_objects_for_category(category_slug):
    category = Category.objects.get(slug=category_slug)
    collector = NestedObjects(using='default')
    collector.collect([category])
    products = []
    for line in collector.data.values():
        products += line
    products = products[1:]
    return products


def get_product(category_slug, product_slug):
    category = Category.objects.get(slug=category_slug)
    products = get_objects_for_category(category.slug)
    for product in products:
        if product.slug == product_slug:
            return product


def get_all_products():
    models_amount = Category.objects.count()
    all_categorys = Category.objects.all()
    collector = NestedObjects(using='default')
    collector.collect(all_categorys)
    products = []
    for line in collector.data.values():
        products += line
    products = products[models_amount:]
    return products


def get_categorys_for_global_category(g_category_slug):
    g_category = GlobalCategory.objects.get(slug=g_category_slug)
    collector = NestedObjects(using='default')
    collector.collect([g_category])
    for index, line in enumerate(collector.data.values()):
        if index == 1:
            return line


def get_product_specif(category_slug, product_slug):
    product = get_product(category_slug, product_slug)
    fields = model_to_dict(product)
    banlist = ["id", "name", "slug", "category",
            "image", "price", "description"]
    final = {}
    for key, value in fields.items():
        if key  not in banlist and value != None:
            ver_name = product._meta.get_field(key).verbose_name
            final[ver_name] = value
    return final

