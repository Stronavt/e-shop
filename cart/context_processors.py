from .models import Product

def new_items(request):

    new_items_qs = Product.objects.filter(secondary_categories__name='new collection').order_by('-created')[:3]
    return {'new_items': new_items_qs}


