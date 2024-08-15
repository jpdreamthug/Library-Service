import stripe
from django.conf import settings
from decimal import Decimal

from django.http import HttpRequest

from borrowing.models import Borrowing
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing: Borrowing, request: HttpRequest) -> Payment:
    total_price = borrowing.book.daily_fee * Decimal(borrowing.days)
    request.build_absolute_uri()
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": int(total_price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
    )

    payment = Payment.objects.create(
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_price
    )
    return payment
