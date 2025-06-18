from django import template
from cart.utils import get_or_set_order_session

register = template.Library()


@register.filter
def cart_items_count(request):
    order = get_or_set_order_session(request)
    count = order.items.count()
    
    # Проверка состояния сессии
    current_order_id = request.session.get('order_id', None)
    print(f'Current order_id in session: {current_order_id}')
    return count