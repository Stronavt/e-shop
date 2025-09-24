E-Shop - полнофункциональный e-commerce проект на Django, разделенный на отдельный приложения для модульности. Основной фокус сделан на корзине(cart) с безлпасными сессиями, использующими order_hash, магазине(shop) с отзывами, административном управлении (staff). Проект поддерживает гостей и аутентифицированных пользователей. 

Основные фукнции.
CART:
- безопасное хранение заказов сессии с 'get_or_set_session' (signed id для предотвращения подделки)
- использование templatetag 'cart_items_count' для отображения кол-ва товаров в шаблонах
- context processor 'new_items' для показа новых товаров
- увеличение/уменьшение товаров в корзине с перезагрузкой страницы(в перспективе заменой на AJAX/JS для динамики)
- поддержка промокодов/скидок
- настройка адресов доставки для залогиненных пользователей

STAFF:
- StaffMixins для администрирования
- просмотр заказов(детальность и статусы)
- CRUD операции для Product и PromoCode

SHOP:
- форма обратной связи - отправка сообщений от клиента
- просмотр страницы профиля с заказами

Техническая часть:
- Backend: Python 3.9+, Django 4.0+
- Database: SQLite
- Оплата: Stripe payment
- Frontend: Django templates with Bootstrap, CSS

Установка и запуск 
Предварительные требования: 
- Python 3.8+
- Git
- pip3, virtualenv
- Stripe account

Шаги установки : 
1. git clone https://github.com/Stronavt/e-shop.git
2. cd e-shop
3. python3 -m venv venv
4. source venv/bin/activate
5. pip3 install -r requirements.txt
6. добавьте STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY, STRIPE_API_VERSION
