import stripe
from django.conf import settings
from decimal import Decimal
from .models import Payment

# Устанавливаем секретный ключ Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """
    Сервис для работы с Stripe API
    """

    @staticmethod
    def create_product(name, description):
        """
        Создание продукта в Stripe
        https://stripe.com/docs/api/products/create
        """
        try:
            product = stripe.Product.create(
                name=name,
                description=description,
                active=True,
            )
            return product
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка создания продукта: {str(e)}")

    @staticmethod
    def create_price(product_id, amount, currency='rub'):
        """
        Создание цены для продукта в Stripe
        https://stripe.com/docs/api/prices/create
        """
        try:
            # Stripe принимает сумму в копейках/центах
            amount_in_cents = int(amount * 100)

            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount_in_cents,
                currency=currency,
                product_data={
                    'name': f'Payment for product',
                }
            )
            return price
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка создания цены: {str(e)}")

    @staticmethod
    def create_checkout_session(price_id, success_url, cancel_url, client_reference_id=None):
        """
        Создание сессии для оплаты
        https://stripe.com/docs/api/checkout/sessions/create
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=client_reference_id,
                metadata={
                    'payment_id': client_reference_id,
                }
            )
            return session
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка создания сессии: {str(e)}")

    @staticmethod
    def create_payment_for_course(user, course):
        """
        Создание платежа для курса через Stripe
        """
        try:
            # Создаем продукт в Stripe
            product = StripeService.create_product(
                name=course.name,
                description=f"Оплата курса: {course.name}"
            )

            # Создаем цену
            price = StripeService.create_price(
                product_id=product.id,
                amount=float(course.price) if hasattr(course, 'price') else 1000.00
            )

            # Создаем платеж в БД
            payment = Payment.objects.create(
                user=user,
                course=course,
                amount=Decimal(price.unit_amount) / 100,
                payment_method='stripe',
                payment_status='pending',
                stripe_product_id=product.id,
                stripe_price_id=price.id,
            )

            # Создаем сессию оплаты
            session = StripeService.create_checkout_session(
                price_id=price.id,
                success_url='http://localhost:8000/api/payments/success/',
                cancel_url='http://localhost:8000/api/payments/cancel/',
                client_reference_id=str(payment.id)
            )

            # Обновляем платеж с ID сессии и ссылкой
            payment.stripe_checkout_session_id = session.id
            payment.checkout_url = session.url
            payment.save()

            return payment

        except Exception as e:
            raise Exception(f"Ошибка создания платежа: {str(e)}")

    @staticmethod
    def confirm_payment(session_id):
        """
        Подтверждение платежа после успешной оплаты
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == 'paid':
                payment_id = session.client_reference_id
                if payment_id:
                    payment = Payment.objects.get(id=payment_id)
                    payment.payment_status = 'paid'
                    payment.stripe_payment_intent_id = session.payment_intent
                    payment.save()
                    return payment
            return None
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка подтверждения платежа: {str(e)}")