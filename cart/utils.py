from .models import Order


def get_or_set_order_session(request):
    order_id = request.session.get('order_id', None)
    print('ORDER_ID: ', order_id)

    if order_id is not None:
        try: 
            order = Order.objects.get(id=order_id, ordered=False)
        except Order.DoesNotExist:
            order = Order.objects.create()
            request.session['order_id'] = order.id


    else:
        order = Order.objects.create()
        request.session['order_id'] = order.id

    if request.user.is_authenticated and order.user is None:
        order.user = request.user
        order.save(update_fields=['user', ])

    return order

