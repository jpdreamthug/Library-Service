import stripe
from django.conf import settings
from decimal import Decimal

from django.http import HttpRequest

from borrowing.models import Borrowing
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_payment_session(
    borrowing: Borrowing, request: HttpRequest
) -> Payment:
    total_price = borrowing.book.daily_fee * Decimal(borrowing.days)

    success_url = request.build_absolute_uri("/api/payments/success")
    cancel_url = request.build_absolute_uri("/api/payments/cancel")

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
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
    )

    payment = Payment.objects.create(
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_price,
    )

    return payment


def create_stripe_fine_session(borrowing: Borrowing, request: HttpRequest) -> Payment:
    success_url = request.build_absolute_uri("/api/payments/success")
    cancel_url = request.build_absolute_uri("/api/payments/cancel")
    fine_amount = borrowing.get_fine_amount()

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Fine for borrowing book - {borrowing.book.title}",
                    },
                    "unit_amount": fine_amount,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
    )

    payment = Payment.objects.create(
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=fine_amount,
        type=Payment.Type.FINE,
    )

    return payment
