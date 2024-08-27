import re

import stripe
from django.conf import settings
from django.http import HttpRequest

from borrowing.models import Borrowing
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def sanitize_product_name(name: str) -> str:
    sanitized_name = re.sub(r"[^a-zA-Z0-9\s]", "", name)
    return sanitized_name[:127]


def create_payment_session(
    borrowing: Borrowing,
    request: HttpRequest,
    payment_type: Payment.Type,
    save=True,
) -> Payment:

    if payment_type == Payment.Type.PAYMENT:
        total_price = borrowing.get_payment_amount()
        product_name = borrowing.book.title
    else:
        total_price = borrowing.get_fine_amount()
        product_name = f"Fine for {borrowing.book.title}"

    product_name = sanitize_product_name(product_name)

    success_url = request.build_absolute_uri(settings.PAYMENT_SUCCESS_URL)
    cancel_url = request.build_absolute_uri(settings.PAYMENT_CANCEL_URL)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": product_name,
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

    payment = Payment(
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_price,
        type=payment_type,
    )
    if save:
        payment.save()

    return payment
