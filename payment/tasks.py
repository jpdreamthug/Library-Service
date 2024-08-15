import stripe
from celery import shared_task
from django.conf import settings

from payment.models import Payment


@shared_task
def check_payment_expiration() -> None:
    payments = Payment.objects.all()
    for payment in payments:
        session = stripe.checkout.Session.retrieve(
            payment.session_id
        )
        if session.status == "expired":
            print(f"Found expired session: {session.id}")
            payment.status = Payment.Status.EXPIRED
