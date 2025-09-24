import logging
from .models import Order
from datetime import timedelta
from django.utils import timezone
from django.core.signing import Signer

logger = logging.getLogger(__name__) 

def get_or_set_order_session(request):
    signed_id = request.session.get('order_signed_id', None)
    order = None
    signer = Signer()

    if signed_id is not None: 
        try:
            order_id = signer.unsign(signed_id)
            order_id = int(order_id)

            order = Order.objects.get(id=order_id, ordered=False)

        except (Signer.BadSignature, ValueError, Order.DoesNotExist):
            if logger:
                logger.warning(f"Invalid signed_id '{signed_id[:10]}', creating new order")
            order = Order.objects.create()

    if order is None:
        order = Order.objects.create()

    new_signed_id = signer.sign(str(order.id))
    request.session['order_signed_id'] = new_signed_id


    if request.user.is_authenticated and order.user is None:
        order.user = request.user
        order.save(update_fields=['user'])

    if (not request.user.is_authenticated and order.user is None and
        order.start_date < timezone.now() - timedelta(hours=24)):

        if logger:
            logger.info(f"Expiring old guest order {order.id} (age: {timezone.now() - order.start_date})")

            order.ordered = True
            order.save(update_fields=['ordered'])

            new_order = Order.objects.create()
            new_signed_id = signer.sign(str(new_order.id))   
            request.session['order_signed_id'] = new_signed_id
            order = new_order

            if logger:
                logger.info(f"Created new order {new_order.id} for guest")

    return order






