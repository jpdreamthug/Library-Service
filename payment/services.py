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
    total_price = borrowing.get_payment_amount()

    success_url = request.build_absolute_uri(settings.PAYMENT_SUCCESS_URL)
    cancel_url = request.build_absolute_uri(settings.PAYMENT_CANCEL_URL)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": total_price,
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
    fine_amount = borrowing.get_fine_amount()

    success_url = request.build_absolute_uri(settings.PAYMENT_SUCCESS_URL)
    cancel_url = request.build_absolute_uri(settings.PAYMENT_CANCEL_URL)

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
